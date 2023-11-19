import os
import tarfile
import logging
import random
import json
import math
from experiments import setup_custom_logger
from tqdm import tqdm
from utils.logic_form_util import lisp_to_sparql
from utils.sparql_executer import execute_query

logger = setup_custom_logger("data/test/log.txt")

'''完成实验结果的打包'''
def my_archive():
    serialization_dir = "predictions/grailqa_1025_simulated_4104_for_prediction"
    weights = "best.th"
    archive_path = None
    
    weights_file = os.path.join(serialization_dir, weights)
    if not os.path.exists(weights_file):
        logging.error("weights file %s does not exist, unable to archive model", weights_file)
        return

    config_file = os.path.join(serialization_dir, "config.json")
    if not os.path.exists(config_file):
        logging.error("config file %s does not exist, unable to archive model", config_file)
    
    if archive_path is not None:
        archive_file = archive_path
        if os.path.isdir(archive_file):
            archive_file = os.path.join(archive_file, "model.tar.gz")
    else:
        archive_file = os.path.join(serialization_dir, "model.tar.gz")
    logging.info("archiving weights and vocabulary to %s", archive_file)

    with tarfile.open(archive_file, "w:gz") as archive:
        archive.add(config_file, arcname="config.json")
        archive.add(weights_file, arcname="weights.th")
        archive.add(os.path.join(serialization_dir, "vocabulary"), arcname="vocabulary")

def load_json(fname, mode="r", encoding="utf8"):
    if "b" in mode:
        encoding = None
    with open(fname, mode=mode, encoding=encoding) as f:
        return json.load(f)

def sample_data(n=1000):
    random.seed(374)
    src_data = load_json("data/GrailQA_v1.0/grailqa_v1.0_train.json")
    data_map = {
        item["qid"]: item for item in src_data
    }
    assert len(data_map) == len(src_data)
    ids = random.sample(list(data_map.keys()), n)
    sampled_data = [
        data_map[qid] for qid in ids
    ]
    dump_json(
        sampled_data,
        f"data/GrailQA_v1.0/grailqa_v1.0_train_{n}.json"
    )

def dump_json(obj, fname, indent=4, mode='w' ,encoding="utf8", ensure_ascii=False):
    """
    @param: ensure_ascii: `False`, 字符原样输出；`True`: 对于非 ASCII 字符进行转义
    """
    if "b" in mode:
        encoding = None
    with open(fname, "w", encoding=encoding) as f:
        return json.dump(obj, f, indent=indent, ensure_ascii=ensure_ascii)

def compare_qids():
    file1 = load_json("data/GrailQA_v1.0/grailqa_v1.0_train_200.json")
    file2 = load_json("/home/home2/xwu/Experiments_FreeBase/data/input/GrailQA_v1.0/grailqa_v1.0_train_200.json")
    file1_qids = set([item["qid"] for item in file1])
    file2_qids = set([item["qid"] for item in file2])
    print(file1_qids == file2_qids)

def prf1(pred_answer, gold_answer):
    pred_answer = set([item.lower() for item in pred_answer])
    gold_answer = set([item.lower() for item in gold_answer])
    if len(pred_answer)== 0:
        if len(gold_answer)==0:
            p=1
            r=1
            f=1
        else:
            p=1
            r=0
            f=0
    elif len(gold_answer) == 0:
        p=0
        r=1
        f=0
    else:
        p = len(pred_answer & gold_answer)/ len(pred_answer)
        r = len(pred_answer & gold_answer)/ len(gold_answer)
        f = 2*(p*r)/(p+r) if p+r>0 else 0
    
    return p, r, f

def add_stats():
    from utils.equivalence_utils import ComponentBasedEquivalenceChecker
    equivalence_checker = ComponentBasedEquivalenceChecker.instance(
        logger
    )
    # TODO:
    search_results = load_json("data/output/grailqa_v1.0_train_200_2023-11-18_beam_20/final_results.json")
    src_data = load_json("data/GrailQA_v1.0/grailqa_v1.0_train_200.json")
    
    qid_to_golden = {
        example["qid"]: example
        for example in src_data
    }
    for search_item in tqdm(search_results["results"]):
        simulated_query_list = list()
        gold_item = qid_to_golden[search_item["qid"]]
        gold_answer = [a['answer_argument'] for a in gold_item["answer"]]
        gold_query = gold_item["s_expression"]
        for (idx, query) in enumerate(search_item["simulated_query_list"]):
            predicted_query = query
            try:
                sparql_query = lisp_to_sparql(predicted_query)
                predicted_answer = execute_query(sparql_query)
            except Exception as e:
                logger.error(f"err: {e}")
                predicted_answer = set()
            p, r, f = prf1(predicted_answer, gold_answer)
            try:
                equivalence, semantic_equivalence, overlapped_components = equivalence_checker.equivalent_logical_form(
                    predicted_query, gold_query
                )
            except Exception as e:
                logger.error(f"err: {e}")
                equivalence = False
                semantic_equivalence = False
                overlapped_components = set()
            simulated_query_list.append({
                "s_expression": predicted_query,
                "f1": f,
                "precision": p,
                "recall": r,
                "equivalence": equivalence,
                "semantic_equivalence": semantic_equivalence,
                "overlapped_components_length": len(overlapped_components)
            })
        search_item["simulated_query_list"] = simulated_query_list
    dump_json(search_results, "data/output/grailqa_v1.0_train_200_2023-11-18_beam_20/final_results_stats.json")   

