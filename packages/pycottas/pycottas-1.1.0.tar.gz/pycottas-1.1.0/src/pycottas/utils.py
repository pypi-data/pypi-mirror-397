__author__ = "Julián Arenas-Guerrero"
__credits__ = ["Julián Arenas-Guerrero"]

__license__ = "Apache-2.0"
__maintainer__ = "Julián Arenas-Guerrero"
__email__ = "julian.arenas.guerrero@upm.es"


import duckdb

from os import path


def get_file_extension(file_path):
    return path.splitext(file_path)[1].lower()


def generate_cottas_info(cottas_file):
    import os
    import datetime

    kv_query = f"SELECT * FROM PARQUET_KV_METADATA('{cottas_file}') WHERE key='index'"
    row_query = f"SELECT num_rows AS triples, num_row_groups AS triples_groups FROM PARQUET_FILE_METADATA('{cottas_file}')"
    properties_query = f"SELECT COUNT(DISTINCT p) FROM PARQUET_SCAN('{cottas_file}')"
    distinct_subjects_query = f"SELECT COUNT(DISTINCT s) FROM PARQUET_SCAN('{cottas_file}')"
    distinct_objects_query = f"SELECT COUNT(DISTINCT o) FROM PARQUET_SCAN('{cottas_file}')"
    schema_query = f"DESCRIBE SELECT * FROM PARQUET_SCAN('{cottas_file}') LIMIT 1"
    compression_query = f"SELECT compression FROM PARQUET_METADATA('{cottas_file}')"

    (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(cottas_file)
    cottas_issued = datetime.datetime.fromtimestamp(ctime).isoformat()

    info_dict = {
        'index': duckdb.execute(kv_query).fetchone()[2].decode(),
        'triples': duckdb.execute(row_query).fetchone()[0],
        'triples_groups': duckdb.execute(row_query).fetchone()[1],
        'properties': duckdb.execute(properties_query).fetchone()[0],
        'distinct_subjects': duckdb.execute(distinct_subjects_query).fetchone()[0],
        'distinct_objects': duckdb.execute(distinct_objects_query).fetchone()[0],
        'issued': cottas_issued,
        'size (MB)': os.path.getsize(cottas_file) / 10**6,
        'compression': duckdb.execute(compression_query).fetchone()[0],
        'quads': 'g' in [res[0] for res in duckdb.execute(schema_query).fetchall()],
    }

    return info_dict


def is_valid_index(index):
    index = index.lower()
    if len(index) == 3:
        if set(index) != {'s', 'p', 'o'}:
            return False
    elif len(index) == 4:
        if set(index) != {'s', 'p', 'o', 'g'}:
            return False
    else:
        return False
    return True


def verify_cottas_file(cottas_file):
    verify_query = f"DESCRIBE SELECT * FROM PARQUET_SCAN('{cottas_file}') LIMIT 1"

    cottas_columns = set()
    for res in duckdb.execute(verify_query).fetchall():
        cottas_columns.add(res[0])

    for pos in ['s', 'p', 'o']:
        if pos not in cottas_columns:
            return False

    return cottas_columns <= {'s', 'p', 'o', 'g'}
