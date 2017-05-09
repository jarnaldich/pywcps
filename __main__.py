from pywcps import *
#--------------------------------------------------------------------------------
#                                  QUERIES
#--------------------------------------------------------------------------------

def query():
    """ The decorator walks the AST and emits a WCPS query. """
    for (c,d) in coverages(c="COV1", d="COV2"):
        return encode(count(d[ansi("1979-05-01T00:00:00","1979-05-31T18:00:00")]) < 0.201, "csv")
