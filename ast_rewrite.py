# -*- coding: utf-8 -*-
import ast
import astor
import inspect
from dsl import *
from collections import namedtuple

SrcTransform = namedtuple('SrcTransform', ['fname', 'code_obj', 'code_src', 'ast', 'in_ast'])

def wcps(fun):
    src = "\n".join(inspect.getsourcelines(fun)[0][1:])
    fun_ast = ast.parse(src)

    prefix = 'For_'
    r = Rewrite(prefix)
    for i in range(10):
        fun_ast = r.visit(fun_ast)
        ast.fix_missing_locations(fun_ast) # Fix line numbers
        if r.cnt == 0:
            break
        prefix = '%s%d_' % (prefix, r.cnt)
        r = Rewrite(prefix)

    out_src = astor.to_source(fun_ast)
    code_obj = compile(fun_ast, filename='<ast>', mode='exec')

    def subs(*args, **kwargs):
        return SrcTransform(fun_ast.body[0].name, code_obj, out_src, fun_ast, (src))

    return subs

def matches_scope(e, name):
    return (isinstance(e.value, ast.Subscript) and
            isinstance(e.value.value, ast.Call) and
            e.value.value.func.id == name)

def matches_subs(e, *names):
    if isinstance(e.value, ast.Call):
        name = e.value.func.id
        if name in names:
            return names[names.index(name)]
        else:
            return None
    else:
        return None

class Rewrite(ast.NodeTransformer):

    def __init__(self, prefix):
        self.scopes = []
        self.prefix = prefix
        self.cnt = 0

    def visit_FunctionDef(self, fd):
        self.scopes.append([])
        self.generic_visit(fd)
        fd.body = self.scopes.pop() + fd.body
        return fd

    def visit_Return(self, e):
        if matches_scope(e, 'For') or matches_scope(e, 'New'):
            return ast.Return(value=self.visit_Subscript(e).value)
        self.generic_visit(e)
        return e

    def visit_Subscript(self, e):
        head = matches_subs(e, 'For', 'New')
        if head:
            if isinstance(e.slice.value, ast.Tuple):
                seq = e.slice.value.elts
            else:
                seq = [e.slice.value]

            funcargs = [ ast.Name(id=a.arg, ctx=ast.Load())
                         for a in e.value.keywords ]
            if head == 'For':
                funvals =  [ ast.Call(func=ast.Name(id='CoverageExpr',
                                                    ctx=ast.Load()),
                                      args=[ast.Str(s=a.arg), a.value],
                                      keywords=[],
                                      starargs=None,
                                      kwargs=None)
                             for a in e.value.keywords ]
            else:
                funvals = [ ast.Str(s='$'+a.arg) for a in e.value.keywords ]
                funvals = [ ast.Call(func=ast.Name(id='IteratorExpr',
                                                   ctx=ast.Load()),
                                      args=[ast.Str(s=a.arg), a.value],
                                      keywords=[],
                                      starargs=None,
                                      kwargs=None)
                             for a in e.value.keywords ]

            funname = "%s%d" % (self.prefix, self.cnt)
            innerBody = [ast.Expr(value=s) for s in seq]
            innerBody[-1] = ast.Return(value=innerBody[-1].value)
            self.scopes[-1].append(ast.FunctionDef(
                    name=funname,
                    args=ast.arguments(args=funcargs, vararg=None, kwarg=None, defaults=[]),
                    body = innerBody,
                    decorator_list=[]))

            self.cnt += 1
            fun_call = ast.Call(func=ast.Name(id=funname,
                                              ctx=ast.Load()),
                    keywords=[],
                    starargs=None,
                    kwargs=None,
                    args=funvals)

            if head == 'For':
                constructor_args = [fun_call]
            else:
                constructor_args = [e.value.args[0], fun_call]

            return ast.Call(func=ast.Name(id= head + 'Expr',
                                          ctx=ast.Load()),
                            args = constructor_args,
                            starargs=None,
                            kwargs=None,
                            keywords = e.value.keywords)

        self.generic_visit(e)
        return e
