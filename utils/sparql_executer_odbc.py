"""
SparqlWrapper 经常报 502 错误，难以确认是 SparalWrapper 的通病 还是 特殊现象
为了更公平地对比，改用 odbc 查询
但是 ODBC 也存在 Literal 的返回格式有点特殊的问题，只能说没有啥两全其美的方法
"""
import pyodbc
import logging
from pathlib import Path
from typing import List

odbc_connection = pyodbc.connect(
    'DRIVER=/data/virtuoso/virtuoso-opensource/lib/virtodbc.so;Host=114.212.81.217:18896;UID=dba;PWD=dba'
)
odbc_connection.setdecoding(pyodbc.SQL_CHAR, encoding='utf8')
odbc_connection.setdecoding(pyodbc.SQL_WCHAR, encoding='utf8')
odbc_connection.setencoding(encoding='utf8')
odbc_connection.timeout = 60 # 和我们这边实验的默认参数保持一致
ODBC_PREFIX = "SPARQL PREFIX ns: <http://rdf.freebase.com/ns/> "

logger = logging.getLogger(__name__)
path = str(Path(__file__).parent.absolute())

with open(path + '/../ontology/fb_roles', 'r') as f:
    contents = f.readlines()

roles = set()
for line in contents:
    fields = line.split()
    roles.add(fields[1])

def execute_query(query: str):
    rtn = []
    try:
        query = f"{ODBC_PREFIX} {query}"
        with odbc_connection.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
    except BaseException as e:
        logger.error(f"Query {query} failed; Exception: {e}")
        return rtn # 出错则默认返回空结果
    
    for row in rows:
        rtn.append(row[0].replace('http://rdf.freebase.com/ns/', '').replace("-08:00", ''))

    return rtn

def is_intersectant(derivation1: tuple, derivation2: str):
    if len(derivation1[1]) > 3 or len(derivation2[1]) > 3:
        return False

    if len(derivation1) == 2:
        clause1 = derivation1[0] + ' ' + ' / '.join(derivation1[1]) + ' ?x. \n'
    elif len(derivation1) == 3:
        clause1 = '?y ' + ' / '.join(derivation1[1]) + ' ?x. \n' + f'FILTER (?y {derivation1[2]} {derivation1[0]}) . \n'

    if len(derivation2) == 2:
        clause2 = derivation2[0] + ' ' + ' / '.join(derivation2[1]) + ' ?x. \n'
    elif len(derivation2) == 3:
        clause2 = '?y ' + ' / '.join(derivation2[1]) + ' ?x. \n' + f'FILTER (?y {derivation2[2]} {derivation2[0]}) . \n'

    query = ("""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX : <http://rdf.freebase.com/ns/> 
        ASK {
        """
             + clause1
             + clause2 +
             """
}
""")
    # print(query)
    try:
        query = f"{ODBC_PREFIX} {query}"
        with odbc_connection.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
    except BaseException as e:
        logger.error(f"Query {query} failed; Exception: {e}")
        return False # 出错则默认返回空结果
    if len(rows) > 0 and rows[0][0] == 1:
        return True
    return False

def is_reachable(derivation: tuple, answer_type: str):
    if len(derivation[1]) > 3:
        return False

    query = ("""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX : <http://rdf.freebase.com/ns/> 
        ASK {
        """
             + derivation[0] + ' ' + ' / '.join(derivation[1]) + '/ :type.object.type :' + answer_type +
             """
}
""")
    # print(query)
    try:
        query = f"{ODBC_PREFIX} {query}"
        with odbc_connection.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
    except BaseException as e:
        logger.error(f"Query {query} failed; Exception: {e}")
        return False # 出错则默认返回空结果
    if len(rows) > 0 and rows[0][0] == 1:
        return True
    return False

