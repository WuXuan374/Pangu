local dataset = "webq";
local decoding_steps = 5;
local device = 7;
local training_option = 2;
local val_option = 2;
local eos = "[SEP]";
{
  "dataset_reader": {
    "type": "bottom_up",
    "dataset": dataset,
    "decoding_steps": decoding_steps,
    "training_option": training_option,
    "source_tokenizer": {
      "type": "my_pretrained_transformer",
      "model_name": "bert-base-uncased",
      "do_lowercase": true
    },
    "source_token_indexers": {
        "tokens": {
              "type": "my_pretrained_transformer",
              "model_name": "bert-base-uncased",
              "do_lowercase": true,
              "namespace": "bert"
        }
    }
  },
  "validation_dataset_reader": {
    "type": "bottom_up",
    "dataset": dataset,
    "decoding_steps": decoding_steps,
    "training_option": val_option,
    "infer": true,
    "source_tokenizer": {
      "type": "my_pretrained_transformer",
      "model_name": "bert-base-uncased",
      "do_lowercase": true
    },
    "source_token_indexers": {
        "tokens": {
              "type": "my_pretrained_transformer",
              "model_name": "bert-base-uncased",
              "do_lowercase": true,
              "namespace": "bert"
        }
    }
  },

  "train_data_path": "data/webqsp_0107.train.json",
  "model": {
    "type": "bottom_up",
    "training_option": training_option,
    "val_option": val_option,
    "dataset": dataset,
    "decoding_steps": decoding_steps,
    "loss_option": 1,
    "EOS": eos,
    "using_hf": true,
    "em_augmentation": true,
    "device": device,  // this is a new field. Be careful when using -r option for training
    "source_embedder": {
//      "allow_unmatched_keys": true,
      "token_embedders": {
        "tokens": {
//          "type": "my_pretrained_transformer",
          "type": "huggingface_transformer",
          "model_name": "bert-base-uncased",
          "pooling": true
       }
      }
    },
    "hidden_size": 768,
    "dropout": 0.5
  },
  "data_loader": {   // previously iterator
    "shuffle": true,
    "batch_size": 1
  },
  "validation_data_loader": {
    "shuffle": true,
    "batch_size": 1
  },
  "trainer": {
    "num_epochs": 12,
    "validation_metric": "+EM",
    "cuda_device": device,
    "num_gradient_accumulation_steps": 8,
    "callbacks": [
      {
        "type": "track_epoch_callback"
      }
    ],
    "optimizer": {
      "type": "adam",
      "lr": 0.001,
      "parameter_groups": [
        [["source_embedder"], {"lr": 2e-5}]
      ]
    }
  },
//    "distributed": {
//     "cuda_devices": [5, 6, 7]
//    }
}