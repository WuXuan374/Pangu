from collections import defaultdict
import itertools
import re
import copy
from enum import Enum
from typing import List

class LITERAL_TYPE(Enum):
    TIME = 1
    NUMBER = 2
    STRING = 3 # 普通字面量

DELIMETER = " "
TIME_SUFFIX = [
    '<http://www.w3.org/2001/XMLSchema#date>',
    '<http://www.w3.org/2001/XMLSchema#gYearMonth>', 
    '<http://www.w3.org/2001/XMLSchema#dateTime>', 
    '<http://www.w3.org/2001/XMLSchema#gYear>'
] # GrailQA 中观察得到的

NUMBER_SUFFIX = [
    '<http://www.w3.org/2001/XMLSchema#integer>',
    '<http://www.w3.org/2001/XMLSchema#float>'
] # GrailQA 中观察得到的

def get_literal_type(literal):
    for suffix in TIME_SUFFIX:
        if suffix in literal:
            return LITERAL_TYPE.TIME
    for suffix in NUMBER_SUFFIX:
        if suffix in literal:
            return LITERAL_TYPE.NUMBER
    if re.match("(\".*?\"(@en)?)", literal):
        return LITERAL_TYPE.STRING
    return None

def _linearize_lisp_expression(expression: list, sub_formula_id):
    sub_formulas = []
    for i, e in enumerate(expression):
        if isinstance(e, list) and e[0] != 'R':
            sub_formulas.extend(_linearize_lisp_expression(e, sub_formula_id))
            expression[i] = '#' + str(sub_formula_id[0] - 1)

    sub_formulas.append(expression)
    sub_formula_id[0] += 1
    return sub_formulas

def lisp_to_nested_expression(lisp_string: str) -> List:
    """
    Takes a logical form as a lisp string and returns a nested list representation of the lisp.
    For example, "(count (division first))" would get mapped to ['count', ['division', 'first']].
    """
    stack: List = []
    current_expression: List = []
    tokens = lisp_string.split()
    for token in tokens:
        while token[0] == '(':
            nested_expression: List = []
            current_expression.append(nested_expression)
            stack.append(current_expression)
            current_expression = nested_expression
            token = token[1:]
        current_expression.append(token.replace(')', ''))
        while token[-1] == ')':
            current_expression = stack.pop()
            token = token[:-1]
    return current_expression[0]

class SYMBOL_TYPE(Enum):
    ENTITY = 1
    LITERAL = 2
    CLASS = 3 # 普通字面量
    RELATION = 4

