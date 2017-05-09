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
        if isinstance(other, float):
            return BinOpExpr('<', self, LiteralExpr(other))
        elif isinstance(other, expr):
            return BinOpExpr('<', self, other)

class LiteralExpr(Expr):
    """ Literals """
    def __init__(self, val):
        self.val = val

    def emit(self):
        return str(self.val)

class EnvironmentExpr(Expr):
    """ Binding (for) expression for ... return ..."""
    def __init__(self, covs):
        self.covs = covs

    def emit(self):
        fors = ["for %s in (%s)" % (k,v) for k,v in self.covs.iteritems()]
        return ", ".join(fors) + " return %s "


class BinOpExpr(Expr):
    """ Binary Operators """
    def __init__(self, op, lhs, rhs):
        self.op  = op
        self.lhs = lhs
        self.rhs = rhs

    def emit(self):
        return "%s %s %s" % (self.lhs.emit(), self.op, self.rhs.emit())

class MemberExpr(Expr):
    """ Dot member operator. Eg. C.red """
    def __init__(self, parent, member):
        self.parent = parent
        self.member = member

class SliceExpr(Expr):
    """ Dot member operator. Eg. C[red] """
    def __init__(self, parent, member):
        self.parent = parent
        self.member = member
        
    def emit(self):
        return "%s[%s]" % (self.parent.emit(), self.member.emit())


class SliceListExpr(Expr):
    """ A list of slices for subindex (c[s1, s2, ...])"""
    def __init__(self, slices):
        self.slices = slices

    def emit(self):
        return ', '.join([s.emit() for s in self.slices])


class ApplyExpr(Expr):
    """ Function application. Eg. count(c[], expr)"""
    def __init__(self, f, child):
        self.f = f
        self.child = child

    def emit(self):
        return "%s(%s)" % (self.f, self.child.emit())

class CoverageExpr(Expr):
    """ Needs to update __getattr__"""
    def __init__(self, name, cov_id):
        #TODO: cov_id could be a list, actually
        self.var_name = name
        self.coverage_id = cov_id

    def emit(self):
        return self.var_name

    def __getitem__(self, *index):
        """
        TODO: Return a SliceExpr or sth like that
        """
        if not all(isinstance(x, Slice) for x in index):
            raise TypeMismatch("Index should be a subclass of Slice")

        return SliceListExpr(index)

    def __repr__(self):
        return "Coverage<%s>" % (self.coverage_id,)

    # def __getattribute__(self, attr):
    #     """ C.red > 0.5 should be valid """
    #     return MemberExpr(self, attr)

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
       return "%s(%s)" % (self.name, ",".join(self.args))


def coverages(**coverages):
    global _ENVIRONMENTS
    _ENVIRONMENTS.append(EnvironmentExpr(coverages))

    yield tuple([CoverageExpr(k,v) for k,v in coverages.iteritems()])

def count(child): return ApplyExpr("count", child)
def max(child): return ApplyExpr("max", child)

def ansi(*args): return Slice("ansi", args)

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
    env = _ENVIRONMENTS.pop()
    return env.emit() % (expr.emit(),)

def ast2dict(root_expr):
    acum = { '_node_' : type(root_expr).__name__ }
    for (name, val) in vars(root_expr).iteritems():
        if isinstance(val, Expr) or isinstance(val, Slice):
            acum[name] = ast2dict(val)
        else:
            acum[name] = val
    return acum

_ENVIRONMENTS=[]

