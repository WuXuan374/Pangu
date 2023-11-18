from utils.simulated_query_enumerator import Enumerator
from utils.sentence_bert_utils import SentenceSimilarityPredictor

def test_enumeration():
    question = "what drug has a pubchem id of adrenergic beta1-antagonist?"
    entity_name = {
        "m.0hqz9mq": "Adrenergic beta1-Antagonist"
    }
    qid = "2101219006000"
    answer_types = ["medicine.drug"]

    enumerator = Enumerator(
        infer=True,
        beam_size=5,
        decoding_steps=5,
        dataset='grail'
    )
    result = enumerator.run(
        question, entity_name, qid, answer_types
    )
    print(f"result: {result}")

def test_sentence_bert():
    sentence_bert_ranker = SentenceSimilarityPredictor.instance(
        hg_model_hub_name='sentence-transformers/all-mpnet-base-v2',
        batch_size=2,
        max_length=128
    )
    question = "what drug has a pubchem id of adrenergic beta1-antagonist?"
    candidate_programs = [
        "(AND broadcast.tv_channel (JOIN broadcast.tv_channel.from 2005-02-23^^http://www.w3.org/2001/XMLSchema#date))",
        "(AND computer.computer (JOIN computer.computer.introduced 1983-03-08^^http://www.w3.org/2001/XMLSchema#date))",
        "(ARGMIN (AND spaceflight.space_program (JOIN (R spaceflight.space_program_sponsor.space_programs_sponsored) m.05vz3zq)) spaceflight.space_program.started)",
        "(AND meteorology.meteorological_service (JOIN (R meteorology.tropical_cyclone_category.meteorological_service) (JOIN meteorology.tropical_cyclone_category.tropical_cyclones m.0vsgmpg)))",
        "(AND medicine.drug (JOIN medicine.drug.mechanism_of_action m.0hqz9mq))",
    ]
    scores = sentence_bert_ranker.get_similarity(
        question, candidate_programs
    )

if __name__=='__main__':
    test_enumeration()
    # test_sentence_bert()