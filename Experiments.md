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
    predictions/webqsp_train_2024-03-12
```

预测, 使用 linking results
```shell
PYTHONHASHSEED=23 python run.py \
    predict \
    predictions/webqsp_train_2024-03-12/model.tar.gz \
    data/webqsp/webqsp_0107.test.json \
    --include-package \
    new_model.bottom_up_parser \
    --include-package \
    new_model.bottom_up_parser_reader \
    --include-package \
    utils.huggingface_interface \
    --output-file \
    predictions/webqsp_train_2024-03-12/predictions.txt \
    --use-dataset-reader \
    --cuda 0 \
    -o \
    "{'model': {'infer': true}, 'validation_dataset_reader': {'infer': true, 'perfect_entity_linking': false}}"
```

在 webqsp_evaluate.py 中
首先执行 (需要到函数内对应修改文件名)
```shell
convert_prediction_format('webqsp_train_2024-03-12')
```

随后运行(main())
```shell
python webqsp_evaluate.py data/webqsp/origin/WebQSP/data/WebQSP.test.json predictions/webqsp_train_2024-03-12/predictions_for_evaluation.json
```

预测, 使用 Oracle entity linking 
cuda=2, 仍然是 GeForce 卡，应该效果是一样的
```shell
PYTHONHASHSEED=23 python run.py \
    predict \
    predictions/webqsp_train_2024-03-12/model.tar.gz \
    data/webqsp/webqsp_0107.test.json \
    --include-package \
    new_model.bottom_up_parser \
    --include-package \
    new_model.bottom_up_parser_reader \
    --include-package \
    utils.huggingface_interface \
    --output-file \
    predictions/webqsp_train_2024-03-12/predictions_oracle_entity_linking.txt \
    --use-dataset-reader \
    --cuda 2 \
    -o \
    "{'model': {'infer': true}, 'validation_dataset_reader': {'infer': true, 'perfect_entity_linking': true}}"
```


在 webqsp_evaluate.py 中
首先执行 (需要到函数内对应修改文件名)
```shell
convert_prediction_format('webqsp_train_2024-03-12')
```

随后运行(main())
```shell
python webqsp_evaluate.py data/webqsp/origin/WebQSP/data/WebQSP.test.json predictions/webqsp_train_2024-03-12/predictions_oracle_entity_linking_for_evaluation.json
```

# grailqa_train_t5_0315
首先完成数据的复制，见 /home4/xwu/Pangu/data/grailqa/grailqa_train_golden_2023-03-15 下的 README

Train -- 跳过了 136 个例子 -- 这些例子一般会引起异常，所以我们打算在 reading 阶段就排除掉
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
    predictions/grailqa_train_golden_2024-03-16
```

预测
```shell
PYTHONHASHSEED=23 python run.py \
    predict \
    predictions/grailqa_train_golden_2024-03-16/model.tar.gz \
    data/grailqa/grailqa_v1.0_dev.json \
    --include-package \
    new_model.bottom_up_parser \
    --include-package \
    new_model.bottom_up_parser_reader \
    --include-package \
    utils.huggingface_interface \
    --output-file \
    predictions/grailqa_train_golden_2024-03-16/predictions.txt \
    --use-dataset-reader \
    --cuda 0 \
    -o \
    "{'model': {'infer': true}, 'validation_dataset_reader': {'infer': true, 'perfect_entity_linking': false}}"
```

在 grail_evaluate.py 中
首先执行
```
convert_prediction_format('grailqa_train_golden_2024-03-16')
```

随后运行(main())
```
python grail_evaluate.py data/grailqa/grailqa_v1.0_dev.json predictions/grailqa_train_golden_2024-03-16/predictions_for_evaluation.json --fb_roles ontology/fb_roles --fb_types ontology/fb_types --reverse_properties ontology/reverse_properties
```