def add_summary_stats():
    results = load_json("data/output/grailqa_v1.0_train_200_2023-11-18_beam_20/final_results_stats.json")
    # f1 == 1.0 作为评价指标
    top1_answer_acc_qids = set() 
    top2_answer_acc_qids = set() 
    top3_answer_acc_qids = set() 
    # "equivalence"
    top1_equivalence_qids = set()
    top2_equivalence_qids = set()
    top3_equivalence_qids = set()
    # "semantic_equivalence"
    top1_semantic_equivalence_qids = set()
    top2_semantic_equivalence_qids = set()
    top3_semantic_equivalence_qids = set()
    # overlapped_components_length
    top1_has_overlap_qids = set()
    top2_has_overlap_qids = set()
    top3_has_overlap_qids = set()
    for search_item in tqdm(results["results"]):
        qid = search_item["qid"]
        for (idx, query) in enumerate(search_item["simulated_query_list"]):
            if math.isclose(query["f1"], 1.0):
                if idx + 1 == 1:
                    top1_answer_acc_qids.add(qid)
                    top2_answer_acc_qids.add(qid)
                    top3_answer_acc_qids.add(qid)
                elif idx + 1 == 2:
                    top2_answer_acc_qids.add(qid)
                    top3_answer_acc_qids.add(qid)
                elif idx + 1 == 3:
                    top3_answer_acc_qids.add(qid)
                else:
                    raise Exception(f"idx: {idx}; search_item: {search_item}")
            
            if query["equivalence"] is True:
                if idx + 1 == 1:
                    top1_equivalence_qids.add(qid)
                    top2_equivalence_qids.add(qid)
                    top3_equivalence_qids.add(qid)
                elif idx + 1 == 2:
                    top2_equivalence_qids.add(qid)
                    top3_equivalence_qids.add(qid)
                elif idx + 1 == 3:
                    top3_equivalence_qids.add(qid)
                else:
                    raise Exception(f"idx: {idx}; search_item: {search_item}")
            
            if query["semantic_equivalence"] is True:
                if idx + 1 == 1:
                    top1_semantic_equivalence_qids.add(qid)
                    top2_semantic_equivalence_qids.add(qid)
                    top3_semantic_equivalence_qids.add(qid)
                elif idx + 1 == 2:
                    top2_semantic_equivalence_qids.add(qid)
                    top3_semantic_equivalence_qids.add(qid)
                elif idx + 1 == 3:
                    top3_semantic_equivalence_qids.add(qid)
                else:
                    raise Exception(f"idx: {idx}; search_item: {search_item}")

            if query["overlapped_components_length"] > 0:
                if idx + 1 == 1:
                    top1_has_overlap_qids.add(qid)
                    top2_has_overlap_qids.add(qid)
                    top3_has_overlap_qids.add(qid)
                elif idx + 1 == 2:
                    top2_has_overlap_qids.add(qid)
                    top3_has_overlap_qids.add(qid)
                elif idx + 1 == 3:
                    top3_has_overlap_qids.add(qid)
                else:
                    raise Exception(f"idx: {idx}; search_item: {search_item}")

    results["summary"]["Top1答案一致"] = len(top1_answer_acc_qids)
    results["summary"]["Top2答案一致"] = len(top2_answer_acc_qids)
    results["summary"]["Top3答案一致"] = len(top3_answer_acc_qids)
    results["summary"]["Top1等价查询"] = len(top1_equivalence_qids)
    results["summary"]["Top2等价查询"] = len(top2_equivalence_qids)
    results["summary"]["Top3等价查询"] = len(top3_equivalence_qids)
    results["summary"]["Top1语义等价"] = len(top1_semantic_equivalence_qids)
    results["summary"]["Top2语义等价"] = len(top2_semantic_equivalence_qids)
    results["summary"]["Top3语义等价"] = len(top3_semantic_equivalence_qids)
    results["summary"]["Top1有效子成分"] = len(top1_has_overlap_qids)
    results["summary"]["Top2有效子成分"] = len(top2_has_overlap_qids)
    results["summary"]["Top3有效子成分"] = len(top3_has_overlap_qids)
    dump_json(results, "data/output/grailqa_v1.0_train_200_2023-11-18_beam_20/final_results_stats.json") 

if __name__ == '__main__':
    # my_archive()
    # sample_data(n=200)
    # compare_qids()
    add_stats()
    add_summary_stats()