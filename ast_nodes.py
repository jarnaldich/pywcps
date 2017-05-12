# -*- coding: utf-8 -*-
from __future__ import absolute_import
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

    def _binop(self, other, op):
        """ Need to dispatch on Expr and Float """
        if isinstance(other, Expr):
            return BinOpExpr(op, self, other)
        else:
            return BinOpExpr(op, self, LiteralExpr(other))

    def __lt__(self, other):
        return self._binop(other, '<')
    def __mul__(self, other):
        return self._binop(other, '*')
    def __add__(self, other):
        return self._binop(other, '+')
    def __div__(self, other):
        return self._binop(other, '/')

class LiteralExpr(Expr):
    """ Literals """
    def __init__(self, val):
        self.val = val

    def emit(self):
        return str(self.val)

class IteratorExpr(Expr):
    """ Iterator variables """
    def __init__(self, name, val):
        self.name = name
        self.val = val

    def emit(self):
        return "$"+self.name

class ForExpr(Expr):
    """ Binding (for) expression for ... return ..."""
    def __init__(self, child, **covs):
        self.covs = covs
        self.child = child

    def emit(self):
        fors = ['%s in (%s)' % (k,v) for k,v in self.covs.iteritems()]
        return "for " + ", ".join(fors) + " return " + self.child.emit()

class NewExpr(Expr):
    """ Binding (for) expression for ... return ..."""
    def __init__(self, name, child, **covs):
        if not all(isinstance(x, Slice) for x in covs.values()):
            raise TypeMismatch("Index should be a subclass of Slice")

        self.name = name
        self.covs = covs
        self.child = child

    def emit(self):
        fors = ['$%s in (%s:%s)' % (k, v.args[0], v.args[1])
                for k,v in self.covs.iteritems()]
        return "for " + ", ".join(fors) + " values ( " + self.child.emit() + " )"

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
    def __init__(self, name, args, crs=""):
        self.name = name
        self.args = args
        self.crs = crs

    def emit(self):
        if self.crs:
            return '%s:"%s"(%s)' % (self.name, self.crs, ":".join(self.args))
        else:
            return "%s(%s)" % (self.name, ":".join(self.args))

class SwitchExpr(Expr):
    """
    switch (case <cond> return <expr>)+
    """
    def __init__(self, cases):
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
        return "case %s return %s" % (self.cond.emit(), self.retval.emit())

class Default(Expr):
    """
    """
    def __init__(self, retval):
        self.retval = retval

    def emit(self):
        return "default return " + self.retval.emit()

