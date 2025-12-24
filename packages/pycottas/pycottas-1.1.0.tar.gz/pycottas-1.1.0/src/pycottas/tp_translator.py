__author__ = "Julián Arenas-Guerrero"
__credits__ = ["Julián Arenas-Guerrero"]

__license__ = "Apache-2.0"
__maintainer__ = "Julián Arenas-Guerrero"
__email__ = "julian.arenas.guerrero@upm.es"


from.constants import i_pos


def _parse_tp(tp_str):
    #statement = "Select ?s ?p ?o where {?s ?p ?o.}"
    #query_tree = parser.parseQuery(statement)
    #q_algebra = algebra.translateQuery(query_tree)
    #algebra.pprintAlgebra(q_algebra)

    splitted_tp_str = tp_str.split()
    s_term = splitted_tp_str[0]
    p_term = splitted_tp_str[1]
    o_term = tp_str.replace(s_term, '', 1).replace(p_term, '', 1).strip()
    g_term = None

    # check whether it is a quad pattern
    if ' <' in o_term:
        splitted_o_term = o_term.split()
        g_term = splitted_o_term[len(splitted_o_term)-1].strip()
        o_term = o_term.replace(g_term, '').strip()

    if g_term:
        return [s_term, p_term, o_term, g_term]
    else:
        return [s_term, p_term, o_term]


def translate_triple_pattern(cottas_file, tp, limit=None, offset=None):
    """
    Given a COTTAS file and a user-defined triple pattern, translate the triple pattern to an SQL query over COTTAS.

    :param cottas_file: path to a COTTAS file
    :param tp: a user-defined triple pattern
    :return: SQL query for the triple pattern
    """

    if type(tp) is str:
        tp_tuple = _parse_tp(tp)
    else:
        tp_aux = []
        for i in range(len(tp)):
            if tp[i] is None:
                tp_aux.append(f"?{i_pos[i]}")
            else:
                tp_aux.append(tp[i].n3())
        tp_tuple = tp_aux

    if len(tp_tuple) == 3:
        tp_query = f"SELECT s, p, o FROM PARQUET_SCAN('{cottas_file}') WHERE "
    elif len(tp_tuple) == 4:
        tp_query = f"SELECT s, p, o, g FROM PARQUET_SCAN('{cottas_file}') WHERE "
    else:
        raise TypeError("The pattern must be a tuple of length 3 (triple) or 4 (quad).")

    # build selection iterating over all positions in the triple pattern
    for i in range(4):
        # skip named graph if not in the triple pattern
        if i < len(tp_tuple):
            if not tp_tuple[i].startswith('?'):
                # scape 'quotes'
                tp_tuple[i] = tp_tuple[i].replace("'", "''")
                tp_query += f"{i_pos[i]}='{tp_tuple[i]}' AND "

    # remove final `AND ` and `WHERE `
    if tp_query.endswith('AND '):
        tp_query = tp_query[:-4]
    if tp_query.endswith('WHERE '):
        tp_query = tp_query[:-6]

    # handle limit and offset
    if limit:
        if type(limit) is not int:
            raise TypeError("Limit must be an integer.")
        tp_query += f" LIMIT {limit}"
    if offset:
        if type(offset) is not int:
            raise TypeError("Offset must be an integer.")
        tp_query += f" OFFSET {offset}"

    return tp_query


def translate_triple_pattern_tuple(cottas_file, tp_tuple, limit=None, offset=None):
    """
    Given a COTTAS file and an RDFlib triple pattern tuple, translate the triple pattern to an SQL query over COTTAS.

    :param cottas_file: path to a COTTAS file
    :param tp_str: a user-defined triple pattern
    :return: SQL query for the triple pattern
    """

    if len(tp_tuple) == 3:
        tp_query = f"SELECT s, p, o FROM PARQUET_SCAN('{cottas_file}') WHERE "
    elif len(tp_tuple) == 4:
        tp_query = f"SELECT s, p, o, g FROM PARQUET_SCAN('{cottas_file}') WHERE "
    else:
        raise TypeError("The pattern must be a tuple of length 3 (triple) or 4 (quad).")

    # build selection iterating over all positions in the triple pattern
    for i in range(4):
        # skip named graph if not in the triple pattern
        if i < len(tp_tuple):
            if not tp_tuple[i] is None:
                if type(tp_tuple[i]) is str:
                    tp_query += f"{i_pos[i]}='{tp_tuple[i]}' AND "
                else:
                    tp_query += f"{i_pos[i]}='{tp_tuple[i].n3()}' AND "

    # remove final `AND ` and `WHERE `
    if tp_query.endswith('AND '):
        tp_query = tp_query[:-4]
    if tp_query.endswith('WHERE '):
        tp_query = tp_query[:-6]

    # handle limit and offset
    if limit:
        if type(limit) is not int:
            raise TypeError("Limit must be an integer.")
        tp_query += f" LIMIT {limit}"
    if offset:
        if type(offset) is not int:
            raise TypeError("Offset must be an integer.")
        tp_query += f" OFFSET {offset}"

    return tp_query
