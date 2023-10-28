# 10-25
输入文件位置: data/grailqa/1025
已经修改了 lisp_to_sparql 函数

!! 每次实验，需要在 grail_train_t5.jsonnet 脚本中修改
- train_data_path
- device

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

预测 grailqa_1025_original_4500_for_prediction
```shell
PYTHONHASHSEED=23 python run.py \
    predict \
    predictions/grailqa_1025_original_4500_for_prediction/model.tar.gz \
    data/grailqa/grailqa_v1.0_dev.json \
    --include-package \
    new_model.bottom_up_parser \
    --include-package \
    new_model.bottom_up_parser_reader \
    --include-package \
    utils.huggingface_interface \
    --output-file \
    predictions/grailqa_1025_original_4500_for_prediction/predictions.txt \
    --use-dataset-reader \
    --cuda 4 \
    -o \
    "{'model': {'infer': true}, 'validation_dataset_reader': {'infer': true, 'perfect_entity_linking': false}}"
```

Evaluate grailqa_1025_original_4500_for_prediction
```shell
python grail_valuate.py data/grailqa/grailqa_v1.0_dev.json predictions/grailqa_1025_original_4500_for_prediction/predictions_for_evaluation.json --fb_roles ontology/fb_roles --fb_types ontology/fb_types --reverse_properties ontology/reverse_properties
```
