from datetime import datetime
import os
import logging
import time
import json
from tqdm import tqdm
from utils.simulated_query_enumerator import Enumerator, postprocess_raw_code
from func_timeout import func_timeout, FunctionTimedOut

def read_examples_file(file_path, perfect_el=True):
    examples = list()
    with open(file_path, 'r') as data_file:
        file_contents = json.load(data_file)
        for item in file_contents:
            if item['qid'] in [2102902009000]:  # will exceed maximum length constraint
                continue
            entity_name_map = {}
            # TODO: 暂时使用 golden 实体
            if perfect_el:
                for node in item["graph_query"]["nodes"]:
                    if node["node_type"] == "entity" or node["node_type"] == "literal":
                        if node['function'] not in ['argmax', 'argmin']:
                            entity_name_map[node['id']] = node['friendly_name'].lower()
            else:
                raise NotImplementedError(f"perfect_el: {perfect_el}")
            if "s_expression" in item:
                gold_answer_type = None
                # 优先使用查询中出现的 class 作为 gold_answer_type
                if "graph_query" in item:
                    for node in item["graph_query"]["nodes"]:
                        if node["node_type"] == 'class':
                            gold_answer_type = node['id']
                            break
                # 从 original 数据集中获得的 gold_answer_type, 同样是通过遍历 node 得到
                if gold_answer_type is None:
                    gold_answer_type = item["gold_answer_type"]
                
            examples.append({
                "question": item["question"],
                "entity_name": entity_name_map,
                "qid": item["qid"],
                "gold_answer_type": gold_answer_type,
                "gold_program": item["s_expression"] if "s_expression" in item else None
            })
    return examples

def setup_custom_logger(log_file_name):
    formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
    fileHandler = logging.FileHandler(log_file_name, mode='a')
    fileHandler.setFormatter(formatter)

    # 根据日志文件名，创建 Logger 实例；可以从不同的地方写入相同的 Log 文件
    logger = logging.getLogger(log_file_name)
    logger.setLevel(logging.INFO)
    logger.addHandler(fileHandler)
    logger.addHandler(logging.StreamHandler()) # Write to stdout as well
    time_ = time.strftime("%Y-%m-%d-%H:%M:%S", time.localtime())
    logger.info(f"Start logging: {time_}")

    return logger

def load_json(fname, mode="r", encoding="utf8"):
    if "b" in mode:
        encoding = None
    with open(fname, mode=mode, encoding=encoding) as f:
        return json.load(f)


def dump_json(obj, fname, indent=4, mode='w' ,encoding="utf8", ensure_ascii=False):
    """
    @param: ensure_ascii: `False`, 字符原样输出；`True`: 对于非 ASCII 字符进行转义
    """
    if "b" in mode:
        encoding = None
    with open(fname, "w", encoding=encoding) as f:
        return json.dump(obj, f, indent=indent, ensure_ascii=ensure_ascii)


