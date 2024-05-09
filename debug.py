import re
import json
from collections import defaultdict

def load_json(fname, mode="r", encoding="utf8"):
    if "b" in mode:
        encoding = None
    with open(fname, mode=mode, encoding=encoding) as f:
        return json.load(f)

def dump_json(obj, fname, indent=4, mode='w' ,encoding="utf8", ensure_ascii=False):
    """
    @param: ensure_ascii: `False`, 字符原样输出；`True`: 对于非 ASCII 字符进行转义
    """
    if "b" in mode:
        encoding = None
    with open(fname, "w", encoding=encoding) as f:
        return json.dump(obj, f, indent=indent, ensure_ascii=ensure_ascii)

def FindInList(entry,elist):
    for item in elist:
        if entry == item:
            return True
    return False
            
def CalculatePRF1(goldAnswerList, predAnswerList):
    if len(goldAnswerList) == 0:
        if len(predAnswerList) == 0:
            return [1.0, 1.0, 1.0]  # consider it 'correct' when there is no labeled answer, and also no predicted answer
        else:
            return [0.0, 1.0, 0.0]  # precision=0 and recall=1 when there is no labeled answer, but has some predicted answer(s)
    elif len(predAnswerList)==0:
        return [1.0, 0.0, 0.0]    # precision=1 and recall=0 when there is labeled answer(s), but no predicted answer
    else:
        glist =[x["AnswerArgument"] for x in goldAnswerList]
        plist =predAnswerList

        tp = 1e-40  # numerical trick
        fp = 0.0
        fn = 0.0

        for gentry in glist:
            if FindInList(gentry,plist):
                tp += 1
            else:
                fn += 1
        for pentry in plist:
            if not FindInList(pentry,glist):
                fp += 1


        precision = tp/(tp + fp)
        recall = tp/(tp + fn)
        
        f1 = (2*precision*recall)/(precision+recall)
        return [precision, recall, f1]


def extract_mentioned_relations_from_sexpr(sexpr:str):
    sexpr = sexpr.replace('(',' ( ').replace(')',' ) ')
    toks = sexpr.split(' ')
    toks = [x for x in toks if len(x)]
    relation_tokens = []

    for t in toks:
        if (re.match("[a-zA-Z_]*\.[a-zA-Z_]*\.[a-zA-z_]*",t.strip()) 
            or re.match("[a-zA-Z_]*\.[a-zA-Z_]*\.[a-zA-Z_]*\.[a-zA-Z_]*",t.strip())):
            relation_tokens.append(t)
    relation_tokens = list(set(relation_tokens))
    return relation_tokens

def extract_mentioned_relations_from_sparql(sparql:str):
    """extract relation from sparql"""
    sparql = sparql.replace('(',' ( ').replace(')',' ) ')
    toks = sparql.split(' ')
    toks = [x for x in toks if len(x)]
    relation_tokens = []
    for t in toks:
        if (re.match("ns:[a-zA-Z_0-9]*\.[a-zA-Z_0-9]*\.[a-zA-Z_0-9]*",t.strip()) 
            or re.match("ns:[a-zA-Z_0-9]*\.[a-zA-Z_0-9]*\.[a-zA-Z_0-9]*\.[a-zA-Z_0-9]*",t.strip())):
            relation_tokens.append(t[3:])
    
    relation_tokens = list(set(relation_tokens))
    return relation_tokens

