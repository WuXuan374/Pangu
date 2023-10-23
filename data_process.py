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


if __name__ == "__main__":
    sample_grailqa(100)