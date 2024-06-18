import json


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

def sample_grailqa(n=100):
    # 直接取 top 100
    grailqa_all = load_json("data/grailqa/grailqa_njuthesis_starQC_0510/grailqa_train_simulated.json")
    dump_json(grailqa_all[:n], f"data/grailqa/grailqa_njuthesis_starQC_0510/grailqa_train_simulated_{n}.json")

def get_grailqa_dev_without_query():
    original = load_json("data/grailqa/grailqa_v1.0_dev.json")
    new_list = list()
    for ex in original:
        new_list.append({
            "qid": ex["qid"],
            "question": ex["question"],
            "answer": ex["answer"],
            "level": ex["level"],
            "graph_query": {
                "nodes": ex["graph_query"]["nodes"]
            }
        })
    dump_json(new_list, "data/grailqa/grailqa_v1.0_dev_wo_query.json")

def compare_prediction_result():
    from tqdm import tqdm
    src_data = load_json("data/grailqa/grailqa_v1.0_test_public.json")
    old_prediction = load_json("predictions/grailqa_njuthesis_starQC_0510_with_simulated_dev/test_set/predictions_for_evaluation.json")
    new_prediction = load_json("predictions/grailqa_paper_starQC_0524_with_simulated_dev/test_set/predictions_for_evaluation.json")
    qid_to_src = {item["qid"]: item for item in src_data}

    diff_qid_set = set()
    for qid in tqdm(old_prediction):
        assert qid in new_prediction, print(f"qid: {qid}")
        if (set(old_prediction[qid]["answer"]) != set(new_prediction[qid]["answer"])):
            diff_qid_set.add(qid)
            print(f"question: {qid_to_src[qid]['question']}; old_sexp: {old_prediction[qid]['logical_form']}; new_sexp: {new_prediction[qid]['logical_form']}")
            print()

    print(f"diff_qid_set: {len(diff_qid_set)}")

# def find_bug_items():
#     # (AND (AND (AND (AND
#     qid_list = list()
#     src_data = load_json("data/grailqa/grailqa_train_golden_2023-12-31/grailqa_train_simulated.json")
#     for item in src_data:
#         if "(AND (AND (AND (AND" in item["s_expression"]:
#             qid_list.append(item["qid"])
#     print(qid_list)
def generate_debug_file():
    # qid_list = [
    #      2101556000000, 3201695015000, 2101324002000, 3200228000000, 2101324004000, 2100279010000, 2103366003000, 2102566011000, 2105063007000, 2101324008000, 2102576009000, 2100882007000, 2100672010000, 2100559015000, 2100672015000, 4301917006000, 3203354013000, 2102300007000, 3201695006000, 2102010009000, 2100559005000, 2101411003000,
    #      3203977002000
    # ]
    # all_data = load_json('data/grailqa/grailqa_train_golden_2023-12-31/grailqa_train_simulated.json')
    # qid_to_data = {ex["qid"]: ex for ex in all_data}
    # selected_data = [
    #     qid_to_data[qid] for qid in qid_list
    # ]
    # dump_json(selected_data, "data/grailqa/grailqa_train_golden_2023-12-31/grailqa_debug.json")
    # qid_list = [
    #     "WebQTrn-790", "WebQTrn-1307", "WebQTrn-1312", "WebQTrn-2238", "WebQTrn-2642", "WebQTrn-2731", "WebQTrn-3200"
    # ]
    # all_data = load_json('data/webqsp/webqsp_train/webqsp_train_simulated.json')
    # qid_to_data = {ex["qid"]: ex for ex in all_data}
    # selected_data = [
    #     qid_to_data[qid] for qid in qid_list
    # ]
    # dump_json(selected_data, "data/webqsp/webqsp_train/webqsp_train_debug.json")

    # question_list = [
    #     "the beyonce experience : live audio is what type of musical album ?"
    # ]
    all_data = load_json('data/grailqa/grailqa_train_golden_2024-03-15/grailqa_train_simulated.json')
    # question_to_data = {ex["question"]: ex for ex in all_data}
    selected_data = [
        data_item for data_item in all_data
        if 'the beyonce experience' in data_item['question'].lower()
    ]
    dump_json(selected_data, "data/grailqa/grailqa_train_golden_2024-03-15/grailqa_train_debug.json")

def qid_overlap():
    original_test = load_json("data/grailqa/grailqa_v1.0_test_public.json")
    original_qid_set = set([item['qid'] for item in original_test])

    predicted = load_json("predictions/grailqa_train_basicQC_2024-04-26/test_set/predictions_for_evaluation.json")
    predicted_qid_set = set(predicted.keys())
    print(original_qid_set == predicted_qid_set, len(original_qid_set), len(predicted_qid_set))

def failed_count():
    predicted = load_json("predictions/grailqa_train_golden_2024-03-16/xwu_pangu_simulated_data/predictions_for_evaluation.json")
    failed_list = [
        (key, value) for (key, value) in predicted.items()
        if (not value["logical_form"]) or (not value["answer"])
    ]
    print(len(failed_list))

if __name__ == "__main__":
    # sample_grailqa(1000)
    # find_bug_items()
    # generate_debug_file()

    # print(len(load_json("data/grailqa/grailqa_v1.0_dev.json")))
    # qid_overlap()
    # failed_count()
    # get_grailqa_dev_without_query()

    '''生成一个空文件，测试 WebQSP 在不做任何训练的情况下，其 KBQA 效果'''
    # dump_json([], 'data/webqsp/webqsp_train_empty/webqsp_train_simulated.json')

    compare_prediction_result()