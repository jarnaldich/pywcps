# -*- coding: utf-8 -*-
from __future__ import absolute_import
from pprint import pprint
from ast_nodes import *

def count(child):  return ApplyExpr("count",  child)
def avg(child):    return ApplyExpr("avg",    child)
def add(child):    return ApplyExpr("add",    child)
def arcsin(child): return ApplyExpr("arcsin", child)
def arccos(child): return ApplyExpr("arccos", child)
def pow(child):    return ApplyExpr("pow",    child)
def re(child):     return ApplyExpr("re",     child)
def im(child):     return ApplyExpr("im",     child)
def cos(child):    return ApplyExpr("cos",    child)
def sin(child):    return ApplyExpr("sin",    child)
def cosh(child):   return ApplyExpr("cosh",   child)
def sinh(child):   return ApplyExpr("sinh",   child)

def cast(totype, child):
    return CastExpr(totype, child)

def quote_str(maybe_str):
    if isinstance(maybe_str, Expr):
        return maybe_str.emit()
    elif isinstance(maybe_str, str) and not maybe_str[0]=='$':
        return '"%s"'%(maybe_str,)
    else:
        return str(maybe_str)

def ansi(*args):
    quoted = ['"%s"'%(x,) for x in args ]
    return Slice("ansi", quoted)

def lon(*args): return Slice("Long", map(str, args))
def lat(*args): return Slice("Lat",  map(str, args))

def axis(label, *args, **kwargs):
    """ Generates a slice over the dimension with name label
    TODO: add crs capability. Could use kwargs
    """
    return Slice(label, map(quote_str, args), **kwargs)


def encode(expr, fmt):
    """
    Return expr as a string
    TODO: Check for fmt validity
    """
    return EncodeAppExpr(expr, fmt)

def switch(*args):
    """ switch
        case xxx """
    if not all((isinstance(x, Case) or isinstance(x,Default) ) for x in args):
        raise TypeMismatch("can only contain case or default")
    return SwitchExpr(args)

def case(cond, retval):
    return Case(cond, retval)

def default(retval):
    """ THe default for the switch statement """
    return Default(retval)

def struct(**kwargs):
    return StructExpr(kwargs)

def printE():
    global _ENVIRONMENTS
    print _ENVIRONMENTS

def wcps(fun):
    def wrapped():
        global _ENVIRONMENTS
        fun()
        obj = _ENVIRONMENTS.pop()
        return obj.emit()

    return wrapped
