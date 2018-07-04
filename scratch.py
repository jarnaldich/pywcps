# -*- coding: utf-8 -*-
import ast
import astor
import inspect
from collections import namedtuple
from dsl import *
from ast_rewrite import wcps

@wcps
def test_simple(): return For(c="C")[encode(c, "csv")]

@wcps
def test_2cov(): return For(c="C", d="V")[encode(c*d, "csv")]

@wcps
def test_count(): return For(c="C")[encode(count(c), "csv")]

@wcps
def test_op2(): return For(c="C")[encode(count(c.rgb < 0.5), "csv")]

@wcps
def test_latlon():
    return For(c="COV1")[
            encode(count(c[axis('Long', 0, 10),
                           axis('Lat', 45,55),
                           axis('ansi',"2010-01-31T23:59:00")] < 0.5), "csv")
    ]

@wcps
def test_cloro():
    return For(c="CCI_V2_monthly_chlor_a_rmsd")[
         encode(cast('float',
                    count(c[ansi("2010-01-31T23:59:00")] < 0.201)),
               "csv")]

@wcps
def test_cloro2():
    return For(c="CCI_V2_release_chlor_a",
               d="CCI_V2_monthly_chlor_a_rmsd")[
                   encode(
          cast('float',
             avg(c[axis('Long',0,10),
                   axis('Lat', 45,55),
                   axis('ansi', '2010-01-31T23:59:00')] *
                 (d[axis('Long',0,10),
                    axis('Lat', 45,55),
                    axis('ansi', '2010-01-31T23:59:00')] < 0.45))
        ), "csv")]

@wcps
def test_colortable():

    def less_than(cov, x):
        return  cov[axis('Lat', 30,70),
                  axis('Long', -30,10),
                  axis('ansi', "2009-09-30T23:59:00Z")] < x

    def rgba(r,g,b,a):
        return struct(red=r, green=g, blue=b, alpha=a)

    return For(a="CCI_V2_monthly_chlor_a")[
            encode(
                switch(
                    case(less_than(a, 0.05), rgba(255, 255, 255,   0)),
                    case(less_than(a,  0.1), rgba(  0, 255, 255, 255)),
                    case(less_than(a,  0.2), rgba(  0, 128, 255, 255)),
                    case(less_than(a,  0.5), rgba(  0,   0, 255, 255)),
                    case(less_than(a,  1.5), rgba(218,   0, 255, 255)),
                    case(less_than(a,  3.0), rgba(255,   0, 255, 255)),
                    case(less_than(a,  4.5), rgba(255, 164,   0, 255)),
                    case(less_than(a,  6.2), rgba(255, 250,   0, 255)),
                    case(less_than(a,   20), rgba(255,   0,   0, 255)),
                    default(rgba(255, 255, 255,  0))), "png")]

@wcps
def test2():
    l = 100000
    def my_slice(cov, time):
        return ((cov[axis('Long', -50,40),
                   axis('Lat', 45,55),
                   axis('ansi', time, crs="CRS:1")] < l) *
    return For(c="CCI_V2_release_daily_chlor_a")[
            encode(New('histogram',
                       px=axis('x', 0, 0),
                       py=axis('y', 0, 0),
                       pt=axis('t', 0, 360))[
                           add((my_slice(c, pt  , l) * my_slice(c,pt)) / count(my_slice(c, pt  , l))) + \
                           add((my_slice(c, pt+1, l) * my_slice(c,pt)) / count(my_slice(c, pt+1, l))) + \
                           add((my_slice(c, pt+2, l) * my_slice(c,pt)) / count(my_slice(c, pt+2, l)))
                       ], "csv")]

# def emit_fun(f):
#     (fname, code, src, ast, in_ast) = f()
#     exec (code) in globals(), locals()
#     return locals()[fname]().emit()

# for f in dir():
#     if f.startswith('test_'):
#         print emit_fun(locals()[f])

# (fname, code, src, ast, in_ast) = test2()
# with open('debug.py', 'w') as f:
#     print >>f, src
from wcps_client import WCPSClient
eo = WCPSClient('http://earthserver.pml.ac.uk/rasdaman/ows/wcps')
# print eo.get_str(test_cloro)
# print eo.get_str(test_cloro2)
# eo.save_to(test_colortable, 'test.png')
print eo.get_str(test2)