预测, 使用 Oracle entity linking 
```shell
PYTHONHASHSEED=23 python run.py \
    predict \
    predictions/grailqa_train_golden_2024-03-16/model.tar.gz \
    data/grailqa/grailqa_v1.0_dev.json \
    --include-package \
    new_model.bottom_up_parser \
    --include-package \
    new_model.bottom_up_parser_reader \
    --include-package \
    utils.huggingface_interface \
    --output-file \
    predictions/grailqa_train_golden_2024-03-16/predictions_oracle_entity_linking.txt \
    --use-dataset-reader \
    --cuda 1 \
    -o \
    "{'model': {'infer': true}, 'validation_dataset_reader': {'infer': true, 'perfect_entity_linking': true}}"
```
在 grail_evaluate.py 中
首先执行
```
convert_prediction_format('grailqa_train_golden_2024-03-16')
```

随后运行(main())
```
python grail_evaluate.py data/grailqa/grailqa_v1.0_dev.json predictions/grailqa_train_golden_2024-03-16/predictions_oracle_entity_linking_for_evaluation.json --fb_roles ontology/fb_roles --fb_types ontology/fb_types --reverse_properties ontology/reverse_properties
```


不管 WebQSP 还是 GrailQA, 都使用 DKILAB endpoint

测试集预测，使用 Linking results
```shell
PYTHONHASHSEED=23 python run.py \
    predict \
    predictions/grailqa_train_golden_2024-03-16/model.tar.gz \
    data/grailqa/grailqa_v1.0_test_public.json \
    --include-package \
    new_model.bottom_up_parser \
    --include-package \
    new_model.bottom_up_parser_reader \
    --include-package \
    utils.huggingface_interface \
    --output-file \
    predictions/grailqa_train_golden_2024-03-16/predictions_test.txt \
    --use-dataset-reader \
    --cuda 0 \
    -o \
    "{'model': {'infer': true}, 'validation_dataset_reader': {'infer': true, 'perfect_entity_linking': false}}"
```

# webqsp_train_basicQC_bert_0423
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
    predictions/webqsp_train_basicQC_2024-04-23
```

预测, 使用 linking results
```shell
PYTHONHASHSEED=23 python run.py \
    predict \
    predictions/webqsp_train_basicQC_2024-04-23/model.tar.gz \
    data/webqsp/webqsp_0107.test.json \
    --include-package \
    new_model.bottom_up_parser \
    --include-package \
    new_model.bottom_up_parser_reader \
    --include-package \
    utils.huggingface_interface \
    --output-file \
    predictions/webqsp_train_basicQC_2024-04-23/predictions.txt \
    --use-dataset-reader \
    --cuda 1 \
    -o \
    "{'model': {'infer': true}, 'validation_dataset_reader': {'infer': true, 'perfect_entity_linking': false}}"
```
在 webqsp_evaluate.py 中
首先执行 (需要到函数内对应修改文件名)
```shell
convert_prediction_format('webqsp_train_basicQC_2024-04-23')
```

随后运行(main())
```shell
python webqsp_evaluate.py data/webqsp/origin/WebQSP/data/WebQSP.test.json predictions/webqsp_train_basicQC_2024-04-23/predictions_for_evaluation.json
```



预测, 使用 Oracle entity linking 
```shell
PYTHONHASHSEED=23 python run.py \
    predict \
    predictions/webqsp_train_basicQC_2024-04-23/model.tar.gz \
    data/webqsp/webqsp_0107.test.json \
    --include-package \
    new_model.bottom_up_parser \
    --include-package \
    new_model.bottom_up_parser_reader \
    --include-package \
    utils.huggingface_interface \
    --output-file \
    predictions/webqsp_train_basicQC_2024-04-23/predictions_oracle_entity_linking.txt \
    --use-dataset-reader \
    --cuda 1 \
    -o \
    "{'model': {'infer': true}, 'validation_dataset_reader': {'infer': true, 'perfect_entity_linking': true}}"
```

在 webqsp_evaluate.py 中
首先执行 (需要到函数内对应修改文件名)
```shell
convert_prediction_format('webqsp_train_basicQC_2024-04-23')
```

随后运行(main())
```shell
python webqsp_evaluate.py data/webqsp/origin/WebQSP/data/WebQSP.test.json predictions/webqsp_train_basicQC_2024-04-23/predictions_oracle_entity_linking_for_evaluation.json
```

# grailqa_train_t5_basicQC_0426
首先完成数据的复制，见 /home4/xwu/Pangu/data/grailqa/grailqa_train_basicQC_2024-04-26 下的 README

Train
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
    predictions/grailqa_train_basicQC_2024-04-26
```

