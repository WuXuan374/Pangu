# 10-25
输入文件位置: data/grailqa/1025
已经修改了 lisp_to_sparql 函数

!! 每次实验，需要在 grail_train_t5.jsonnet 脚本中修改
- train_data_path
- device

!! evaluate 之前
- 调用 grailqa_evaluate.py 中的 `convert_prediction_format`, 把 prediction.txt 转成 prediction_for_evaluation.json

original_4500
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
    predictions/grailqa_1025_original_4500
```
预测 original_4500
```shell
PYTHONHASHSEED=23 python run.py \
    predict \
    predictions/grailqa_1025_original_4500/model.tar.gz \
    data/grailqa/grailqa_v1.0_dev.json \
    --include-package \
    new_model.bottom_up_parser \
    --include-package \
    new_model.bottom_up_parser_reader \
    --include-package \
    utils.huggingface_interface \
    --output-file \
    predictions/grailqa_1025_original_4500/predictions.txt \
    --use-dataset-reader \
    --cuda 0 \
    -o \
    "{'model': {'infer': true}, 'validation_dataset_reader': {'infer': true, 'perfect_entity_linking': false}}"
```
应该只需要保留 `model.tar.gz`
Evaluate grailqa_1025_original_4500
```shell
python grail_evaluate.py data/grailqa/grailqa_v1.0_dev.json predictions/grailqa_1025_original_4500/predictions_for_evaluation.json --fb_roles ontology/fb_roles --fb_types ontology/fb_types --reverse_properties ontology/reverse_properties
```


simulated_4104
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
    predictions/grailqa_1025_simulated_4104
```
预测 simulated_4104
```shell
PYTHONHASHSEED=23 python run.py \
    predict \
    predictions/grailqa_1025_simulated_4104/model.tar.gz \
    data/grailqa/grailqa_v1.0_dev.json \
    --include-package \
    new_model.bottom_up_parser \
    --include-package \
    new_model.bottom_up_parser_reader \
    --include-package \
    utils.huggingface_interface \
    --output-file \
    predictions/grailqa_1025_simulated_4104/predictions.txt \
    --use-dataset-reader \
    --cuda 0 \
    -o \
    "{'model': {'infer': true}, 'validation_dataset_reader': {'infer': true, 'perfect_entity_linking': false}}"
```
Evaluate grailqa_1025_simulated_4104
```shell
python grail_evaluate.py data/grailqa/grailqa_v1.0_dev.json predictions/grailqa_1025_simulated_4104/predictions_for_evaluation.json --fb_roles ontology/fb_roles --fb_types ontology/fb_types --reverse_properties ontology/reverse_properties
```

simulated_0_200
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
预测 simulated_0_200
```shell
PYTHONHASHSEED=23 python run.py \
    predict \
    predictions/grailqa_v1.0_train_0_200_linking_2023-12-18_simulated/model.tar.gz \
    data/grailqa/grailqa_v1.0_dev.json \
    --include-package \
    new_model.bottom_up_parser \
    --include-package \
    new_model.bottom_up_parser_reader \
    --include-package \
    utils.huggingface_interface \
    --output-file \
    predictions/grailqa_v1.0_train_0_200_linking_2023-12-18_simulated/predictions.txt \
    --use-dataset-reader \
    --cuda 0 \
    -o \
    "{'model': {'infer': true}, 'validation_dataset_reader': {'infer': true, 'perfect_entity_linking': false}}"
```
Evaluate simulated_0_200
```shell
python grail_evaluate.py data/grailqa/grailqa_v1.0_dev.json predictions/grailqa_v1.0_train_0_200_linking_2023-12-18_simulated/predictions_for_evaluation.json --fb_roles ontology/fb_roles --fb_types ontology/fb_types --reverse_properties ontology/reverse_properties
```

original_0_200
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
预测 original_0_200
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
Evaluate original_0_200
```shell
python grail_evaluate.py data/grailqa/grailqa_v1.0_dev.json predictions/grailqa_v1.0_train_0_200_linking_2023-12-18_original/predictions_for_evaluation.json --fb_roles ontology/fb_roles --fb_types ontology/fb_types --reverse_properties ontology/reverse_properties
```

# webqsp_train_bert
TODO: 根据 https://github.com/dki-lab/Pangu/issues/10, 可能也要尝试 "em_augmentation": false
Train 
```shell
PYTHONHASHSEED=23 python run.py \
    train \
    acl_configs/webq_train_bert_base.jsonnet \
    --include-package \
    new_model.bottom_up_parser \
    --include-package \
    new_model.bottom_up_parser_reader \
    --include-package \
    utils.huggingface_interface \
    -s \
    predictions/webqsp_train_2023-12-29
```