def relation_diff():
    star_qc_training_data = load_json("data/webqsp/webqsp_train_starQC/webqsp_train_simulated.json")
    # star_qc_prediction = list()
    # with open("predictions/webqsp_train_2024-03-12/predictions.txt", 'r') as f:
    #     for line in f:
    #         line = json.loads(line)
    #         star_qc_prediction.append(line)
    
    basic_qc_training_data = load_json("data/webqsp/webqsp_train_baseline/webqsp_train_simulated.json")
    # basic_qc_prediction = list()
    # with open("predictions/webqsp_train_basicQC_2024-04-23/predictions.txt", 'r') as f:
    #     for line in f:
    #         line = json.loads(line)
    #         basic_qc_prediction.append(line)
    
    # original_train = load_json("data/webqsp/origin/WebQSP/data/WebQSP.train.json")["Questions"]
    # original_test = load_json("data/webqsp/origin/WebQSP/data/WebQSP.test.json")["Questions"]

    star_qc_training_distri = _get_relation_distribution_training(star_qc_training_data)
    # star_qc_prediction_distri = _get_relation_distribution_predict(star_qc_prediction)

    basic_qc_training_distri = _get_relation_distribution_training(basic_qc_training_data)
    # basic_qc_prediction_distri = _get_relation_distribution_predict(basic_qc_prediction)

    print(star_qc_training_distri)

    print()

    print(basic_qc_training_distri)

    # original_train_distri = _get_relation_distribution_origin(original_train)
    # original_test_distri = _get_relation_distribution_origin(original_test)

    # print(f"star_qc_training_distri: {_sort_dict_by_value(star_qc_training_distri)[:15]}")
    # print(f"star_qc_prediction_distri: {_sort_dict_by_value(star_qc_prediction_distri)[:15]}")

    # print(f"basic_qc_training_distri: {_sort_dict_by_value(basic_qc_training_distri)[:15]}")
    # print(f"basic_qc_prediction_distri: {_sort_dict_by_value(basic_qc_prediction_distri)[:15]}")

    # print(f"original_test_distri: {_sort_dict_by_value(original_train_distri)[:15]}")
    # print(f"original_test_distri: {_sort_dict_by_value(original_test_distri)[:15]}")

    # star_qc_more_rels = set()
    # basic_qc_more_rels = set()
    # for key in star_qc_training_distri:
    #     if star_qc_training_distri[key] - basic_qc_training_distri.get(key, 0) > 20:
    #         star_qc_more_rels.add(key)
    #     elif basic_qc_training_distri.get(key, 0) - star_qc_training_distri[key] > 20:
    #         basic_qc_more_rels.add(key)


    # for key in basic_qc_training_distri:
    #     if basic_qc_training_distri[key] - star_qc_training_distri.get(key, 0) > 20:
    #         basic_qc_more_rels.add(key)
    #     elif star_qc_training_distri.get(key, 0) - basic_qc_training_distri[key] > 20:
    #         star_qc_more_rels.add(key)

    # print(f"star_qc_more_rels: {star_qc_more_rels}")
    # print(f"basic_qc_more_rels: {basic_qc_more_rels}")

    

def _get_relation_distribution_training(data_list):
    relation_distribution = defaultdict(int)
    for item in data_list:
        relation_list = extract_mentioned_relations_from_sexpr(item["s_expression"])
        for _rel in relation_list:
            relation_distribution[_rel] += 1
    return relation_distribution

def _get_relation_distribution_predict(data_list):
    relation_distribution = defaultdict(int)
    for item in data_list:
        relation_list = extract_mentioned_relations_from_sexpr(item["logical_form"])
        for _rel in relation_list:
            relation_distribution[_rel] += 1
    return relation_distribution

def _get_relation_distribution_origin(data_list):
    relation_distribution = defaultdict(int)
    for item in data_list:
        for parse in item["Parses"]:
            relation_list = extract_mentioned_relations_from_sparql(parse["Sparql"])
            for _rel in relation_list:
                relation_distribution[_rel] += 1
    return relation_distribution

def _sort_dict_by_value(dic):
    return list(sorted(dic.items(), key=lambda item: item[1], reverse=True))

