__author__ = "Julián Arenas-Guerrero"
__credits__ = ["Julián Arenas-Guerrero"]

__license__ = "Apache-2.0"
__maintainer__ = "Julián Arenas-Guerrero"
__email__ = "julian.arenas.guerrero@upm.es"


import duckdb

from typing import Iterable
from rdflib.store import Store
from rdflib.util import from_n3

from .utils import verify_cottas_file
from .types import Triple
from .tp_translator import translate_triple_pattern_tuple


class COTTASStore(Store):
    """An implementation of a Store over a COTTAS document.

    It is heavily inspired by the work from @FlorianLudwig (https://github.com/RDFLib/rdflib/issues/894) and adapted
    from rdflib-hdt (https://github.com/RDFLib/rdflib-hdt).

    Args:
      - path: Absolute path to the COTTAS file to load.
    """
    def __init__(self, path: str, configuration=None, identifier=None):
        super(COTTASStore, self).__init__(configuration=configuration, identifier=identifier)

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

    def triples(self, pattern, context) -> Iterable[Triple]:
        """Search for a triple pattern in a COTTAS store.

        Args:
          - pattern: The triple pattern (s, p, o) to search.
          - context: The query execution context.

        Returns: An iterator that produces RDF triples matching the input triple pattern.
        """
        for triple in duckdb.execute(translate_triple_pattern_tuple(self._cottas_path, pattern)).fetchall():
            triple = from_n3(triple[0]), from_n3(triple[1]), from_n3(triple[2])
            yield triple, None
        return

    def create(self, configuration):
        raise TypeError('The COTTAS store is read only!')

    def destroy(self, configuration):
        raise TypeError('The COTTAS store is read only!')

    def commit(self):
        raise TypeError('The COTTAS store is read only!')

    def rollback(self):
        raise TypeError('The COTTAS store is read only!')

    def add(self, _, context=None, quoted=False):
        raise TypeError('The COTTAS store is read only!')

    def addN(self, quads):
        raise TypeError('The COTTAS store is read only!')

    def remove(self, _, context):
        raise TypeError('The COTTAS store is read only!')