预测
```shell
PYTHONHASHSEED=23 python run.py \
    predict \
    predictions/webqsp_train_2023-12-29/model.tar.gz \
    data/webqsp/webqsp_0107.test.json \
    --include-package \
    new_model.bottom_up_parser \
    --include-package \
    new_model.bottom_up_parser_reader \
    --include-package \
    utils.huggingface_interface \
    --output-file \
    predictions/webqsp_train_2023-12-29/predictions.txt \
    --use-dataset-reader \
    --cuda 0 \
    -o \
    "{'model': {'infer': true}, 'validation_dataset_reader': {'infer': true, 'perfect_entity_linking': false}}"
```

在 webqsp_evaluate.py 中
首先执行
```
convert_prediction_format('webqsp_train_2023-12-29')
```

随后运行(main())
```
python webqsp_evaluate.py data/webqsp/origin/WebQSP/data/WebQSP.test.json predictions/webqsp_train_2023-12-29/predictions_for_evaluation.json
```

预测, 使用 Oracle entity linking 
cuda=2, 仍然是 GeForce 卡，应该效果是一样的
```shell
PYTHONHASHSEED=23 python run.py \
    predict \
    predictions/webqsp_train_2023-12-29/model.tar.gz \
    data/webqsp/webqsp_0107.test.json \
    --include-package \
    new_model.bottom_up_parser \
    --include-package \
    new_model.bottom_up_parser_reader \
    --include-package \
    utils.huggingface_interface \
    --output-file \
    predictions/webqsp_train_2023-12-29/predictions_oracle_entity_linking.txt \
    --use-dataset-reader \
    --cuda 2 \
    -o \
    "{'model': {'infer': true}, 'validation_dataset_reader': {'infer': true, 'perfect_entity_linking': true}}"
```

在 webqsp_evaluate.py 中
首先执行
```
convert_prediction_format('webqsp_train_2023-12-29')
```

随后运行(main())
```
python webqsp_evaluate.py data/webqsp/origin/WebQSP/data/WebQSP.test.json predictions/webqsp_train_2023-12-29/predictions_oracle_entity_linking_for_evaluation.json
```

# grailqa_train_t5
首先完成数据的复制，见 /home4/xwu/Pangu/data/grailqa/grailqa_train_golden_2023-12-31 下的 README

Train -- 跳过了 140 个例子 -- 这些例子一般会引起异常，所以我们打算在 reading 阶段就排除掉
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
    predictions/grailqa_train_golden_2023-12-31
```

预测
```shell
PYTHONHASHSEED=23 python run.py \
    predict \
    predictions/grailqa_train_golden_2023-12-31/model.tar.gz \
    data/grailqa/grailqa_v1.0_dev.json \
    --include-package \
    new_model.bottom_up_parser \
    --include-package \
    new_model.bottom_up_parser_reader \
    --include-package \
    utils.huggingface_interface \
    --output-file \
    predictions/grailqa_train_golden_2023-12-31/predictions.txt \
    --use-dataset-reader \
    --cuda 0 \
    -o \
    "{'model': {'infer': true}, 'validation_dataset_reader': {'infer': true, 'perfect_entity_linking': false}}"
```

在 grail_evaluate.py 中
首先执行
```
convert_prediction_format('grailqa_train_golden_2023-12-31')
```

随后运行(main())
```
python grail_evaluate.py data/grailqa/grailqa_v1.0_dev.json predictions/grailqa_train_golden_2023-12-31/predictions_for_evaluation.json --fb_roles ontology/fb_roles --fb_types ontology/fb_types --reverse_properties ontology/reverse_properties
```

预测, 使用 Oracle entity linking 
```shell
PYTHONHASHSEED=23 python run.py \
    predict \
    predictions/grailqa_train_golden_2023-12-31/model.tar.gz \
    data/grailqa/grailqa_v1.0_dev.json \
    --include-package \
    new_model.bottom_up_parser \
    --include-package \
    new_model.bottom_up_parser_reader \
    --include-package \
    utils.huggingface_interface \
    --output-file \
    predictions/grailqa_train_golden_2023-12-31/predictions_oracle_entity_linking.txt \
    --use-dataset-reader \
    --cuda 0 \
    -o \
    "{'model': {'infer': true}, 'validation_dataset_reader': {'infer': true, 'perfect_entity_linking': true}}"
```
在 grail_evaluate.py 中
首先执行
```
convert_prediction_format('grailqa_train_golden_2023-12-31')
```

随后运行(main())
```
python grail_evaluate.py data/grailqa/grailqa_v1.0_dev.json predictions/grailqa_train_golden_2023-12-31/predictions_oracle_entity_linking_for_evaluation.json --fb_roles ontology/fb_roles --fb_types ontology/fb_types --reverse_properties ontology/reverse_properties
```


# webqsp_train_bert_0310
Train 
```shell
PYTHONHASHSEED=23 python run.py \
    train \
    acl_configs/webq_train_bert_base.jsonnet \
    --include-package \
    new_model.bottom_up_parser \
    --include-package \
    new_model.bottom_up_parser_reader \
    --include-package \
    utils.huggingface_interface \
    -s \
    predictions/webqsp_train_2024-03-10