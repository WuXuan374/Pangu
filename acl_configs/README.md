#
webq_train_bert_base_original.jsonnet: github 上的回复 https://github.com/dki-lab/Pangu/issues/16

webq_train_bert_base_checkpoint.jsonnet: 下载 checkpoint 时，我根据 checkpoint 里面的日志信息，总结得到的配置信息

webq_train_bert_base.jsonnet:
- 综合 webq_train_bert_base_original.jsonnet 和 webq_train_bert_base_checkpoint.jsonnet 得到的配置信息
    - 主要是依据 webq_train_bert_base_checkpoint.jsonnet, 前者里面的一些配置信息，跑的时候会报错
- **跑模型时用这个!**
    - "em_augmentation": false, 如 https://github.com/dki-lab/Pangu/issues/10 所述