def enumeration_grailqa_debug():
    args = dict()
    current_time = datetime.now()
    args["grailqa_file"] = "data/GrailQA_v1.0/grailqa_v1.0_train_200.json" 
    args["output_dir"] = f"data/output/grailqa_v1.0_train_200_{current_time.strftime('%Y-%m-%d_%H:%M:%S')}"
    args["sparql_timeout"] = 60
    args["detection_timeout"] = 7  # 每个问题的最大探测时间
    args["checkpoint_size"] = 50 # 每 500 条数据，把这 500 条的内容做个记录
    args["beam_size"] = 5
    args["decoding_steps"] = 5
    args["top_k"] = 3
    args["dataset"] = 'grail'

    # TODO: 训练集上目前实体 和 答案类型都使用 golden 的，后面改成链接结果吧
    examples = read_examples_file(args["grailqa_file"], perfect_el=True)[:10]
    logger = setup_custom_logger("data/test/log.txt")
    logger.info("arguments")
    for (key, value) in args.items():
        logger.info(f"{key}: {value}")
    enumerator = Enumerator.instance(
        infer=True,
        beam_size=args["beam_size"],
        decoding_steps=args["decoding_steps"],
        dataset=args["dataset"]
    )

    final_results = dict()
    final_results["results"] = list()
    final_results["summary"] = dict()
    searched_query_list = list()
    search_time_list = list()
    qid_list = list()

    logger.info(f"examples: {len(examples)}")
    for (example_idx, example) in tqdm(enumerate(examples), desc="遍历所有 GrailQA 样本"):
        detection_start_time = time.time()
        result = None
        try:
            # TODO: 暂时使用 golden answer type
            result = func_timeout(
                args["detection_timeout"],
                enumerator.run,
                args=(example["question"], example["entity_name"], example["qid"], example["gold_answer_type"], args["top_k"])
            )
        except FunctionTimedOut:
            logger.info(f"qid: {example['qid']} timed out after {args['detection_timeout']}s")
            try:
                '''小技巧，基于执行结果的 program 再选择'''
                beam_programs_sorted = sorted(
                    enumerator.all_beam_programs, key=lambda x:x[1], reverse=True
                ) # 从高到低排序

                top_k_predictions_idx = list()
                for (idx, (p, _)) in enumerate(beam_programs_sorted):  
                    if p.finalized:
                        if p.execution is None:
                            top_k_predictions_idx.append(idx)
                        elif isinstance(p.execution, int) and p.execution != 0:
                            top_k_predictions_idx.append(idx)
                        elif not isinstance(p.execution, int) and len(p.execution) > 0:
                            if not p.is_cvt(enumerator._computer):
                                top_k_predictions_idx.append(idx)
                    if len(top_k_predictions_idx) >= args["top_k"]:
                        break
                # 可能仍然少于 topk, 那么剩余内容按照得分排序，填满 topk 位置(不再做 finalized 等检查了)
                for (idx, (p, _)) in enumerate(beam_programs_sorted): 
                    if idx in top_k_predictions_idx:
                        continue
                    if len(top_k_predictions_idx) >= args["top_k"]:
                        break
                    top_k_predictions_idx.append(idx)
                top_k_predictions = [beam_programs_sorted[idx][0] for idx in top_k_predictions_idx]

                for p in top_k_predictions:
                    if p.code_raw != '':
                        p.code_raw = postprocess_raw_code(p.code_raw)
            except UnboundLocalError:  
                print("question:", example["question"])
            
            result = {
                "predictions": top_k_predictions,
                "qid": example["qid"]
            }
        
        detection_end_time = time.time()
        search_time_list.append(detection_end_time - detection_start_time)
        if result is not None and "predictions" in result:
            searched_query_list.append(result["predictions"])
            logger.info(f"qid: {example['qid']}; pred: {result['predictions']}")
        else:
            searched_query_list.append([])
        qid_list.append(example["qid"])
    
    final_results["summary"] = {
        "总数": len(examples),
        "平均搜索时间": sum(search_time_list) / len(search_time_list),
    }

    final_results["results"] = [
        {
            "qid": qid,
            "time": search_t,
            "simulated_query_list": [q.code_raw for q in query_list],
        } 
        for (query_list, search_t, qid) in zip(searched_query_list, search_time_list, qid_list)
    ]

    print(final_results)

