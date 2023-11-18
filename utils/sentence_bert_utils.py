from transformers import AutoTokenizer, AutoModel
import torch
import sentence_transformers
import torch.nn.functional as F
from tqdm import tqdm
from typing import List

def mean_pooling(model_output, attention_mask):
    token_embeddings = model_output[0] #First element of model_output contains all token embeddings
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)

'''单例模式'''
class SentenceSimilarityPredictor(object):
    def __init__(
        self,
        hg_model_hub_name='sentence-transformers/all-mpnet-base-v2',
        batch_size=4,
        max_length=128
    ): 
        """
        把模型的初始化放在外面，加快速度，避免重复加载
        注意：很多地方是写死的，如果要尝试不同的预训练模型，需要修改
        """
        self.tokenizer = AutoTokenizer.from_pretrained(
            hg_model_hub_name,
            cache_dir='/home/home2/xwu/Exploration/hfcache/sentence-transformers_all-mpnet-base-v2',
            local_files_only=True
        )

        self.model = AutoModel.from_pretrained(
            hg_model_hub_name,
            cache_dir='/home/home2/xwu/Exploration/hfcache/sentence-transformers_all-mpnet-base-v2',
            local_files_only=True
        )

        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.model = self.model.to(self.device)
        self.batch_size = batch_size
        self.max_length = max_length
    
    @classmethod
    def instance(cls, *args, **kwargs):
        if not hasattr(SentenceSimilarityPredictor, "_instance"):
            SentenceSimilarityPredictor._instance = SentenceSimilarityPredictor(*args, **kwargs)
        return SentenceSimilarityPredictor._instance
    
    def get_similarity(
        self,
        question:str,
        candidate_programs:List,
    ):
        scores = None
        question_encoded = self.tokenizer.batch_encode_plus(
            [question],
            padding='longest',
            truncation='longest_first',
            max_length=self.max_length,
            return_tensors='pt'
        ).to(self.device) 
        with torch.no_grad():
            model_output = self.model(**question_encoded)
        question_embeddings = mean_pooling(model_output, question_encoded['attention_mask'])
        question_embeddings = F.normalize(question_embeddings, p=2, dim=1) # (1, 768)
        for start_idx in range(0, len(candidate_programs), self.batch_size):
        # for start_idx in range(0, len(sentences), batch_size):
            batch_programs = candidate_programs[start_idx: start_idx+self.batch_size]
            batch_programs_encoded = self.tokenizer.batch_encode_plus(
                batch_programs,
                padding='longest',
                truncation='longest_first',
                max_length=self.max_length,
                return_tensors='pt'
            ).to(self.device)
            with torch.no_grad():
                model_output = self.model(**batch_programs_encoded)
            programs_embeddings = mean_pooling(model_output, batch_programs_encoded['attention_mask'])
            programs_embeddings = F.normalize(programs_embeddings, p=2, dim=1) # (batch_size, 768)
            
            batch_scores = sentence_transformers.util.cos_sim(question_embeddings, programs_embeddings)
            batch_scores = torch.squeeze(batch_scores, 0) # (batch_size)

            if scores is None:
                scores = batch_scores
            else:
                scores = torch.cat((scores, batch_scores), dim=0)
        
        return scores
        
    