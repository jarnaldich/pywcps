# -*- coding: utf-8 -*-
from __future__ import absolute_import
import requests
from .ast_nodes import *
from .dsl import *

def emit_fun(f, *args, **kwargs):
    (fname, code, src, ast, in_ast) = f()
    exec (code) in globals(), locals()
    return locals()[fname](*args, **kwargs).emit()

class WCPSClient(object):

    def __init__(self, url):
        self.url = url

    def _req(self, wcps_str):
        return requests.post(self.url, data={'query': wcps_str})

    def get_str(self, q, *args, **kwargs):
        return self._req(emit_fun(q, *args, **kwargs)).text

    def save_to(self, q, fname, *args, **kwargs):
        with open(fname,'wb') as f:
            f.write(self._req(emit_fun(q, *args, **kwargs)).content)

    def ipython_image(self, q, ipython_kw = {}, *args, **kwargs):
        from IPython.display import Image
	ipython_kw['data'] = self._req(emit_fun(q, *args, **kwargs)).content
        return Image(**ipython_kw)

if __name__ == "__main__":
    eo = WCPSClient('http://earthserver.pml.ac.uk/rasdaman/ows/wcps')