def webqsp_evaluate_with_record(folder):

    goldData = load_json('data/webqsp/origin/WebQSP/data/WebQSP.test.json')
    predAnswers = load_json(f'predictions/{folder}/debug/predictions_for_evaluation.json')

    PredAnswersById = {}
    PredById = {}

    for item in predAnswers:
        PredAnswersById[item["QuestionId"]] = item["Answers"]
        PredById[item["QuestionId"]] = item

    total = 0.0
    f1sum = 0.0
    recSum = 0.0
    precSum = 0.0
    numCorrect = 0
    results = list()
    for entry in goldData["Questions"]:
        gold_relations = set()
        skip = True
        for pidx in range(0,len(entry["Parses"])):
            np = entry["Parses"][pidx]
            if np["AnnotatorComment"]["QuestionQuality"] == "Good" and np["AnnotatorComment"]["ParseQuality"] == "Complete":
                skip = False

        if(len(entry["Parses"])==0 or skip):
            continue

        total += 1
    
        id = entry["QuestionId"]
    
        if id not in PredAnswersById:
            print(f"The problem {id} is not in the prediction set")
            print("Continue to evaluate the other entries")
            continue

        if len(entry["Parses"]) == 0:
            print("Empty parses in the gold set. Breaking!!")
            break

        predAnswers = PredAnswersById[id]

        bestf1 = -9999
        bestf1Rec = -9999
        bestf1Prec = -9999
        for pidx in range(0,len(entry["Parses"])):
            # gold_relations: 考虑所有 parse
            gold_relations.update(extract_mentioned_relations_from_sparql(entry["Parses"][pidx]["Sparql"]))
            pidxAnswers = entry["Parses"][pidx]["Answers"]
            prec,rec,f1 = CalculatePRF1(pidxAnswers,predAnswers)
            if f1 > bestf1:
                bestf1 = f1
                bestf1Rec = rec
                bestf1Prec = prec

        f1sum += bestf1
        recSum += bestf1Rec
        precSum += bestf1Prec
        if bestf1 == 1.0:
            numCorrect += 1
        
        results.append({
            "qid": id,
            "pred_answer": predAnswers,
            "logical_form": PredById[id]["logical_form"],
            "f1": bestf1,
            "gold_relations": list(gold_relations)
        })
    
    dump_json(results, f'predictions/{folder}/debug/results_with_f1.json')

    print(f"Number of questions: {int(total)}")
    print("Average precision over questions: %.3f" % (precSum / total))
    print("Average recall over questions: %.3f" % (recSum / total))
    print("Average f1 over questions (accuracy): %.3f" % (f1sum / total))
    print("F1 of average recall and average precision: %.3f" % (2 * (recSum / total) * (precSum / total) / (recSum / total + precSum / total)))
    print("True accuracy (ratio of questions answered exactly correctly): %.3f" % (numCorrect / total))

def convert_prediction_format(folder):
    old_file = f"predictions/{folder}/predictions.txt"
    data = list()
    with open(old_file, 'r') as f:
        for line in f:
            line = json.loads(line)
            data.append({
                "QuestionId": line["qid"],
                "Answers": line["answer"],
                "logical_form": line["logical_form"]
            })
    json.dump(data, open(f"predictions/{folder}/debug/predictions_for_evaluation.json", 'w'))

def calculate_accumulated_f1():
    star_qc_more_rels = {'location.location.time_zones', 'education.education.institution', 'film.performance.actor', 'people.person.profession', 'tv.regular_tv_appearance.character', 'tv.regular_tv_appearance.actor', 'people.person.education'}
    basic_qc_more_rels = {'education.education.student', 'film.actor.film', 'education.educational_institution.students_graduates', 'people.profession.people_with_this_profession', 'people.person.date_of_birth', 'time.time_zone.locations_in_this_time_zone', 'award.award_nominee.award_nominations', 'sports.sports_team_roster.player', 'award.award_nomination.nominated_for', 'sports.sports_team.roster', 'location.location.contains'}
    star_qc_prediction = load_json('predictions/webqsp_train_2024-03-12/debug/results_with_f1.json')
    basic_qc_prediction = load_json('predictions/webqsp_train_basicQC_2024-04-23/debug/results_with_f1.json')
    
    star_qc_more_accumulated = {
        "star_qc": list(),
        "basic_qc": list()
    }
    basic_qc_more_accumulated = {
        "star_qc": list(),
        "basic_qc": list()
    }

    for _pred in star_qc_prediction:
        if star_qc_more_rels & set(_pred["gold_relations"]):
            star_qc_more_accumulated["star_qc"].append(_pred["f1"])
        if basic_qc_more_rels & set(_pred["gold_relations"]):
            basic_qc_more_accumulated["star_qc"].append(_pred["f1"])
        
    for _pred in basic_qc_prediction:
        if star_qc_more_rels & set(_pred["gold_relations"]):
            star_qc_more_accumulated["basic_qc"].append(_pred["f1"])
        if basic_qc_more_rels & set(_pred["gold_relations"]):
            basic_qc_more_accumulated["basic_qc"].append(_pred["f1"])
    
    print(f"star_qc_more_accumulated")
    print(f"star_qc_prediction: {len(star_qc_more_accumulated['star_qc'])} {sum(star_qc_more_accumulated['star_qc'])}")
    print(f"basic_qc_prediction: {len(star_qc_more_accumulated['basic_qc'])} {sum(star_qc_more_accumulated['basic_qc'])}")

    print()

    print(f"basic_qc_more_accumulated")
    print(f"star_qc_prediction: {len(basic_qc_more_accumulated['star_qc'])} {sum(basic_qc_more_accumulated['star_qc'])}")
    print(f"basic_qc_prediction: {len(basic_qc_more_accumulated['basic_qc'])} {sum(basic_qc_more_accumulated['basic_qc'])}")

