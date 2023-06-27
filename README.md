:mega: :mega:**(This is mainly for reproducing our ACL'2023 results on KBQA. In the next version, we will release the generic Pangu library.)**

# Don't Generate, Discriminate: A Proposal for Grounding Language Models to Real-World Environments

>A key missing capacity of current language models (LMs) is grounding to real-world environments. Most existing work for grounded language understanding uses LMs to directly generate plans that can be executed in the environment to achieve the desired effects. It thereby casts the burden of ensuring grammaticality, faithfulness, and controllability all on the LMs. We propose Pangu, a generic framework for grounded language understanding that capitalizes on the discriminative ability of LMs instead of their generative ability. Pangu consists of a symbolic agent and a neural LM working in a concerted fashion: The agent explores the environment to incrementally construct valid plans, and the LM evaluates the plausibility of the candidate plans to guide the search process. A case study on the challenging problem of knowledge base question answering (KBQA), which features a massive environment, demonstrates the remarkable effectiveness and flexibility of Pangu: A BERT-base LM is sufficient for setting a new record on standard KBQA datasets, and larger LMs further bring substantial gains. Pangu also enables, for the first time, effective few-shot in-context learning for KBQA with large LMs such as Codex.

<img width="991" alt="image" src="https://github.com/entslscheia/pangu_anonymous/assets/15921425/8108955c-6211-40ac-92a3-1231a588181c">


## Environment Setup
Please configure your own conda environment using `environment.yml`. Replace `[your_conda_path]` in that file with the path of your local anaconda folder.

## File Structure
```
pangu_anonymous/
├─  acl_configs/: configuration files for training and inference
├─  data/: KBQA data files (e.g., GrailQA)
├─  ontology/: Processed Freebase ontology files
├─  answer_typing/: Answer typing results
├─  el_results/: Entity linking results 
├─  utils/:
│    ├─  bert_interface.py: Interface to BERT 
│    ├─  huggingface_interface.py: Interface to Huggingface models 
│    ├─  logic_form_util.py: Tools related to logical forms, including the exact match checker for two logical forms
│    ├─  sparql_executor.py: Sparql-related tools
│    ├─  kb_environment.py: Core functions for KB querying and constrained decoding
│    └── sparql_cache.py: Cache executions of different types of Sparql queries
├─  new_model/:
│    ├─  bottom_up_parser.py: Pangu model class
│    └── bottom_up_parser_reader.py: Pangu dataset reader class
├─  new_model/: prediction results in json
├─  run.py: Main function
└── environment.yml: yml file for conda environment 
```

## Training & Inference
```
PYTHONHASHSEED=23 python run.py
    \ train
    \ acl_configs/grail_train.jsonnet
    \ --include-package
    \ new_model.bottom_up_parser
    \ --include-package
    \ new_model.bottom_up_parser_reader
    \ --include-package
    \ utils.huggingface_interface
    \ -s
    \ [output_dir]
```

To do inference with a saved model, use the first configuration in `launch.json`, or do
```
PYTHONHASHSEED=23 python run.py
    \ predict
    \ [output_dir]/model.tar.gz
    \ [path_to_file] (e.g., grail_v1.0_test_public.json)
    \ --include-package
    \ new_model.bottom_up_parser
    \ --include-package
    \ new_model.bottom_up_parser_reader
    \ --include-package
    \ utils.huggingface_interface
    \ -output-file
    \ predictions.txt
    \ --use-dataset-reader
    \ -o
    \ "{'model': {'infer': true}, 'validation_dataset_reader': {'infer': true, 'perfect_entity_linking': false}}"
```

In `utils.sparql_executer.py`, replace "http://127.0.0.1:3094/sparql" with your own SPARQL endpoint.

Configure your experiments following configuration files under `acl_configs`.