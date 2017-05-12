# -*- coding: utf-8 -*-
import ast
import astor
import inspect

class For():
    """
    """
    def __init__(self, **covs):
        self.covs = covs
        env = inspect.currentframe().f_back.f_locals
        print env
        for k,v in self.covs.iteritems():
            env[k] = v

    def __getitem__(self, *subexpr):
        a = ""
        return "HOOOOL"

def subexp(*args):
    print "HOOOLA"
    f_parent = inspect.currentframe().f_back.f_locals

def wcps(fun):
    src = "\n".join(inspect.getsourcelines(fun)[0][1:])
    fun_ast = ast.parse(src)
    
    ast.fix_missing_locations(fun_ast) # Fix line numbers
    print astor.dump(fun_ast)
    print astor.to_source(fun_ast)

    prefix = 'For_'
    r = Rewrite(prefix)
    for i in range(10):
        fun_ast = r.visit(fun_ast)
        ast.fix_missing_locations(fun_ast) # Fix line numbers
        print r.cnt
        if r.cnt == 0:
            break
        prefix = '%s%d_' % (prefix, r.cnt)
        r = Rewrite(prefix)

#    out_fun = r.visit(fun_ast)
    print astor.to_source(fun_ast)
    code_obj = compile(fun_ast, filename='<ast>', mode='exec')
    def subs(*args, **kwargs):
        return code_obj
    return subs


def test2():
    For(c="C1")[
            encode(New('histogram',
                       px=axis('x', 0, 0),
                       py=axis('y', 0, 0),
                       pt=axis('t', 0, 360))[
                           add(c[Long[-50:40], Lat[45:55], ansi[pt]])
                       ], "csv"),
    ]

class Rewrite(ast.NodeTransformer):
    pass

def matches_scope(e, name):
    return (isinstance(e.value, ast.Subscript) and 
            isinstance(e.value.value, ast.Call) and
            e.value.value.func.id == name)

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

    def visit_Expr(self, e):
        if matches_scope(e, 'For'):
            if isinstance(e.value.slice.value, ast.Tuple):
                seq = e.value.slice.value.elts
            else:
                print type(e.value.slice.value)
                seq = [e.value.slice.value] 

            funcargs = [ ast.Name(id=a.arg, ctx=ast.Load()) for a in e.value.value.keywords ]
            funvals =  [ a.value for a in e.value.value.keywords ]
            funname = "%s%d" % (self.prefix, self.cnt)
            innerBody = ast.Expr(value=ast.List(elts=seq, ctx=ast.Load()))
            self.scopes[-1].append(ast.FunctionDef(
                    name=funname, #ast.Name(id="auto", ctx=ast.Load()),
                    args=ast.arguments(args=funcargs, vararg=None, kwarg=None, defaults=[]),
                    body = [ast.Expr(value=s) for s in seq],
                    decorator_list=[]))

            self.cnt += 1

            return ast.Expr(value=ast.Call(func=ast.Name(id=funname, ctx=ast.Load()),
                    keywords=[],
                    starargs=None,
                    kwargs=None,
                    args=funvals))

        return e

@wcps
def test():
    return "hola"
    For(a="A")[
        subexp()
    ]
    For(c="C1")[
            encode(c, "csv"),
            For(d="C2")[
                subexp(), subexp()
            ]
    ]

#exec (test()) in globals(), locals()