预测 (Linking Result)
```shell
PYTHONHASHSEED=23 python run.py \
    predict \
    predictions/grailqa_train_basicQC_2024-04-26/model.tar.gz \
    data/grailqa/grailqa_v1.0_dev.json \
    --include-package \
    new_model.bottom_up_parser \
    --include-package \
    new_model.bottom_up_parser_reader \
    --include-package \
    utils.huggingface_interface \
    --output-file \
    predictions/grailqa_train_basicQC_2024-04-26/predictions.txt \
    --use-dataset-reader \
    --cuda 2 \
    -o \
    "{'model': {'infer': true}, 'validation_dataset_reader': {'infer': true, 'perfect_entity_linking': false}}"
```
在 grail_evaluate.py 中
首先执行
```
convert_prediction_format('grailqa_train_basicQC_2024-04-26')
```

随后运行(main())
```
python grail_evaluate.py data/grailqa/grailqa_v1.0_dev.json predictions/grailqa_train_basicQC_2024-04-26/predictions_for_evaluation.json --fb_roles ontology/fb_roles --fb_types ontology/fb_types --reverse_properties ontology/reverse_properties
```

测试集预测，使用 Linking results
```shell
PYTHONHASHSEED=23 python run.py \
    predict \
    predictions/grailqa_train_basicQC_2024-04-26/model.tar.gz \
    data/grailqa/grailqa_v1.0_test_public.json \
    --include-package \
    new_model.bottom_up_parser \
    --include-package \
    new_model.bottom_up_parser_reader \
    --include-package \
    utils.huggingface_interface \
    --output-file \
    predictions/grailqa_train_basicQC_2024-04-26/predictions_test.txt \
    --use-dataset-reader \
    --cuda 2 \
    -o \
    "{'model': {'infer': true}, 'validation_dataset_reader': {'infer': true, 'perfect_entity_linking': false}}"
```

随后执行 
```
convert_prediction_format('grailqa_train_basicQC_2024-04-26')
```

# webqsp_bert_starQC_0430
首先完成数据的复制，见 /home4/xwu/Pangu/data/webqsp/webqsp_train_starQC 下的 README

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
    predictions/webqsp_bert_starQC_0430
```

预测, 使用 linking results
```shell
PYTHONHASHSEED=23 python run.py \
    predict \
    predictions/webqsp_bert_starQC_0430/model.tar.gz \
    data/webqsp/webqsp_0107.test.json \
    --include-package \
    new_model.bottom_up_parser \
    --include-package \
    new_model.bottom_up_parser_reader \
    --include-package \
    utils.huggingface_interface \
    --output-file \
    predictions/webqsp_bert_starQC_0430/predictions.txt \
    --use-dataset-reader \
    --cuda 0 \
    -o \
    "{'model': {'infer': true}, 'validation_dataset_reader': {'infer': true, 'perfect_entity_linking': false}}"
```

```
在 webqsp_evaluate.py 中
首先执行 (需要到函数内对应修改文件名)
```shell
convert_prediction_format('webqsp_bert_starQC_0430')
```

随后运行(main())
```shell
python webqsp_evaluate.py data/webqsp/origin/WebQSP/data/WebQSP.test.json predictions/webqsp_bert_starQC_0430/predictions_for_evaluation.json
```

预测, 使用 Oracle entity linking
```shell
PYTHONHASHSEED=23 python run.py \
    predict \
    predictions/webqsp_bert_starQC_0430/model.tar.gz \
    data/webqsp/webqsp_0107.test.json \
    --include-package \
    new_model.bottom_up_parser \
    --include-package \
    new_model.bottom_up_parser_reader \
    --include-package \
    utils.huggingface_interface \
    --output-file \
    predictions/webqsp_bert_starQC_0430/predictions_oracle_entity_linking.txt \
    --use-dataset-reader \
    --cuda 1 \
    -o \
    "{'model': {'infer': true}, 'validation_dataset_reader': {'infer': true, 'perfect_entity_linking': true}}"
```

