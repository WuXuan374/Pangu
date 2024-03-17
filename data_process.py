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
    grailqa_all = load_json("data/grailqa_v1.0_dev.json")
    dump_json(grailqa_all[:n], f"data/grailqa_v1.0_dev_{n}.json")

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
    qid_list = [
        "WebQTrn-790", "WebQTrn-1307", "WebQTrn-1312", "WebQTrn-2238", "WebQTrn-2642", "WebQTrn-2731", "WebQTrn-3200"
    ]
    all_data = load_json('data/webqsp/webqsp_train/webqsp_train_simulated.json')
    qid_to_data = {ex["qid"]: ex for ex in all_data}
    selected_data = [
        qid_to_data[qid] for qid in qid_list
    ]
    dump_json(selected_data, "data/webqsp/webqsp_train/webqsp_train_debug.json")

if __name__ == "__main__":
    # sample_grailqa(100)
    # find_bug_items()
    generate_debug_file()