class ComponentBasedEquivalenceChecker(object):
    def __init__(
        self, 
        logger,
        reverse_property_path="ontology/reverse_properties"
    ):
        '''默认会处理逆关系'''
        self.logger = logger
        self.reverse_properties = dict()
        with open(reverse_property_path, 'r') as f:
            for line in f:
                self.reverse_properties[line.split('\t')[0]] = line.split('\t')[1].replace('\n', '')
    
    @classmethod
    def instance(cls, *args, **kwargs):
        '''单例模式'''
        if not hasattr(ComponentBasedEquivalenceChecker, "_instance"):
            ComponentBasedEquivalenceChecker._instance = ComponentBasedEquivalenceChecker(*args, **kwargs)
        return ComponentBasedEquivalenceChecker._instance

    def process_literal(self, literal):
        '''新旧 S-expression 中的 literal 可能存在格式差别，对此我们做个替换（旧的格式改成新的）'''
        if "^^http://www.w3.org/2001/XMLSchema" in literal:
            data_type = literal.split("^^")[1].split("#")[1]
            if data_type in ['date', 'gYearMonth', 'gYear']:
                return f'"{literal.split("^^")[0] + "-08:00"}"^^<{literal.split("^^")[1]}>'
            else:
                return f'"{literal.split("^^")[0]}"^^<{literal.split("^^")[1]}>'
        elif literal.endswith("@en"):
            return literal
        elif literal.startswith('"') and literal.endswith('"'):
            return f"{literal}@en" 
        else:
            try:
                value = float(literal)
                return f'"{value}"^^<http://www.w3.org/2001/XMLSchema#float>'
            except:
                return literal

    def _equivalent_logical_form(self, sexp1, sexp2):
        '''
        @return equivalence: bool, 等价查询
        @return component_set1
        @return component_set2
        '''
        sexp1 = self.sexp_pre_process(sexp1)
        sexp1 = lisp_to_nested_expression(sexp1)
        linear_sexp1 = _linearize_lisp_expression(sexp1, [0])
        component_dict1 = self.logical_form_to_component_set(linear_sexp1) # {key: list}
        final_component_key1 = max(list(component_dict1.keys()))
        final_component_set1 = set(component_dict1[final_component_key1])
        sub_component_set1 = set()
        # 特判: 如果只有一个成分，那么子成分也包含 final_component
        for (key, lst) in component_dict1.items():
            if key != final_component_key1:
                sub_component_set1.update(lst)
            else: # key == final_component_key1
                if len(component_dict1) <= 1:
                    sub_component_set1.update(lst)
                elif not component_dict1[key][0].startswith('AND'):
                    sub_component_set1.update(lst)

        sexp2 = self.sexp_pre_process(sexp2)
        sexp2 = lisp_to_nested_expression(sexp2)
        linear_sexp2 = _linearize_lisp_expression(sexp2, [0])
        component_dict2 = self.logical_form_to_component_set(linear_sexp2)
        final_component_key2 = max(list(component_dict2.keys()))
        final_component_set2 = set(component_dict2[final_component_key2])
        sub_component_set2 = set()
        for (key, lst) in component_dict2.items():
            if key != final_component_key2:
                sub_component_set2.update(lst)
            else: # key == final_component_key1
                if len(component_dict2) <= 1:
                    sub_component_set1.update(lst)
                elif not component_dict2[key][0].startswith('AND'):
                    sub_component_set1.update(lst)
        return final_component_set1 == final_component_set2, sub_component_set1, sub_component_set2, component_dict1, component_dict2
    
    def equivalent_logical_form(self, sexp1, sexp2):
        equivalence, sub_component_set1, sub_component_set2, component_dict1, component_dict2 = self._equivalent_logical_form(sexp1, sexp2)
        semantic_equivalence = equivalence
        
        '''
        如果只差一个 type.object.type 指向的类型，我们就认为其是语义等价的
        形如: JOIN type.object.type {class}
        '''
        if sub_component_set1.issubset(sub_component_set2):
            diff = sub_component_set2 - sub_component_set1
            if len(diff) == 1:
                sub_program = list(diff)[0]
                clauses = sub_program.split()
                if len(clauses) == 3:
                    if clauses[0] == 'JOIN' and clauses[1] == 'type.object.type':
                        semantic_equivalence = True
        
        elif sub_component_set2.issubset(sub_component_set1):
            diff = sub_component_set1 - sub_component_set2
            if len(diff) == 1:
                sub_program = list(diff)[0]
                clauses = sub_program.split()
                if len(clauses) == 3:
                    if clauses[0] == 'JOIN' and clauses[1] == 'type.object.type':
                        semantic_equivalence = True
        
        all_components_set1 = set()
        all_components_set2 = set()
        for (_, lst) in component_dict1.items():
            all_components_set1.update(lst)
        for (_, lst) in component_dict2.items():
            all_components_set2.update(lst)

        return equivalence, semantic_equivalence, all_components_set1 & all_components_set2
    


    def sexp_pre_process(self, sexp):
        '''
        旧版的 Sexp 中，AND 和 ARGMAX / ARGMIN 后面可能跟着一个 class, 这里做个处理
        '''
        new_tokens = list()
        sexp = sexp.replace('(', ' ( ')
        sexp = sexp.replace(')', ' ) ')
        tokens = sexp.split()
        tokens = [x for x in tokens if len(x)]
        i = 0
        while i < len(tokens):
            tok = tokens[i]
            tok = tok.strip()
            try:
                if tok in ['AND', 'ARGMIN', 'ARGMAX']:
                    if self.get_symbol_type(tokens[i+1]) == SYMBOL_TYPE.CLASS:
                        new_tokens.append(tok)
                        new_tokens.extend(['(', 'JOIN', 'type.object.type', tokens[i+1], ')'])
                        i += 2
                        continue
            except:
                pass
            new_tokens.append(tok)
            i += 1
        
        new_sexp = ""
        for (idx, tok) in enumerate(new_tokens):
            if idx == 0 or (new_tokens[idx-1] == '(') or (tok == ')'):
                new_sexp = f"{new_sexp}{tok}"
            else:
                new_sexp = f"{new_sexp} {tok}"
        return new_sexp


    def logical_form_to_component_set(self, linear_sexp):
        sub_component_dict = defaultdict(list) # 每个 sub program 对应的子成分，{i: list()}
        and_component_dict = dict() # 特判，AND 操作符所对应的子成分（嵌套情况下放在同一层）
        for (i, subp) in enumerate(linear_sexp):
            if subp[0] == 'JOIN':
                '''
                sub[1]:
                - relation
                - R relation
                '''
                sub_component_str_list = list() # 子成分，序列化之后的表示
                sub_component_str_list.append([subp[0]])
                
                if isinstance(subp[1], list): # R relation
                    if len(subp[1]) != 2:
                        raise Exception(f"R relation: subp[1]: {subp[1]}; linear_sexp: {linear_sexp}")
                    rel = subp[1][1]
                    if rel in self.reverse_properties:
                        component_str = self.reverse_properties[rel]
                    else:
                        component_str = DELIMETER.join([subp[1][0], rel]) # subp[1][0]: R
                elif self.get_symbol_type(subp[1]) == SYMBOL_TYPE.RELATION: # relation
                    component_str = subp[1]
                else:
                    raise Exception(f"JOIN, subp[1]: {subp[1]}")
                sub_component_str_list.append([component_str])
                
                '''
                subp[2]:
                - #n
                - entity, class, literal
                - relation, R relation (跟在 ARGMIN / ARGMAX 之后的话)
                '''
                if subp[2][0] == '#': # sub component
                    sub_component_idx = int(subp[2][1:])
                    # JOIN + AND 的特判，会把 JOIN 的内容添加到 AND 的子成分中
                    if sub_component_idx in and_component_dict:
                        if len(sub_component_str_list[0]) == 1 and len(sub_component_str_list[1]) == 1:
                            join_str = DELIMETER.join([sub_component_str_list[0][0], sub_component_str_list[1][0]])
                        else:
                            raise Exception(f"JOIN, sub_component_str_list: {sub_component_str_list}")
                        and_str_list = list()
                        tmp = copy.deepcopy(and_component_dict[sub_component_idx])
                        for original_str in tmp:
                            # 把 JOIN 的内容添加到 AND 的子成分中
                            and_str_list.append(DELIMETER.join([join_str, original_str]))
                        and_component_dict.pop(sub_component_idx)
                        and_component_dict[i] = and_str_list
                        sub_component_str_list.append(tmp) # 仍然要把这些 JOIN 子成分，加入集合中
                    elif sub_component_idx in sub_component_dict:
                        sub_component_str_list.append(sub_component_dict[sub_component_idx])
                    else:
                        raise Exception(f"JOIN: subp[2]: {subp[2]}; linear_sexp: {linear_sexp}")
                    
                    
                elif isinstance(subp[2], list): # R relation
                    if len(subp[2]) != 2:
                        raise Exception(f"R relation: subp[2]: {subp[2]}; linear_sexp: {linear_sexp}")
                    rel = subp[2][1]
                    if rel in self.reverse_properties:
                        component_str = self.reverse_properties[rel]
                    else:
                        component_str = DELIMETER.join([subp[2][0], rel]) # subp[2][0]: R
                    sub_component_str_list.append([component_str])
                else:
                    symbol_type = self.get_symbol_type(subp[2])
                    if symbol_type in [SYMBOL_TYPE.ENTITY, SYMBOL_TYPE.CLASS]: # entity / class
                        sub_component_str_list.append([subp[2]])
                    elif symbol_type in [SYMBOL_TYPE.LITERAL]:
                        sub_component_str_list.append(
                            [self.process_literal(subp[2])]
                        )
                    elif symbol_type == SYMBOL_TYPE.RELATION:
                        sub_component_str_list.append([subp[2]])
                    else:
                        raise Exception(f"JOIN, subp[2]: {subp[2]}")

                for tup in itertools.product(*sub_component_str_list):
                    sub_component_dict[i].append(DELIMETER.join(tup))

            elif subp[0] in [
                'EQ', 'GE', 'GT', 'LE', 'LT',
                'ge', 'gt', 'le', 'lt'
            ]:
                '''
                subp[1]:
                - #n
                - relation, R relation
                
                subp[2]
                - #n
                - time / number
                '''
                sub_component_str_list = list()
                sub_component_str_list.append([self.map_operator(subp[0])])
                if subp[1][0] == '#':
                    sub_component_idx = int(subp[1][1:])
                    if sub_component_idx in and_component_dict:
                        and_str_list = list()
                        tmp = and_component_dict[sub_component_idx]
                        for tup in itertools.permutations(tmp, len(tmp)):
                            and_str_list.append(DELIMETER.join(['AND'] + list(tup)))
                        and_component_dict.pop(sub_component_idx)
                        sub_component_str_list.append(and_str_list)
                    elif sub_component_idx in sub_component_dict:
                        sub_component_str_list.append(sub_component_dict[sub_component_idx])
                    else:
                        raise Exception(f"{subp[0]}: subp[1]: {subp[1]}; linear_sexp: {linear_sexp}")
                    
                elif isinstance(subp[1], list): # R relation
                    if len(subp[1]) != 2:
                        raise Exception(f"R relation: subp[1]: {subp[1]}; linear_sexp: {linear_sexp}")
                    rel = subp[1][1]
                    if rel in self.reverse_properties:
                        component_str = self.reverse_properties[rel]
                    else:
                        component_str = DELIMETER.join([subp[1][0], rel]) # subp[1][0]: R
                    sub_component_str_list.append([component_str])
                elif self.get_symbol_type(subp[1]) == SYMBOL_TYPE.RELATION: # relation
                    sub_component_str_list.append([subp[1]])
                else:
                    raise Exception(f"JOIN, subp[1]: {subp[1]}")
            
                if subp[2][0] == '#':
                    sub_component_idx = int(subp[2][1:])
                    if sub_component_idx in and_component_dict:
                        and_str_list = list()
                        tmp = and_component_dict[sub_component_idx]
                        for tup in itertools.permutations(tmp, len(tmp)):
                            and_str_list.append(DELIMETER.join(['AND'] + list(tup)))
                        and_component_dict.pop(sub_component_idx)
                        sub_component_str_list.append(and_str_list)
                    elif sub_component_idx in sub_component_dict:
                        sub_component_str_list.append(sub_component_dict[sub_component_idx])
                    else:
                        raise Exception(f"{subp[0]}: subp[2]: {subp[2]}; linear_sexp: {linear_sexp}")

                elif self.get_symbol_type(subp[2]) == SYMBOL_TYPE.LITERAL:
                    sub_component_str_list.append(
                        [self.process_literal(subp[2])]
                    )
                for tup in itertools.product(*sub_component_str_list):
                    sub_component_dict[i].append(DELIMETER.join(tup))

            elif subp[0] == 'AND':
                '''
                将子成分加入 and_component_dict
                递归地，通过 AND 多层嵌套的子成分平级加入 and_component_dict
                '''
                if (subp[1][0] == '#') and (subp[2][0] == '#'):
                    subp1_idx = int(subp[1][1:])
                    subp2_idx = int(subp[2][1:])

                    sub_component_str_list = list()
                    if subp1_idx in and_component_dict:
                        sub_component_str_list.extend(and_component_dict[subp1_idx])
                        and_component_dict.pop(subp1_idx)
                    else:
                        sub_component_str_list.extend(sub_component_dict[subp1_idx])
                    if subp2_idx in and_component_dict:
                        sub_component_str_list.extend(and_component_dict[subp2_idx])
                        and_component_dict.pop(subp2_idx)
                    else:
                        sub_component_str_list.extend(sub_component_dict[subp2_idx])
                    and_component_dict[i] = sub_component_str_list
                elif (self.get_symbol_type(subp[1]) == SYMBOL_TYPE.CLASS) and (subp[2][0] == '#'):
                    # 特判，AND 后面可以紧跟一个 class
                    sub_component_str_list.append(DELIMETER.join(['JOIN', 'type.object.type', subp[1]]))
                    subp2_idx = int(subp[2][1:])
                    if subp2_idx in and_component_dict:
                        sub_component_str_list.extend(and_component_dict[subp2_idx])
                        and_component_dict.pop(subp2_idx)
                    else:
                        sub_component_str_list.extend(sub_component_dict[subp2_idx])

                    and_component_dict[i] = sub_component_str_list
                else:
                    raise Exception(f"AND; subp:{subp}; linear_sexp:{linear_sexp}")
            
            elif subp[0] in ['ARGMIN', 'ARGMAX']:
                '''
                subp[1]: 
                - #n
                - (针对旧版的适配) class
                subp[2]:
                    - relation
                    - R relation
                    - #n (只可能是多跳关系)
                '''
                sub_component_str_list = list()
                sub_component_str_list.append([subp[0]])

                if subp[1][0] == '#':
                    subp1_idx = int(subp[1][1:])
                    if subp1_idx in and_component_dict:
                        and_str_list = list()
                        tmp = and_component_dict[subp1_idx]
                        for tup in itertools.permutations(tmp, len(tmp)):
                            and_str_list.append(DELIMETER.join(['AND'] + list(tup)))
                        and_component_dict.pop(subp1_idx)
                        sub_component_str_list.append(and_str_list)
                    elif subp1_idx in sub_component_dict:
                        sub_component_str_list.append(sub_component_dict[subp1_idx])
                    else:
                        raise Exception(f"{subp[0]}: subp[2]: {subp[1]}; linear_sexp: {linear_sexp}")               
                elif self.get_symbol_type(subp[1]) == SYMBOL_TYPE.CLASS:
                    sub_component_str_list.append(
                        [DELIMETER.join(['JOIN', 'type.object.type', subp[1]])]
                    )
                else:
                    raise Exception(f"ARG; subp:{subp}; linear_sexp:{linear_sexp}")

                if subp[2][0] == '#':
                    subp2_idx = int(subp[2][1:])
                    if subp2_idx in and_component_dict:
                        and_str_list = list()
                        tmp = and_component_dict[subp2_idx]
                        for tup in itertools.permutations(tmp, len(tmp)):
                            and_str_list.append(DELIMETER.join(['AND'] + list(tup)))
                        and_component_dict.pop(subp2_idx)
                        sub_component_str_list.append(and_str_list)
                    elif subp2_idx in sub_component_dict:
                        sub_component_str_list.append(sub_component_dict[subp2_idx])
                    else:
                        raise Exception(f"{subp[0]}: subp[2]: {subp[2]}; linear_sexp: {linear_sexp}") 

                elif isinstance(subp[2], list): # R relation
                    if len(subp[2]) != 2:
                        raise Exception(f"R relation: subp[2]: {subp[2]}; ARG; subp:{subp}; linear_sexp: {linear_sexp}")
                    rel = subp[2][1]
                    if rel in self.reverse_properties:
                        component_str = self.reverse_properties[rel]
                    else:
                        component_str = DELIMETER.join([subp[2][0], rel])
                    sub_component_str_list.append([component_str])
                elif self.get_symbol_type(subp[2]) == SYMBOL_TYPE.RELATION: # relation
                    sub_component_str_list.append([subp[2]])
                else:
                    raise Exception(f"ARG, subp[2]: {subp[2]}; subp: {subp}; linear_sexp: {linear_sexp}")

                for tup in itertools.product(*sub_component_str_list):
                    sub_component_dict[i].append(DELIMETER.join(tup))
            
            elif subp[0] == 'COUNT':
                '''
                subp[1]: #n
                '''
                sub_component_str_list = list()
                sub_component_str_list.append([subp[0]])

                if subp[1][0] == '#':
                    subp1_idx = int(subp[1][1:])
                    if subp1_idx in and_component_dict:
                        and_str_list = list()
                        tmp = and_component_dict[subp1_idx]
                        for tup in itertools.permutations(tmp, len(tmp)):
                            and_str_list.append(DELIMETER.join(['AND'] + list(tup)))
                        and_component_dict.pop(subp1_idx)
                        sub_component_str_list.append(and_str_list)
                    elif subp1_idx in sub_component_dict:
                        sub_component_str_list.append(sub_component_dict[subp1_idx])
                    else:
                        raise Exception(f"{subp[0]}: subp[1]: {subp[1]}; linear_sexp: {linear_sexp}") 
                else:
                    raise Exception(f"COUNT; subp:{subp}; linear_sexp:{linear_sexp}")

                for tup in itertools.product(*sub_component_str_list):
                    sub_component_dict[i].append(DELIMETER.join(tup))
            elif subp[0] == 'TC':
                '''
                subp[1]: #n
                subp[2]: 
                - #n (复合关系)
                - R relation
                - relation
                subp[3]:
                - literal
                '''
                sub_component_str_list = list()
                sub_component_str_list.append([subp[0]])

                if subp[1][0] == '#':
                    subp1_idx = int(subp[1][1:])
                    if subp1_idx in and_component_dict:
                        and_str_list = list()
                        tmp = and_component_dict[subp1_idx]
                        for tup in itertools.permutations(tmp, len(tmp)):
                            and_str_list.append(DELIMETER.join(['AND'] + list(tup)))
                        and_component_dict.pop(subp1_idx)
                        sub_component_str_list.append(and_str_list)
                    elif subp1_idx in sub_component_dict:
                        sub_component_str_list.append(sub_component_dict[subp1_idx])
                    else:
                        raise Exception(f"{subp[0]}: subp[1]: {subp[1]}; linear_sexp: {linear_sexp}") 
                else:
                    raise Exception(f"TC; subp:{subp}; linear_sexp:{linear_sexp}")

                if subp[2][0] == '#':
                    subp2_idx = int(subp[2][1:])
                    # 只可能是复合关系，不可能是 AND clause
                    if subp2_idx in sub_component_dict:
                        sub_component_str_list.append(sub_component_dict[subp2_idx])
                    else:
                        raise Exception(f"TC; subp[2]:{subp[2]}; linear_sexp:{linear_sexp}")

                elif isinstance(subp[2], list): # R relation
                    if len(subp[2]) != 2:
                        raise Exception(f"R relation: subp[2]: {subp[2]}; TC subp:{subp}; linear_sexp: {linear_sexp}")
                    rel = subp[2][1]
                    if rel in self.reverse_properties:
                        component_str = self.reverse_properties[rel]
                    else:
                        component_str = DELIMETER.join([subp[2][0], rel])
                    sub_component_str_list.append([component_str])
                elif self.get_symbol_type(subp[2]) == SYMBOL_TYPE.RELATION: # relation
                    sub_component_str_list.append([subp[2]])
                else:
                    raise Exception(f"TC; subp:{subp}; linear_sexp:{linear_sexp}")

                if self.get_symbol_type(subp[3]) == SYMBOL_TYPE.LITERAL:
                    sub_component_str_list.append([subp[3]])
                else:
                    raise Exception(f"TC; subp:{subp}; linear_sexp:{linear_sexp}")
                
                for tup in itertools.product(*sub_component_str_list):
                    sub_component_dict[i].append(DELIMETER.join(tup))

            else:
                raise NotImplementedError(f"subp: {subp}; linear_sexp:{linear_sexp}")

        # 有可能最外层是一个 AND, 那么需要把这个 AND 对应的子成分做个排列
        if len(and_component_dict) == 1:
            key = list(and_component_dict.keys())[0]
            and_str_list = list()
            tmp = and_component_dict[key]
            for tup in itertools.permutations(tmp, len(tmp)):
                and_str_list.append(DELIMETER.join(['AND'] + list(tup)))
            and_component_dict.pop(key)
            new_idx = max(list(sub_component_dict.keys())) + 1
            sub_component_dict[new_idx] = and_str_list
        elif len(and_component_dict) > 1:
            raise Exception(f"and_component_dict: {and_component_dict}; linear_sexp:{linear_sexp}")

        return sub_component_dict

    def map_operator(self, operator):
        operator_dict = {
            "EQ": "JOIN",
            "ge": "GE",
            'gt': 'GT',
            "le": "LE",
            "lt": "LT"
        }
        if operator in operator_dict:
            return operator_dict[operator]
        else:
            return operator

    def get_symbol_type(self, symbol: str) -> SYMBOL_TYPE:
        """
        适配两种版本 S-expression 的元素类型判断
        """
        if symbol.startswith('m.') or symbol.startswith('g.'):
            return SYMBOL_TYPE.ENTITY
        elif re.fullmatch("[a-zA-Z_]+\.[a-zA-Z_]+", symbol):
            return SYMBOL_TYPE.CLASS
        elif 'http://www.w3.org/2001/XMLSchema' in symbol:
            return SYMBOL_TYPE.LITERAL
        elif symbol.startswith('"') and symbol.endswith('"'):
            return SYMBOL_TYPE.LITERAL
        elif re.fullmatch('".+"@.+', symbol): 
            return SYMBOL_TYPE.LITERAL
        elif symbol == 'NOW':
            return SYMBOL_TYPE.LITERAL
        elif re.fullmatch("[a-zA-Z_]+\.[a-zA-Z_]+\.[a-zA-z_]+", symbol) or re.fullmatch("[a-zA-Z_]+\.[a-zA-Z_]+\.[a-zA-z_]+\.[a-zA-z_]+", symbol) or re.fullmatch("[a-zA-Z_]+\.[a-zA-Z_]+\.[a-zA-z_]+\.[a-zA-z_]+\.[a-zA-z_]+", symbol):
            return SYMBOL_TYPE.RELATION
        else:
            try:
                float(symbol)
                return SYMBOL_TYPE.LITERAL # literal
            except:
                raise NotImplementedError(f"symbol: {symbol}")