def enumeration_grailqa():
    args = dict()
    current_time = datetime.now()
    args["grailqa_file"] = "data/GrailQA_v1.0/grailqa_v1.0_train_200.json" 
    args["output_dir"] = f"data/output/grailqa_v1.0_train_200_{current_time.strftime('%Y-%m-%d_%H:%M:%S')}"
    args["sparql_timeout"] = 60
    args["detection_timeout"] = 120  # 每个问题的最大探测时间
    args["checkpoint_size"] = 50 # 每 500 条数据，把这 500 条的内容做个记录
    args["beam_size"] = 5
    args["decoding_steps"] = 20
    args["top_k"] = 3
    args["dataset"] = 'grail'

    os.makedirs(args["output_dir"], exist_ok=True)
    tmp_dir = os.path.join(args["output_dir"], "_tmp", "")
    os.makedirs(tmp_dir, exist_ok=True)

    # TODO: 训练集上目前实体 和 答案类型都使用 golden 的，后面改成链接结果吧
    examples = read_examples_file(args["grailqa_file"], perfect_el=True)
    logger = setup_custom_logger(os.path.join(
        args["output_dir"],
        "log.txt"
    ))
    logger.info("arguments")
    for (key, value) in args.items():
        logger.info(f"{key}: {value}")
    enumerator = Enumerator.instance(
        infer=True,
        beam_size=args["beam_size"],
        decoding_steps=args["decoding_steps"],
        dataset=args["dataset"]
    )

    final_results = dict()
    final_results["results"] = list()
    final_results["summary"] = dict()
    searched_query_list = list()
    search_time_list = list()
    qid_list = list()

    logger.info(f"examples: {len(examples)}")
    for (example_idx, example) in tqdm(enumerate(examples), desc="遍历所有 GrailQA 样本"):
        detection_start_time = time.time()
        result = None
        try:
            # TODO: 暂时使用 golden answer type
            result = func_timeout(
                args["detection_timeout"],
                enumerator.run,
                args=(example["question"], example["entity_name"], example["qid"], example["gold_answer_type"], args["top_k"])
            )
        except FunctionTimedOut:
            logger.info(f"qid: {example['qid']} timed out after {args['detection_timeout']}s")
            try:
                '''小技巧，基于执行结果的 program 再选择'''
                beam_programs_sorted = sorted(
                    enumerator.all_beam_programs, key=lambda x:x[1], reverse=True
                ) # 从高到低排序

                top_k_predictions_idx = list()
                for (idx, (p, _)) in enumerate(beam_programs_sorted):  
                    if p.finalized:
                        if p.execution is None:
                            top_k_predictions_idx.append(idx)
                        elif isinstance(p.execution, int) and p.execution != 0:
                            top_k_predictions_idx.append(idx)
                        elif not isinstance(p.execution, int) and len(p.execution) > 0:
                            if not p.is_cvt(enumerator._computer):
                                top_k_predictions_idx.append(idx)
                    if len(top_k_predictions_idx) >= args["top_k"]:
                        break
                # 可能仍然少于 topk, 那么剩余内容按照得分排序，填满 topk 位置(不再做 finalized 等检查了)
                for (idx, (p, _)) in enumerate(beam_programs_sorted): 
                    if idx in top_k_predictions_idx:
                        continue
                    if len(top_k_predictions_idx) >= args["top_k"]:
                        break
                    top_k_predictions_idx.append(idx)
                top_k_predictions = [beam_programs_sorted[idx][0] for idx in top_k_predictions_idx]

                for p in top_k_predictions:
                    if p.code_raw != '':
                        p.code_raw = postprocess_raw_code(p.code_raw)
            except UnboundLocalError:  
                print("question:", example["question"])
            
            result = {
                "predictions": top_k_predictions,
                "qid": example["qid"]
            }
        except BaseException as err:
            logger.error(f"err: {err}")
        
        detection_end_time = time.time()
        search_time_list.append(detection_end_time - detection_start_time)
        if result is not None and "predictions" in result:
            searched_query_list.append(result["predictions"])
            logger.info(f"qid: {example['qid']}; pred: {result['predictions']}")
        else:
            searched_query_list.append([])
        qid_list.append(example["qid"])

        if (example_idx + 1) % args["checkpoint_size"] == 0:
            checkpoint_results = [
                {
                    "qid": qid,
                    "time": search_t,
                    "simulated_query_list": [q.code_raw for q in query_list],
                }
                for (query_list, search_t, qid) in zip(
                    searched_query_list[(example_idx + 1 - args["checkpoint_size"]): (example_idx + 1)], 
                    search_time_list[(example_idx + 1 - args["checkpoint_size"]): (example_idx + 1)], 
                    qid_list[(example_idx + 1 - args["checkpoint_size"]): (example_idx + 1)]
                )
            ]
            dump_json(checkpoint_results, os.path.join(
                tmp_dir, f'{int(example_idx / args["checkpoint_size"])}.json'
            ))
    
    final_results["summary"] = {
        "总数": len(examples),
        "平均搜索时间": sum(search_time_list) / len(search_time_list),
    }

    final_results["results"] = [
        {
            "qid": qid,
            "time": search_t,
            "simulated_query_list": [q.code_raw for q in query_list],
        } 
        for (query_list, search_t, qid) in zip(searched_query_list, search_time_list, qid_list)
    ]

    dump_json(final_results, os.path.join(
        args["output_dir"], 'final_results.json'
    ))

if __name__=='__main__':
    # enumeration_grailqa_debug()
    enumeration_grailqa()