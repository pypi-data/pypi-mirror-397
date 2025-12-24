__author__ = "Julián Arenas-Guerrero"
__credits__ = ["Julián Arenas-Guerrero"]

__license__ = "Apache-2.0"
__maintainer__ = "Julián Arenas-Guerrero"
__email__ = "julian.arenas.guerrero@upm.es"


import duckdb
import pyoxigraph

from rdflib.util import from_n3
from .tp_translator import translate_triple_pattern
from .utils import verify_cottas_file


class COTTASDocument():
    def __init__(self, path: str):
        if not verify_cottas_file(path):
            raise Exception(f"{path} is not a valid COTTAS file.")

        self._cottas_path = path
        duckdb.query(
            f"SET parquet_metadata_cache=true; SET enable_progress_bar=false; SELECT * FROM PARQUET_SCAN('{path}')")
        self._num_triples = duckdb.execute(f"SELECT COUNT(*) FROM PARQUET_SCAN('{path}')").fetchone()[0]
        self._is_quad_table = 'g' in [res[0] for res in duckdb.execute(
            f"DESCRIBE SELECT * FROM PARQUET_SCAN('{path}') LIMIT 1").fetchall()]

    @property
    def cottas_file(self) -> str:
        """The COTTAS file path."""
        return self._cottas_path

    @property
    def is_quad_table(self) -> str:
        """Whether the table has named graphs."""
        return self._is_quad_table

    def __len__(self, context) -> int:
        """The number of RDF triples in the COTTAS store."""
        return self._num_triples

    @property
    def nb_subjects(self) -> int:
        """The number of subjects in the COTTAS store."""
        return duckdb.execute(f"SELECT COUNT(DISTINCT s) FROM PARQUET_SCAN('{self._cottas_path}')").fetchone()[0]

    @property
    def nb_predicates(self) -> int:
        """The number of predicates in the COTTAS store."""
        return duckdb.execute(f"SELECT COUNT(DISTINCT p) FROM PARQUET_SCAN('{self._cottas_path}')").fetchone()[0]

    @property
    def nb_objects(self) -> int:
        """The number of objects in the COTTAS store."""
        return duckdb.execute(f"SELECT COUNT(DISTINCT o) FROM PARQUET_SCAN('{self._cottas_path}')").fetchone()[0]

    def search(self, pattern, limit=None, offset=None, results_in_n3=True):
        if len(pattern) == 4 and not self._is_quad_table:
            raise Exception("The COTTAS file is not a quad table, quad patterns are not valid.")

        triples = duckdb.execute(translate_triple_pattern(self._cottas_path, pattern, limit, offset)).fetchall()

        if results_in_n3:
            return triples

        for i, triple in enumerate(triples):
            if len(triple) == 3:
                triples[i] = (from_n3(triple[0]), from_n3(triple[1]), from_n3(triple[2]))
            else:
                # len(triple) = 4
                triples[i] = (from_n3(triple[0]), from_n3(triple[1]), from_n3(triple[2]), from_n3(triple[3]))

        return triples