def diff_prediction():
    import math
    star_qc_prediction_map = {
        item["qid"]: item 
        for item in load_json('predictions/webqsp_bert_starQC_0430/debug/results_with_f1.json')
    }
    basic_qc_prediction_map = {
        item["qid"]: item 
        for item in load_json('predictions/webqsp_bert_baseline_0502/debug/results_with_f1.json')
    }

    better_qid_set = set()

    for qid in star_qc_prediction_map:
        if star_qc_prediction_map[qid]["f1"] > basic_qc_prediction_map[qid]["f1"]:
            if math.isclose(star_qc_prediction_map[qid]["f1"], 1.0):
                better_qid_set.add(qid)
    
    print(f"better_qid_set: {len(better_qid_set)} {better_qid_set}")

def case_study():
    webqsp_train = load_json("data/webqsp/origin/WebQSP/data/WebQSP.train.json")
    webqsp_test = load_json("data/webqsp/origin/WebQSP/data/WebQSP.test.json")

    target_rel = "base.biblioness.bibs_location.country"

    train_occurence_qid = set()
    test_occurence_qid = set()
    
    for item in webqsp_train["Questions"]:
        for parse in item["Parses"]:
            if f"ns:{target_rel}" in parse["Sparql"]:
                train_occurence_qid.add(item['QuestionId'])
                break
    
    for item in webqsp_test["Questions"]:
        for parse in item["Parses"]:
            if f"ns:{target_rel}" in parse["Sparql"]:
                test_occurence_qid.add(item['QuestionId'])
                break
    
    print(f"train_occurence: {train_occurence_qid}")
    print(f"test_occurence: {test_occurence_qid}")

def f1_diff():
    import random
    random.seed(374)
    basic_result = load_json("predictions/webqsp_bert_baseline_0502/debug/results_with_f1.json")
    star_result = load_json("predictions/webqsp_bert_starQC_0430/debug/results_with_f1.json")
    basic_f1 = sum([item['f1'] for item in basic_result])
    star_f1 = sum([item['f1'] for item in star_result])
    print(f"summary: basic: {basic_f1}; star: {star_f1}")

    qid_to_basic_result = {item['qid']: item for item in basic_result}
    qid_to_star_result = {item['qid']: item for item in star_result}
    assert len(qid_to_basic_result) == len(qid_to_star_result)
    print(f"result_num: {len(qid_to_basic_result)}")
    star_better_qid = set()
    basic_better_qid = set()
    for qid in qid_to_basic_result:
        if qid_to_basic_result[qid]["f1"] > qid_to_star_result[qid]["f1"]:
            basic_better_qid.add(qid)
        elif qid_to_star_result[qid]["f1"] > qid_to_basic_result[qid]["f1"]:
            star_better_qid.add(qid)
    print(f"star_better_qid: {len(star_better_qid)}")
    print(f"basic_better_qid: {len(basic_better_qid)}")
    print(f"sampled star_better_qid: {random.sample(star_better_qid, 20)}")

if __name__ == "__main__":
    # relation_diff()
    # convert_prediction_format('webqsp_train_basicQC_2024-04-23')
    # webqsp_evaluate_with_record('webqsp_train_basicQC_2024-04-23')
    # star_qc_more_rels = {'location.location.time_zones', 'education.education.institution', 'film.performance.actor', 'people.person.profession', 'tv.regular_tv_appearance.character', 'tv.regular_tv_appearance.actor', 'people.person.education'}
    # basic_qc_more_rels = {'education.education.student', 'film.actor.film', 'education.educational_institution.students_graduates', 'people.profession.people_with_this_profession', 'people.person.date_of_birth', 'time.time_zone.locations_in_this_time_zone', 'award.award_nominee.award_nominations', 'sports.sports_team_roster.player', 'award.award_nomination.nominated_for', 'sports.sports_team.roster', 'location.location.contains'}
    # calculate_accumulated_f1()

    # print(sum(
    #     item['f1'] for item in load_json('predictions/webqsp_bert_starQC_0430/debug/results_with_f1.json')
    # ))

    # print(sum(
    #     item['f1'] for item in load_json('predictions/webqsp_bert_baseline_0502/debug/results_with_f1.json')
    # ))

    # diff_prediction()

    # case_study()
    f1_diff()