```
在 webqsp_evaluate.py 中
首先执行 (需要到函数内对应修改文件名)
```shell
convert_prediction_format('webqsp_bert_starQC_0430')
```

随后运行(main())
```shell
python webqsp_evaluate.py data/webqsp/origin/WebQSP/data/WebQSP.test.json predictions/webqsp_bert_starQC_0430/predictions_oracle_entity_linking_for_evaluation.json
```

# webqsp_bert_baseline_0502
首先完成数据的复制，见 /home4/xwu/Pangu/data/webqsp/webqsp_train_baseline 下的 README

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
    predictions/webqsp_bert_baseline_0502
```

预测, 使用 Oracle entity linking 
```shell
PYTHONHASHSEED=23 python run.py \
    predict \
    predictions/webqsp_bert_baseline_0502/model.tar.gz \
    data/webqsp/webqsp_0107.test.json \
    --include-package \
    new_model.bottom_up_parser \
    --include-package \
    new_model.bottom_up_parser_reader \
    --include-package \
    utils.huggingface_interface \
    --output-file \
    predictions/webqsp_bert_baseline_0502/predictions_oracle_entity_linking.txt \
    --use-dataset-reader \
    --cuda 0 \
    -o \
    "{'model': {'infer': true}, 'validation_dataset_reader': {'infer': true, 'perfect_entity_linking': true}}"
```

在 webqsp_evaluate.py 中
首先执行 (需要到函数内对应修改文件名)
```shell
convert_prediction_format('webqsp_bert_baseline_0502')
```

随后运行(main())
```shell
python webqsp_evaluate.py data/webqsp/origin/WebQSP/data/WebQSP.test.json predictions/webqsp_bert_baseline_0502/predictions_oracle_entity_linking_for_evaluation.json
```


预测, 使用 linking results
```shell
PYTHONHASHSEED=23 python run.py \
    predict \
    predictions/webqsp_bert_baseline_0502/model.tar.gz \
    data/webqsp/webqsp_0107.test.json \
    --include-package \
    new_model.bottom_up_parser \
    --include-package \
    new_model.bottom_up_parser_reader \
    --include-package \
    utils.huggingface_interface \
    --output-file \
    predictions/webqsp_bert_baseline_0502/predictions.txt \
    --use-dataset-reader \
    --cuda 0 \
    -o \
    "{'model': {'infer': true}, 'validation_dataset_reader': {'infer': true, 'perfect_entity_linking': false}}"
```
在 webqsp_evaluate.py 中
首先执行 (需要到函数内对应修改文件名)
```shell
convert_prediction_format('webqsp_bert_baseline_0502')
```

随后运行(main())
```shell
python webqsp_evaluate.py data/webqsp/origin/WebQSP/data/WebQSP.test.json predictions/webqsp_bert_baseline_0502/predictions_for_evaluation.json
```

# grailqa_train_t5_starQC_0505
首先完成数据的复制，见 /home4/xwu/Pangu/data/grailqa/grailqa_train_t5_starQC_0505 下的 README

Train
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
    predictions/grailqa_train_t5_starQC_0505
```

# debug
训练集使用 grailqa_train_simulated_1000.json, 1000 个样本
验证集使用 grailqa_dev_simulated.json，都是模拟查询
暂时移除缓存
修改脚本
- 训练集
- 验证集
- "+EM" 改成 "+F1"

Train
```shell
PYTHONHASHSEED=23 python run.py \
    train \
    acl_configs/grail_train_t5_for_debug.jsonnet \
    --include-package \
    new_model.bottom_up_parser \
    --include-package \
    new_model.bottom_up_parser_reader \
    --include-package \
    utils.huggingface_interface \
    -s \
    predictions/grailqa_debug
```

# grailqa_njuthesis_starQC_0510_with_simulated_dev
主要区别: 验证集也使用模拟查询
Train
```shell
PYTHONHASHSEED=23 python run.py \
    train \
    acl_configs/grail_train_t5_with_simulated_dev.jsonnet \
    --include-package \
    new_model.bottom_up_parser \
    --include-package \
    new_model.bottom_up_parser_reader \
    --include-package \
    utils.huggingface_interface \
    -s \
    predictions/grailqa_njuthesis_starQC_0510_with_simulated_dev