def is_reachable_cmp(derivation: tuple, answer_type: str):
    if len(derivation[1]) > 3:
        return False

    query = ("""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX : <http://rdf.freebase.com/ns/> 
        ASK {
        """
             + '?x ' + ' / '.join(derivation[1]) + '/ :type.object.type :' + answer_type + ' .\n'
             + f'FILTER (?x {derivation[2]} {derivation[0]})'
               """
}
""")
    # print(query)
    try:
        query = f"{ODBC_PREFIX} {query}"
        with odbc_connection.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
    except Exception as e:
        logger.error(f"Query {query} failed; Exception: {e}")
        logger.error(f"")
        return False # 出错则默认返回空结果
    if len(rows) > 0 and rows[0][0] == 1:
        return True
    return False

def get_types(entity: str) -> List[str]:
    query = ("""
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX : <http://rdf.freebase.com/ns/> 
    SELECT (?x0 AS ?value) WHERE {
    SELECT DISTINCT ?x0  WHERE {
    """
             ':' + entity + ' :type.object.type ?x0 . '
                            """
    }
    }
    """)
    # print(query)
    rtn = []
    try:
        query = f"{ODBC_PREFIX} {query}"
        with odbc_connection.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
    except BaseException as e:
        logger.error(f"Query {query} failed; Exception: {e}")
        return rtn # 出错则默认返回空结果

    for row in rows:
        rtn.append(row[0].replace('http://rdf.freebase.com/ns/', ''))

    return rtn

def get_notable_type(entity: str):
    query = ("""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX : <http://rdf.freebase.com/ns/> 
        SELECT (?x0 AS ?value) WHERE {
        SELECT DISTINCT ?x0  WHERE {

        """
             ':' + entity + ' :common.topic.notable_types ?y . '
                            """
        ?y :type.object.name ?x0
        FILTER (lang(?x0) = 'en')
    }
    }
    """)

    # print(query)
    rtn = []
    try:
        query = f"{ODBC_PREFIX} {query}"
        with odbc_connection.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
    except BaseException as e:
        logger.error(f"Query {query} failed; Exception: {e}")
        return rtn # 出错则默认返回空结果
    
    for row in rows:
        rtn.append(row[0])

    if len(rtn) == 0:
        rtn = ['entity']

    return rtn

def get_in_attributes(value: str):
    in_attributes = set()

    query1 = ("""
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX : <http://rdf.freebase.com/ns/> 
                SELECT (?x0 AS ?value) WHERE {
                SELECT DISTINCT ?x0  WHERE {
                """
              '?x1 ?x0 ' + value + '. '
                                   """
    FILTER regex(?x0, "http://rdf.freebase.com/ns/")
    }
    }
    """)
    try:
        query1 = f"{ODBC_PREFIX} {query1}"
        with odbc_connection.cursor() as cursor:
            cursor.execute(query1)
            rows = cursor.fetchall()
    except Exception as e:
        logger.error(f"Query {query1} failed; Exception: {e}")
        return in_attributes # 出错则默认返回空结果
    for row in rows:
        in_attributes.add(row[0].replace('http://rdf.freebase.com/ns/', ''))

    return in_attributes

def get_in_relations(entity: str):
    in_relations = set()

    query1 = ("""
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX : <http://rdf.freebase.com/ns/> 
            SELECT (?x0 AS ?value) WHERE {
            SELECT DISTINCT ?x0  WHERE {
            """
              '?x1 ?x0 ' + ':' + entity + '. '
                                          """
     FILTER regex(?x0, "http://rdf.freebase.com/ns/")
     }
     }
     """)
    try:
        query1 = f"{ODBC_PREFIX} {query1}"
        with odbc_connection.cursor() as cursor:
            cursor.execute(query1)
            rows = cursor.fetchall()
    except Exception as e:
        logger.error(f"Query {query1} failed; Exception: {e}")
        return in_relations # 出错则默认返回空结果
    for row in rows:
        in_relations.add(row[0].replace('http://rdf.freebase.com/ns/', ''))

    return in_relations

def get_in_entities(entity: str, relation: str):
    neighbors = set()

    query1 = ("""
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX : <http://rdf.freebase.com/ns/> 
            SELECT (?x1 AS ?value) WHERE {
            SELECT DISTINCT ?x1  WHERE {
            """
              '?x1' + ' :' + relation + ' :' + entity + '. '
                                                        """
                   FILTER regex(?x1, "http://rdf.freebase.com/ns/")
                   }
                   }
                   """)
    try:
        query1 = f"{ODBC_PREFIX} {query1}"
        with odbc_connection.cursor() as cursor:
            cursor.execute(query1)
            rows = cursor.fetchall()
    except Exception as e:
        logger.error(f"Query {query1} failed; Exception: {e}")
        return neighbors # 出错则默认返回空结果
    for row in rows:
        neighbors.add(row[0].replace('http://rdf.freebase.com/ns/', ''))

    return neighbors

