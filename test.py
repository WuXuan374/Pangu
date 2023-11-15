from utils.simulated_query_enumerator import Enumerator

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

if __name__=='__main__':
    test_enumeration()