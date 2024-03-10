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
    predictions/grailqa_v1.0_train_0_200_linking_2023-12-18_original
```
预测
```shell
PYTHONHASHSEED=23 python run.py \
    predict \
    predictions/grailqa_v1.0_train_0_200_linking_2023-12-18_original/model.tar.gz \
    data/grailqa/grailqa_v1.0_dev.json \
    --include-package \
    new_model.bottom_up_parser \
    --include-package \
    new_model.bottom_up_parser_reader \
    --include-package \
    utils.huggingface_interface \
    --output-file \
    predictions/grailqa_v1.0_train_0_200_linking_2023-12-18_original/predictions.txt \
    --use-dataset-reader \
    --cuda 0 \
    -o \
    "{'model': {'infer': true}, 'validation_dataset_reader': {'infer': true, 'perfect_entity_linking': false}}"
```

获得 F1 等指标:
```
python grailqa_evaluate.py <path_to_dev> <path_to_predictions> --fb_roles <path_to_fb_roles> --fb_types <path_to_fb_types> --reverse_properties <path_to_reverse_properties>

python grailqa_evaluate.py data/grailqa/grailqa_v1.0_dev.json predictions/grailqa_v1.0_train_0_200_linking_2023-12-18_simulated/predictions.txt --fb_roles ontology/fb_roles --fb_types ontology/fb_types --reverse_properties ontology/reverse_properties
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

# 修改过的文件记录
- 详细 diff 见 https://github.com/WuXuan374/Pangu/compare/5caf0a5..c9a1b30; diff 方式参考 https://docs.github.com/en/pull-requests/committing-changes-to-your-project/viewing-and-comparing-commits/comparing-commits
- 还有一些其他的改动，认为没必要写出来（比如一些笔记）
- utils
    - sparql_executer.py: 没有太大改动，修改了 endpoint, 以及 logging 方式
        - 网络错误等，不要直接退出程序，给个默认值（[]）即可
    - sparql_cache.py: 没有太大改动
    - kb_environment.py: 只加了一个 try-catch 结构
        - L753: 原来会报错，仍然 try-catch --> candidate_programs 不做 append, 应该没啥影响
    - logic_form_util.py: 比较重要，对于我们 S-expression 格式的一些兼容处理
        - 注意还有 WebQSP 的一点处理，被我们注释掉了; 这段处理针对字面量类型的 Literal, 但是 Simulated Query 这边，我们已经预先处理好了这种 literal 的格式("Country"@en)
            - 如果是跑 original 代码的话，可能要找回原来的版本
        - L440, 默认返回一个 dict(), 和其他情况保持一致
        - postprocess_raw_code --> 对程序影响最小的修改方式
            - bottom_up_parser.py, L757 和 L726
![Alt text](img/image.png)
- acl_configs
    - grail_train_t5.jsonnet: 主要修改训练集路径
    - webq_train_bert_base.jsonnet
        - em_augmentation=False, 按照 github issue 的说法 https://github.com/dki-lab/Pangu/issues/10
        - 训练集路径

- data_process.py: 用不上
- grailqa_evaluate.py: 官方脚本
- new_model
    - bottom_up_parser.py
        - 日志记录；**硬编码序列长度限制，避免爆显存**
        - L239: 我们观察到 height 过大，在后面 forward() 函数里面可能导致 list out of index error; 故选择在读取数据时检查 height, 如果 height 过大，则抛出一个异常（外层会舍弃这个 example）
        - L570: 同样是观察到 L614 这边，如果 gold_ids 长度大于 beam_size 会报错；故将 gold_ids 截取前 beam size 个
    - bottom_up_parser_reader.py
        - gold_answer_type 的处理
            - WebQSP test 时，采用原来的处理（没有 graph_query, 则 gold_answer_type 为 None）
        - 一些 try-catch 结构

# WebQSP 相关数据来源
data/ 目录下的数据来源: https://buckeyemailosu-my.sharepoint.com/personal/gu_826_buckeyemail_osu_edu/_layouts/15/onedrive.aspx?id=%2Fpersonal%2Fgu%5F826%5Fbuckeyemail%5Fosu%5Fedu%2FDocuments%2Fdata%2Ezip&parent=%2Fpersonal%2Fgu%5F826%5Fbuckeyemail%5Fosu%5Fedu%2FDocuments&ga=1
相关说明见 issue: https://github.com/dki-lab/Pangu/issues/10, 应该是作者官方提供的

https://github.com/dki-lab/Pangu/issues/10: 注意 WebQSP 上的效果如果不好，可能要尝试设置 em_augmentation=False （训练时）

# 关于链接结果的思考
Pangu 中的实体链接是直接使用其他工作的结果(只在 Inference 时使用链接结果)，具体而言
- GrailQA: TIARA
- WebQSP: ELQ
我们在 Simulated Query 的实验中直接使用了 Pangu 的实体链接结果
- 另外再去复现这两个方法的链接结果有点麻烦了，在 Pangu 的代码中也没有给出这两个方法的链接代码，只给了结果
- 完全做到不利用任何训练数据好像是不可能的，比如 ELQ 就是在 WebQSP 上预训练过的，这没办法
- 还需要注意的是，如果我们对比 IR 方法或者其他的 <question, answer> 方法，在 WebQSP 上，他们都使用 oracle entity linking 

## debug 结束，改成正式运行
- 训练集数据
- 缓存
