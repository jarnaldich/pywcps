# -*- coding: utf-8 -*-
from __future__ import absolute_import
from pprint import pprint
import pickle

#--------------------------------------------------------------------------------
#                                  EXCEPTIONS
#--------------------------------------------------------------------------------
class TypeMismatch(Exception):
    pass

#--------------------------------------------------------------------------------
#                                  EXPRESSIONS
#--------------------------------------------------------------------------------
class Expr(object):
    """
    TODO: Probably override arithm operators
    """
    def emit(self):
        return "emit(%s)" % (type(self).__name__)

    def __lt__(self, other):
        """ Need to dispatch on Expr and Float """
        if isinstance(other, Expr):
            return BinOpExpr('<', self, other)
        else:
            return BinOpExpr('<', self, LiteralExpr(other))

    def __mul__(self, other):
        """ Need to dispatch on Expr and Float """
        if isinstance(other, float):
            return BinOpExpr('*', self, LiteralExpr(other))
        elif isinstance(other, Expr):
            return BinOpExpr('*', self, other)


class LiteralExpr(Expr):
    """ Literals """
    def __init__(self, val):
        self.val = val

    def emit(self):
        return str(self.val)

class EnvironmentExpr(Expr):
    """ Binding (for) expression for ... return ..."""
    def __init__(self, covs, child):
        self.covs = covs
        self.child = child

    def emit(self):
        fors = ["%s in (%s)" % (k,v) for k,v in self.covs.iteritems()]
        return "for " + ", ".join(fors) + " return " + self.child.emit()


class BinOpExpr(Expr):
    """ Binary Operators """
    def __init__(self, op, lhs, rhs):
        self.op  = op
        self.lhs = lhs
        self.rhs = rhs

    def emit(self):
        return "(%s %s %s)" % (self.lhs.emit(), self.op, self.rhs.emit())

class MemberExpr(Expr):
    """ Dot member operator. Eg. C.red """
    def __init__(self, coverage, member):
        self.coverage = coverage
        self.member = member

    def emit(self):
        return "%s.%s" % (self.coverage.emit(),
                          self.member)

class SliceExpr(Expr):
    """ Dot member operator. Eg. C[red] """
    def __init__(self, parent, member):
        self.parent = parent
        self.member = member

    def emit(self):
        return "%s[%s]" % (self.parent.emit(), self.member.emit())


class SliceListExpr(Expr):
    """ A list of slices for subindices
        (c[s1, s2, ...])"""
    def __init__(self, cov, slices):
        self.cov = cov
        self.slices = slices

    def emit(self):
        lst = ', '.join([s.emit() for s in self.slices])
        return '%s[%s]' % (self.cov.emit(), lst)

class CastExpr(Expr):
    """ (type) expr"""
    def __init__(self, totype, child):
        self.child = child
        self.totype = totype

    def emit(self):
        return "(%s) %s" % (self.totype, self.child.emit())

class ApplyExpr(Expr):
    """ Function application. Eg. count(c[], expr)"""
    def __init__(self, f, child):
        self.f = f
        self.child = child

    def emit(self):
        return "%s(%s)" % (self.f, self.child.emit())

class EncodeAppExpr(Expr):
    """ Function application. Eg. count(c[], expr)"""
    def __init__(self, child, fmt, *opts):
        self.child = child
        self.fmt = fmt
        self.opts = opts

    def emit(self):
        return 'encode(%s, "%s")' % (self.child.emit(),
                                     self.fmt)


class CoverageExpr(Expr):
    def __init__(self, name, cov_id):
        #TODO: cov_id could be a list, actually
        self.var_name = name
        self.coverage_id = cov_id

    def emit(self):
        return self.var_name

    def __call__(self):
        _push(self)

    def __getitem__(self, index):
        """
        TODO: Return a SliceExpr or sth like that
        """
        if not isinstance(index, tuple):
            index = (index,)

        if not all(isinstance(x, Slice) for x in index):
            raise TypeMismatch("Index should be a subclass of Slice")

        return SliceListExpr(self, list(index))

    def __repr__(self):
        return "Coverage<%s>" % (self.coverage_id,)

    def __getattr__(self, attr):
        """ C.red > 0.5 should be valid """
        return MemberExpr(self, attr)

#--------------------------------------------------------------------------------
#                                    SLICES
#--------------------------------------------------------------------------------
class Slice(Expr):
    """
    Used for subsetting / slicing coverages. Not sure if this should be a child
    of Expr.
    Eg c[ THIS THING HERE ]
    """
    def __init__(self, name, args):
        self.name = name
        self.args = args

    def emit(self):
       return "%s(%s)" % (self.name, ":".join(self.args))

class SwitchExpr(Expr):
    """
    switch (case <cond> return <expr>)+
    """
    def __init__(self, cases):
        print cases
        self.cases = cases

    def emit(self):
        cases = ' '.join([c.emit() for c in self.cases])
        return "switch " + cases

class StructExpr(Expr):
    """
    { name: val }
    """
    def __init__(self, kwargs):
        self.assoc = kwargs

    def emit(self):
        def emit(o):
            if isinstance(o, Expr):
                return o.emit()
            else:
                return o
        pairs = [ "%s: %s"% (k, emit(v)) for k,v in self.assoc.iteritems() ]
        return '{%s}' % ('; '.join(pairs))


class Case(Expr):
    """
    Maybe does not need to inherit from Expr
    """
    def __init__(self, cond, retval):
        self.cond = cond
        self.retval = retval

    def emit(self):
        print self.cond
        return "case %s return %s" % (self.cond.emit(), self.retval.emit())

class Default(Expr):
    """
    """
    def __init__(self, retval):
        self.retval = retval

    def emit(self):
        return "default return " + self.retval.emit()

def _push(obj):
    global _ENVIRONMENTS
    _ENVIRONMENTS.append(obj)

def _pop():
    global _ENVIRONMENTS
    return _ENVIRONMENTS.pop()

def count(child): return ApplyExpr("count", child)
def avg(child): return ApplyExpr("avg", child)

def cast(totype, child):
    return CastExpr(totype, child)

def quote_str(maybe_str):
    if isinstance(maybe_str, str):
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
    return Slice(label, map(quote_str, args))


def debug(expr, fmt):
    """
    Return expr as a string
    TODO: Check for cast_to validity
    TODO: Check for fmt validity
    TODO: Do Sth With EPR
    """
    print pprint(ast2dict(expr), indent=2)

def encode(expr, fmt):
    """
    Return expr as a string
    TODO: Check for fmt validity
    """
    _push(EncodeAppExpr(expr, fmt))

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

def ast2dict(root_expr):
    acum = { '_node_' : type(root_expr).__name__ }
    for (name, val) in vars(root_expr).iteritems():
        if isinstance(val, Expr) or isinstance(val, Slice):
            acum[name] = ast2dict(val)
        else:
            acum[name] = val
    return acum

class Coverages(object):
    def __init__(self, **kwargs):
        """TODO: Maybe the where clause should be here, too"""
        self.coverages = kwargs

    def __enter__(self):
        lst = [CoverageExpr(k,v)
               for k,v in self.coverages.iteritems()]
        if len(lst) > 1:
            return tuple(lst)
        else:
            return lst[0]

    def __exit__(self, extype, exval, traceback):
        if extype is None:
            _push(EnvironmentExpr(self.coverages, _pop()))

_ENVIRONMENTS=[]

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


