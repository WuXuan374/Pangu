# 代码执行过程
- 创建 conda 环境 -- "pangu"
    - 参考 https://github.com/dki-lab/Pangu/issues/3
        - 配置文件中删除一些东西
        - 需要手动安装的那两个，我没有装，照样能跑
- 替换 SPARQL 端口（记得替换成 Dkilab 的这个）
- 最好把 SPARQL 缓存先下载下来
    - 暂时没遇到查询超时，后面遇到了，可能需要下载缓存，保证 SPARQL 的执行不影响最终效果

- 配置文件: grailqa_train_t5.jsonnet
    - 我们作如下修改
        - `device`: 改成我们自己的编号？
        - `train_data_path`: 替换成 目标训练集
        - `validation_data_path`: 无需替换，原始验证集即可
        - `shuffle`: 应该都改为 true
- SPARQL 缓存检查
- GrailQA 所执行的命令
训练
```shell
PYTHONHASHSEED=23 python run.py \
    train \
    acl_configs/grail_train_t5.jsonnet \
    --include-package \
    new_model.bottom_up_parser \
    --include-package \
    new_model.bottom_up_parser_reader \
    --include-package \
    utils.huggingface_interface \
    -s \
    predictions/grailqa_v1.0_train_0_200_linking_2023-12-18_simulated
```
预测
```shell
PYTHONHASHSEED=23 python run.py \
    predict \
    predictions/grailqa_2_1023/model.tar.gz \
    data/grailqa_v1.0_dev_2.json \
    --include-package \
    new_model.bottom_up_parser \
    --include-package \
    new_model.bottom_up_parser_reader \
    --include-package \
    utils.huggingface_interface \
    --output-file \
    predictions/grailqa_2_1023/predictions.txt \
    --use-dataset-reader \
    --cuda 0 \
    -o \
    "{'model': {'infer': true}, 'validation_dataset_reader': {'infer': true, 'perfect_entity_linking': false}}"
```

# 整体流程归纳
- 关于训练比较关心的几个点:
    - 使用 EM 作为 evaluation metric
    - 有 patience 参数，GrailQA 设置为 3，作者说 GrailQA 一般训练 4 - 5 epochs 就结束了，也就是最好的 epoch 其实出现在第一轮或者第二轮
- 关于 EM
    - 各类参数都定义在 bottom_up_parser.py get_metrics() 里面
- 使用了很多 allennlp 里面的工具函数

- 数据的读取: BUParser_DatasetReader
下面介绍的都是替换成我们的 Simulated Query 之后
    - 实体链接: 直接使用他们提供的文件
    - answer_types_grail_combined.txt: 只用于 inference 和 validation, 因此直接使用他们的文件
    - ["graph_query"]["nodes"]: 
        - 里面的一些信息，仅当只用 perfect-entity-linking 时会用到
            - 训练集要求 perfect-entity-linking, 所以我们得自己抽取一下相关信息
        - 里面的 class 信息，用于 gold_answer_type; 但是这个好像是需要的？不过既然是 gold, 我们使用数据集中正确的信息，应该是没问题的（我们不需要更新）

- 总结: 除了 ["s-expression"] 之外， ["graph_query"]["nodes"] 里面的内容也做相应替换；替换方式参考我们之前的那些数据处理（从我们的 Simulated Query 中抽取这些信息）
    - 我们的 S-expression 和他们有一些格式上的不同（例如 Literal, EQ, 类型的处理等）；但是针对 Pangu, 我们做了后处理，把这些格式又转回来了

- 输出
    - metrics.json, 有验证集上的 EM, F1 等信息
    - prediction.txt (需要执行 prediction 的另外命令)， 给出每个问题预测得到的 S-expression 和 执行结果

# 数据处理
部分见 data_process.py
还有一部分见 Experiment_Freebase 下的 data_process_pangu.py --> 有一些依赖函数在那边