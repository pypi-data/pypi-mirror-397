__author__ = "Julián Arenas-Guerrero"
__credits__ = ["Julián Arenas-Guerrero"]

__license__ = "Apache-2.0"
__maintainer__ = "Julián Arenas-Guerrero"
__email__ = "julian.arenas.guerrero@upm.es"


# dict mapping RDF term positions to attribute names
i_pos = {
    0: 's',
    1: 'p',
    2: 'o',
    3: 'g'
}


##############################################################################
#############################   Oxigraph  ####################################
##############################################################################

file_ext_2_mime_type = {
    '.nt': 'application/n-triples',
    '.nq': 'application/n-quads',
    '.ttl': 'text/turtle',
    '.trig': 'application/trig',
    '.rdf': 'application/rdf+xml'
}