```

**原始**验证集上的 prediction, 使用 Linking result
```shell
PYTHONHASHSEED=23 python run.py \
    predict \
    predictions/grailqa_njuthesis_starQC_0510_with_simulated_dev/model.tar.gz \
    data/grailqa/grailqa_v1.0_dev.json \
    --include-package \
    new_model.bottom_up_parser \
    --include-package \
    new_model.bottom_up_parser_reader \
    --include-package \
    utils.huggingface_interface \
    --output-file \
    predictions/grailqa_njuthesis_starQC_0510_with_simulated_dev/predictions.txt \
    --use-dataset-reader \
    --cuda 2 \
    -o \
    "{'model': {'infer': true}, 'validation_dataset_reader': {'infer': true, 'perfect_entity_linking': false}}"
```

在 grail_evaluate.py 中
首先执行
```
convert_prediction_format('grailqa_njuthesis_starQC_0510_with_simulated_dev')
```

随后运行(main())
```
python grail_evaluate.py data/grailqa/grailqa_v1.0_dev.json predictions/grailqa_njuthesis_starQC_0510_with_simulated_dev/predictions_for_evaluation.json --fb_roles ontology/fb_roles --fb_types ontology/fb_types --reverse_properties ontology/reverse_properties
```

测试集 Prediction，使用 Linking results
```shell
PYTHONHASHSEED=23 python run.py \
    predict \
    predictions/grailqa_njuthesis_starQC_0510_with_simulated_dev/model.tar.gz \
    data/grailqa/grailqa_v1.0_test_public.json \
    --include-package \
    new_model.bottom_up_parser \
    --include-package \
    new_model.bottom_up_parser_reader \
    --include-package \
    utils.huggingface_interface \
    --output-file \
    predictions/grailqa_njuthesis_starQC_0510_with_simulated_dev/test_set/predictions_test.txt \
    --use-dataset-reader \
    --cuda 2 \
    -o \
    "{'model': {'infer': true}, 'validation_dataset_reader': {'infer': true, 'perfect_entity_linking': false}}"
```

随后执行 
```
convert_prediction_format('grailqa_njuthesis_starQC_0510_with_simulated_dev')
```


# grailqa_njuthesis_basicQC_0513_with_simulated_dev
主要区别: 验证集也使用模拟查询
Train
```shell
PYTHONHASHSEED=23 python run.py \
    train \
    acl_configs/grail_train_t5_with_simulated_dev.jsonnet \
    --include-package \
    new_model.bottom_up_parser \
    --include-package \
    new_model.bottom_up_parser_reader \
    --include-package \
    utils.huggingface_interface \
    -s \
    predictions/grailqa_njuthesis_basicQC_0513_with_simulated_dev
```

测试集 Prediction，使用 Linking results
```shell
PYTHONHASHSEED=23 python run.py \
    predict \
    predictions/grailqa_njuthesis_basicQC_0513_with_simulated_dev/model.tar.gz \
    data/grailqa/grailqa_v1.0_test_public.json \
    --include-package \
    new_model.bottom_up_parser \
    --include-package \
    new_model.bottom_up_parser_reader \
    --include-package \
    utils.huggingface_interface \
    --output-file \
    predictions/grailqa_njuthesis_basicQC_0513_with_simulated_dev/test_set/predictions.txt \
    --use-dataset-reader \
    --cuda 2 \
    -o \
    "{'model': {'infer': true}, 'validation_dataset_reader': {'infer': true, 'perfect_entity_linking': false}}"
```

随后执行 
```
convert_prediction_format('grailqa_njuthesis_basicQC_0513_with_simulated_dev')
```

**原始**验证集上的 prediction, 使用 Linking result
```shell
PYTHONHASHSEED=23 python run.py \
    predict \
    predictions/grailqa_njuthesis_basicQC_0513_with_simulated_dev/model.tar.gz \
    data/grailqa/grailqa_v1.0_dev.json \
    --include-package \
    new_model.bottom_up_parser \
    --include-package \
    new_model.bottom_up_parser_reader \
    --include-package \
    utils.huggingface_interface \
    --output-file \
    predictions/grailqa_njuthesis_basicQC_0513_with_simulated_dev/predictions.txt \
    --use-dataset-reader \
    --cuda 2 \
    -o \
    "{'model': {'infer': true}, 'validation_dataset_reader': {'infer': true, 'perfect_entity_linking': false}}"
