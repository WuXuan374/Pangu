import logging
import random

from typing import Dict, List, Tuple, Union, Set
from collections import defaultdict

from utils.logic_form_util import (
    postprocess_raw_code,
    lisp_to_sparql
)
from utils.kb_environment import Computer, Program
from utils.sentence_bert_utils import SentenceSimilarityPredictor
from utils.sparql_executer_odbc import execute_query as execute_query_odbc
from utils.sparql_executer import execute_query
import torch
from func_timeout import FunctionTimedOut

logger = logging.getLogger(__name__)
random.seed(374)

class Enumerator(object):
    def __init__(
            self,
            infer=True,
            beam_size=5,
            decoding_steps=4,  # 5 for grail; 4 for graph
            dataset='grail'
     ) -> None:
        self._infer = infer # TODO: 只应该为 True
        self._beam_size = beam_size
        self._decoding_steps = decoding_steps
        if self._infer:
            self._computer = Computer(dataset=dataset)
        else:
            self._computer = None # TODO: 不应该执行
        
        self._dataset = dataset
        self.sentence_bert_ranker = SentenceSimilarityPredictor.instance()
        # 如果超时了，可以通过访问这个成员变量，然后对 program 做排序
        self.all_beam_programs:List[Tuple[Program, float]] = []
    
    @classmethod
    def instance(cls, *args, **kwargs):
        '''单例模式'''
        if not hasattr(Enumerator, "_instance"):
            Enumerator._instance = Enumerator(*args, **kwargs)
        return Enumerator._instance
        
    
    '''单个样例'''
    def run(
        self,  # type: ignore
        question: str,
        # for entity: key->mid, value->friendly name; for value: key->value w type, value->value w/o type
        entity_name: Dict,
        qid=None,
        answer_types=None, # List[str]
        top_k=3 # 返回 top_k 个查询
    ):
        logger.info(f"question: {question}")
        if self._infer and str(qid) in ["test-13230", "2100263012000", "WebQTest-2031"]:
            # cache the results during prediction
            self._computer._cache.cache_results()
        
        if self._computer is not None:
            self._computer.set_training(training=False) # TODO: Not Training!
        
        programs:List[List[Program]] = [] # List of List, 每一个 step 对应一个 list 的 programs
        self.all_beam_programs = []
        '''{topic entity: [list of programs from this topic entity]}'''
        programs_indexed:Dict[str, List[Program]] = defaultdict(lambda: []) 
        highest_score = -1e32 # 上一轮的最高得分
        num_candidates = 0
        decoding_steps = self._decoding_steps

        for decoding_step in range(decoding_steps):
            if decoding_step == 0: # TODO: entity_name 需要控制，传的是 golden 还是 linked
                candidate_programs: List[Program] = self._computer.get_initial_programs(entity_name, answer_types, None)
            else:
                candidate_programs: List[Program] = self._computer.get_admissible_programs(
                    programs[decoding_step - 1],
                    programs_indexed,
                    entity_name
                )
                num_candidates += len(candidate_programs)
            
            if len(candidate_programs) == 0:  # normally due to all beam programs being finalized
                break
            else:
                new_beam_programs, scores = self._get_top_candidates(
                    candidate_programs, question
                )

                if len(scores) > 0 and scores[0] > highest_score:
                    highest_score = scores[0]
                elif decoding_step > 0:
                    break  
            
            beam_programs = new_beam_programs
        
            # TODO: 这里开始都是支持 batch 的写法，应该给成不支持 batch, 只有一个 item
            programs.append([bp for bp in beam_programs if not bp.dummy])
            self.all_beam_programs.extend([(bp, s) for (bp, s) in zip(beam_programs, scores) if not bp.dummy])
            for bp in beam_programs:
                if bp.dummy:
                    continue
                if isinstance(bp.source, set):
                    bp.source = tuple(bp.source)
                programs_indexed[bp.source].append(bp)

        try:
            '''小技巧，基于执行结果的 program 再选择'''
            beam_programs_sorted = sorted(
                self.all_beam_programs, key=lambda x:x[1], reverse=True
            ) # 从高到低排序

            top_k_predictions_idx = list()
            for (idx, (p, _)) in enumerate(beam_programs_sorted):  
                if p.finalized:
                    if p.execution is None:
                        top_k_predictions_idx.append(idx)
                    elif isinstance(p.execution, int) and p.execution != 0:
                        top_k_predictions_idx.append(idx)
                    elif not isinstance(p.execution, int) and len(p.execution) > 0:
                        if not p.is_cvt(self._computer):
                            top_k_predictions_idx.append(idx)
                if len(top_k_predictions_idx) >= top_k:
                    break
            # 可能仍然少于 topk, 那么剩余内容按照得分排序，填满 topk 位置(不再做 finalized 等检查了)
            for (idx, (p, _)) in enumerate(beam_programs_sorted): 
                if idx in top_k_predictions_idx:
                    continue
                if len(top_k_predictions_idx) >= top_k:
                    break
                top_k_predictions_idx.append(idx)
            top_k_predictions = [beam_programs_sorted[idx][0] for idx in top_k_predictions_idx]

            for p in top_k_predictions:
                if p.code_raw != '':
                    p.code_raw = postprocess_raw_code(p.code_raw)
        except UnboundLocalError:  
            print("question:", question)
        
        result = {
            "predictions": top_k_predictions,
            "qid": qid
        }

        return result
    
    def post_process_results(self, results):
        qid = results["qid"]
        top_k_programs = results["predictions"]
        predictions = list()
        for program in top_k_programs:
            if program is not None:
                predicted_lf = program.code_raw
                if predicted_lf != '':
                    try:
                        sparql_query = lisp_to_sparql(predicted_lf)
                        denotation = list(execute_query_odbc(sparql_query))
                        # denotation = list(execute_query(sparql_query))
                    except Exception as e:
                        logger.error(f"err: {e}")
                else:
                    denotation = ["1"]

            else:
                predicted_lf = ''
                denotation = ["1"]
            
            predictions.append({
                "logical_form": predicted_lf,
                "answer": denotation
            })
        
        return {
            "qid": qid,
            "predictions": predictions
        }


    def _get_top_candidates(
        self, 
        candidate_programs: List[Program],
        question: str,
    ):
        '''暂时先用 SentenceBert'''
        scores = self.sentence_bert_ranker.get_similarity(
            question, [p.code for p in candidate_programs]
        )
        # 为什么要 + 5? 还要过滤掉一些不可执行的 program
        top_scores, top_indices = torch.topk(scores, k=min([len(candidate_programs), self._beam_size + 5]))
        
        rtn_candidates = []
        rtn_scores = []
        for (score, idx) in zip(top_scores.tolist(), top_indices.tolist()):
            if len(rtn_candidates) == self._beam_size:
                break
            candi = candidate_programs[idx]
            candi.execute(self._computer)
            if isinstance(candi.source, str):
                # 执行结果为空，或者执行结果只有 topic entity
                if isinstance(candi.execution, set):
                    if len(candi.execution) == 0 or (
                            list(candi.execution)[0] == candi.source and len(candi.execution) == 1):
                        continue
                else:  # COUNT function
                    if candi.execution == 0:
                        continue
            rtn_candidates.append(candi)
            rtn_scores.append(score)
        return rtn_candidates, rtn_scores