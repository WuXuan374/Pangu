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