```

在 grail_evaluate.py 中
首先执行
```
convert_prediction_format('grailqa_njuthesis_basicQC_0513_with_simulated_dev')
```

随后运行(main())
```
python grail_evaluate.py data/grailqa/grailqa_v1.0_dev.json predictions/grailqa_njuthesis_basicQC_0513_with_simulated_dev/predictions_for_evaluation.json --fb_roles ontology/fb_roles --fb_types ontology/fb_types --reverse_properties ontology/reverse_properties
```

# webqsp_no_training
Pangu 不做任何训练，在 WebQSP 上的实验效果
参数
- 训练数据替换为一个空文件
- 训练轮数替换为 1
我们看看能否训练，以及导出训练好的模型

Train 
```shell
PYTHONHASHSEED=23 python run.py \
    train \
    acl_configs/webq_train_bert_base_no_training.jsonnet \
    --include-package \
    new_model.bottom_up_parser \
    --include-package \
    new_model.bottom_up_parser_reader \
    --include-package \
    utils.huggingface_interface \
    -s \
    predictions/webqsp_bert_no_training_0521
```

预测, 使用 linking results
```shell
PYTHONHASHSEED=23 python run.py \
    predict \
    predictions/webqsp_bert_no_training_0521/model.tar.gz \
    data/webqsp/webqsp_0107.test.json \
    --include-package \
    new_model.bottom_up_parser \
    --include-package \
    new_model.bottom_up_parser_reader \
    --include-package \
    utils.huggingface_interface \
    --output-file \
    predictions/webqsp_bert_no_training_0521/predictions.txt \
    --use-dataset-reader \
    --cuda 0 \
    -o \
    "{'model': {'infer': true}, 'validation_dataset_reader': {'infer': true, 'perfect_entity_linking': false}}"
```

在 webqsp_evaluate.py 中
首先执行 (需要到函数内对应修改文件名)
```shell
convert_prediction_format('webqsp_bert_no_training_0521')
```

随后运行(main())
```shell
python webqsp_evaluate.py data/webqsp/origin/WebQSP/data/WebQSP.test.json predictions/webqsp_bert_no_training_0521/predictions_for_evaluation.json
```

# grailqa_paper_starQC_0524_with_simulated_dev
验证集也使用模拟查询

Train
```shell
PYTHONHASHSEED=23 python run.py \
    train \
    acl_configs/grail_train_t5_with_simulated_dev.jsonnet \
    --include-package \
    new_model.bottom_up_parser \
    --include-package \
    new_model.bottom_up_parser_reader \
    --include-package \
    utils.huggingface_interface \
    -s \
    predictions/grailqa_paper_starQC_0524_with_simulated_dev
```

Epoch 2 prediction 过程中遇到了网络问题，因此额外跑一遍 Epoch 2 prediction
- 模拟查询构成的验证集
- perfect_entity_linking

```shell
PYTHONHASHSEED=23 python run.py \
    predict \
    predictions/grailqa_paper_starQC_0524_with_simulated_dev/epoch_2_model.tar.gz \
    data/grailqa/grailqa_paper_starQC_0524/grailqa_dev_simulated.json \
    --include-package \
    new_model.bottom_up_parser \
    --include-package \
    new_model.bottom_up_parser_reader \
    --include-package \
    utils.huggingface_interface \
    --output-file \
    predictions/grailqa_paper_starQC_0524_with_simulated_dev/epoch_2_prediction/predictions.txt \
    --use-dataset-reader \
    --cuda 2 \
    -o \
    "{'model': {'infer': true}, 'validation_dataset_reader': {'infer': true, 'perfect_entity_linking': true}}"
```

**原始**验证集上的 prediction, 使用 Linking result
```shell
PYTHONHASHSEED=23 python run.py \
    predict \
    predictions/grailqa_paper_starQC_0524_with_simulated_dev/model.tar.gz \
    data/grailqa/grailqa_v1.0_dev.json \
    --include-package \
    new_model.bottom_up_parser \
    --include-package \
    new_model.bottom_up_parser_reader \
    --include-package \
    utils.huggingface_interface \
    --output-file \
    predictions/grailqa_paper_starQC_0524_with_simulated_dev/predictions.txt \
    --use-dataset-reader \
    --cuda 2 \
    -o \
    "{'model': {'infer': true}, 'validation_dataset_reader': {'infer': true, 'perfect_entity_linking': false}}"
