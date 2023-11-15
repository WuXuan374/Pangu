import logging
import random

from typing import Dict, List, Tuple, Union, Set
from collections import defaultdict

from utils.logic_form_util import (
    postprocess_raw_code,
    lisp_to_sparql
)
from utils.kb_environment import Computer, Program
import torch

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
    
    '''单个样例'''
    def run(
        self,  # type: ignore
        question: str,
        # for entity: key->mid, value->friendly name; for value: key->value w type, value->value w/o type
        entity_name: Dict,
        qid=None,
        answer_types=None # List[str]
    ):
        logger.info(f"question: {question}")
        if self._infer and str(qid) in ["test-13230", "2100263012000", "WebQTest-2031"]:
            # cache the results during prediction
            self._computer._cache.cache_results()
        
        if self._computer is not None:
            self._computer.set_training(training=False) # TODO: Not Training!
        
        predictions = None
        programs:List[List[Program]] = [] # List of List, 每一个 step 对应一个 list 的 programs
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
            for bp in beam_programs:
                if bp.dummy:
                    continue
                if isinstance(bp.source, set):
                    bp.source = tuple(bp.source)
                programs_indexed[bp.source].append(bp)
        
        try:
            '''小技巧，基于执行结果的 program 再选择'''
            finalized = False
            for p in beam_programs:  
                selection = False
                if p.finalized:
                    if p.execution is None:
                        selection = True
                    elif isinstance(p.execution, int) and p.execution != 0:
                        selection = True
                    elif not isinstance(p.execution, int) and len(p.execution) > 0:
                        if not p.is_cvt(self._computer):
                            selection = True
                    if selection:
                        finalized = True
                        predictions = p
                        break
            if self._dataset == 'webq' and finalized:  # because torch.topk is unstable
                entities = []
                for e in entity_name: # entity_name 应该是按照实体链接的置信度排好序了
                    entities.append(e)
                if isinstance(predictions.source, str):
                    eid = entities.index(predictions.source)
                else:
                    eid = entities.index(predictions.source[0])
                for p in beam_programs:
                    if p.code == predictions.code and p.source != predictions.source:
                        if isinstance(p.source, str):
                            peid = entities.index(p.source)
                        else:
                            peid = entities.index(p.source[0])
                        if peid < eid: # 同等条件下，选择置信度更高的链接实体导出的 program
                            eid = peid
                            predictions = p
            if not finalized:  # todo: here still need to filter null answer
                if len(beam_programs) > 0:
                    predictions = beam_programs[0]
                # elif len(candidate_programs_i) > 0:
                #     predictions = candidate_programs_i[0]  # ideally, this should never happen
                else:
                    predictions = Program()
                    print("Unexpected!!!!")
            if predictions.code_raw != '':
                predictions.code_raw = postprocess_raw_code(predictions.code_raw)
        except UnboundLocalError:  
            print("question:", question)
        
        result = {
            "predictions": predictions,
            "qid": qid
        }

        return result

    def _get_top_candidates(
        self, 
        candidate_programs: List[Program],
        question: str,
    ):
        '''暂时不做任何排序，直接返回'''
        scores = [random.random() for _ in range(len(candidate_programs))]
        scores = torch.FloatTensor(scores)
        # 为什么要 + 5? 还要过滤掉一些不可执行的 program
        top_scores, top_indices = torch.topk(torch.FloatTensor(scores), k=min([len(candidate_programs), self._beam_size + 5]))
        
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