def get_in_entities_for_literal(value: str, relation: str):
    neighbors = set()

    query1 = ("""
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX : <http://rdf.freebase.com/ns/> 
            SELECT (?x1 AS ?value) WHERE {
            SELECT DISTINCT ?x1  WHERE {
            """
              '?x1' + ':' + relation + ' ' + value + '. '
                                                     """
                FILTER regex(?x1, "http://rdf.freebase.com/ns/")
                }
                }
                """)

    try:
        query1 = f"{ODBC_PREFIX} {query1}"
        with odbc_connection.cursor() as cursor:
            cursor.execute(query1)
            rows = cursor.fetchall()
    except Exception as e:
        logger.error(f"Query {query1} failed; Exception: {e}")
        return neighbors # 出错则默认返回空结果
    for row in rows:
        neighbors.add(row[0].replace('http://rdf.freebase.com/ns/', ''))

    return neighbors

def get_out_relations(entity: str):
    out_relations = set()

    query2 = ("""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX : <http://rdf.freebase.com/ns/> 
        SELECT (?x0 AS ?value) WHERE {
        SELECT DISTINCT ?x0  WHERE {
        """
              ':' + entity + ' ?x0 ?x1 . '
                             """
    FILTER regex(?x0, "http://rdf.freebase.com/ns/")
    }
    }
    """)
    try:
        query2 = f"{ODBC_PREFIX} {query2}"
        with odbc_connection.cursor() as cursor:
            cursor.execute(query2)
            rows = cursor.fetchall()
    except Exception as e:
        logger.error(f"Query {query2} failed; Exception: {e}")
        return out_relations # 出错则默认返回空结果
    for row in rows:
        out_relations.add(row[0].replace('http://rdf.freebase.com/ns/', ''))

    return out_relations

def get_out_entities(entity: str, relation: str):
    neighbors = set()

    query2 = ("""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX : <http://rdf.freebase.com/ns/> 
        SELECT (?x1 AS ?value) WHERE {
        SELECT DISTINCT ?x1  WHERE {
        """
              ':' + entity + ' :' + relation + ' ?x1 . '
                                               """
                      FILTER regex(?x1, "http://rdf.freebase.com/ns/")
                      }
                      }
                      """)
    # print(query2)

    try:
        query2 = f"{ODBC_PREFIX} {query2}"
        with odbc_connection.cursor() as cursor:
            cursor.execute(query2)
            rows = cursor.fetchall()
    except Exception as e:
        logger.error(f"Query {query2} failed; Exception: {e}")
        return neighbors # 出错则默认返回空结果
    for row in rows:
        neighbors.add(row[0].replace('http://rdf.freebase.com/ns/', ''))

    return neighbors

def get_entities_cmp(value, relation: str, cmp: str):
    neighbors = set()

    query2 = ("""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX : <http://rdf.freebase.com/ns/> 
        SELECT (?x1 AS ?value) WHERE {
        SELECT DISTINCT ?x1  WHERE {
        """
              '?x1' + ':' + relation + ' ?sk0 . '
                                       """
              FILTER regex(?x1, "http://rdf.freebase.com/ns/")
              """
                                       f'FILTER (?sk0 {cmp} {value})'
                                       """
                                       }
                                       }
                                       """)
    try:
        query2 = f"{ODBC_PREFIX} {query2}"
        with odbc_connection.cursor() as cursor:
            cursor.execute(query2)
            rows = cursor.fetchall()
    except Exception as e:
        logger.error(f"Query {query2} failed; Exception: {e}")
        return neighbors # 出错则默认返回空结果
    for row in rows:
        neighbors.add(row[0].replace('http://rdf.freebase.com/ns/', ''))

    return neighbors
