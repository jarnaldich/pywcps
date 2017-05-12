# -*- coding: utf-8 -*-
from __future__ import absolute_import
import requests
from ast_nodes import *
from dsl import *

def emit_fun(f):
    (fname, code, src, ast, in_ast) = f()
    exec (code) in globals(), locals()
    return locals()[fname]().emit()

class WCPSClient(object):

    def __init__(self, url):
        self.url = url

    def _req(self, wcps_str):
        return requests.post(self.url, data={'query': wcps_str})

    def get_str(self, q):
        return self._req(emit_fun(q)).text

    def save_to(self, q, fname):
        with open(fname,'wb') as f:
            f.write(self._req(emit_fun(q)).content)

if __name__ == "__main__":
    eo = WCPSClient('http://earthserver.pml.ac.uk/rasdaman/ows/wcps')