```

在 grail_evaluate.py 中
首先执行
```
convert_prediction_format('grailqa_paper_starQC_0524_with_simulated_dev')
```

随后运行(main()) --> 模拟查询构成的验证集
```
python grail_evaluate.py data/grailqa/grailqa_v1.0_dev.json predictions/grailqa_paper_starQC_0524_with_simulated_dev/predictions_for_evaluation.json --fb_roles ontology/fb_roles --fb_types ontology/fb_types --reverse_properties ontology/reverse_properties
```

测试集 Prediction，使用 Linking results
```shell
PYTHONHASHSEED=23 python run.py \
    predict \
    predictions/grailqa_paper_starQC_0524_with_simulated_dev/model.tar.gz \
    data/grailqa/grailqa_v1.0_test_public.json \
    --include-package \
    new_model.bottom_up_parser \
    --include-package \
    new_model.bottom_up_parser_reader \
    --include-package \
    utils.huggingface_interface \
    --output-file \
    predictions/grailqa_paper_starQC_0524_with_simulated_dev/test_set/predictions.txt \
    --use-dataset-reader \
    --cuda 2 \
    -o \
    "{'model': {'infer': true}, 'validation_dataset_reader': {'infer': true, 'perfect_entity_linking': false}}"
```

随后执行 
```
convert_prediction_format('grailqa_paper_starQC_0524_with_simulated_dev')
```

# grailqa_paper_baseline_0601_with_simulated_dev
验证集也使用模拟查询

Train
```shell
PYTHONHASHSEED=23 python run.py \
    train \
    acl_configs/grail_train_t5_with_simulated_dev.jsonnet \
    --include-package \
    new_model.bottom_up_parser \
    --include-package \
    new_model.bottom_up_parser_reader \
    --include-package \
    utils.huggingface_interface \
    -s \
    predictions/grailqa_paper_baseline_0601_with_simulated_dev
```

测试集 Prediction，使用 Linking results
```shell
PYTHONHASHSEED=23 python run.py \
    predict \
    predictions/grailqa_paper_baseline_0601_with_simulated_dev/model.tar.gz \
    data/grailqa/grailqa_v1.0_test_public.json \
    --include-package \
    new_model.bottom_up_parser \
    --include-package \
    new_model.bottom_up_parser_reader \
    --include-package \
    utils.huggingface_interface \
    --output-file \
    predictions/grailqa_paper_baseline_0601_with_simulated_dev/test_set/predictions.txt \
    --use-dataset-reader \
    --cuda 2 \
    -o \
    "{'model': {'infer': true}, 'validation_dataset_reader': {'infer': true, 'perfect_entity_linking': false}}"
```

随后执行 
```
convert_prediction_format('grailqa_paper_baseline_0601_with_simulated_dev')
```

**原始**验证集上的 prediction, 使用 Linking result
```shell
PYTHONHASHSEED=23 python run.py \
    predict \
    predictions/grailqa_paper_baseline_0601_with_simulated_dev/model.tar.gz \
    data/grailqa/grailqa_v1.0_dev.json \
    --include-package \
    new_model.bottom_up_parser \
    --include-package \
    new_model.bottom_up_parser_reader \
    --include-package \
    utils.huggingface_interface \
    --output-file \
    predictions/grailqa_paper_baseline_0601_with_simulated_dev/predictions.txt \
    --use-dataset-reader \
    --cuda 2 \
    -o \
    "{'model': {'infer': true}, 'validation_dataset_reader': {'infer': true, 'perfect_entity_linking': false}}"
```

在 grail_evaluate.py 中
首先执行
```
convert_prediction_format('grailqa_paper_baseline_0601_with_simulated_dev')
```

随后运行(main()) --> 模拟查询构成的验证集
```
python grail_evaluate.py data/grailqa/grailqa_v1.0_dev.json predictions/grailqa_paper_baseline_0601_with_simulated_dev/predictions_for_evaluation.json --fb_roles ontology/fb_roles --fb_types ontology/fb_types --reverse_properties ontology/reverse_properties
```
