# pyWCPS

* NOT USABLE YET, API LIKELY TO CHANGE *

Library for writing Web Coverage Processing Service (WCPS) queries in
Python, the core of which is an Embedded Domain Specific Language (EDSL) for
generating the WCPS Language queries.

The problem: accessing WCPS from Python often means generating a string with the
query source code and then sending it to the server endpoint via REST or POST. For
non trivial queries, generating the string from Python code can be cumbersome
because of:

- Lack of tooling support (editor indentation, paren matching, etc...).
- The code is mostly generated with ad-hoc interpolation and concatenation of
  strings, which is weak in terms of abstraction and composability.
- WCPS code gets obscured since it is intertwined with Python code.

These problems can be greatly reduced by designing an Embedded Domain Specific
Language (EDSL). The EDSL design pattern aims to map the syntax of the embedded
language (here the WCPS language) into the syntax of a host language (here
Python). This allows for automatically reusing the abstraction capabilities
and tooling of the host language.

Here are a list of real examples from: showing what we can achieve with this
approach:
...

# The Plan

  Writing a EDSL for a language that I do not know that much can be a bit risky,
  so I prefer to start small. What I am more interested now is in getting the
  structure right before adding a whole lot of functions. 
  
  For example, I have just implemented the functions and operators that I needed
  for the queries above (avg, count, +, *). I have left the others out
  intentionally because I first need to make sure the structure is solid.
  
  That is where I would like to get feedback/help:
  
  - Can you think of a language construct I have left out? I'd be especially
    interested in any query that has essentialy a different structure than the
    ones I have already implemented...
    
  - I have seen in the documentation that one can write for example a
    convolution. Any complete example on that?

  If you are interested, keep reading...

# Design Principles

  The goal is should be to make it possible to express WCPS Language queries as
  Python constructs. All WCPS functionality should be available.
  
  When designing a DSL, some compromises have to be made. One can imagine trying
  to make the surface syntax as close to the embedded language (WCPS) as possible,
  at the expense of forcing the syntax of the host language (being un-Pythonic),
  or to ignore the syntax of the host language whatsoever and just provide a
  library for the host, at the expense of making this library counter intuitive for
  the users of the embedded language. 
  
  Designing a EDSL often involves a non-negligible amount of magic (on the fly syntax
  manipulation, run-time code generation, introspection, etc...). These tools,
  when not used with care, can lead to unexpected and uninutitive behaviours for
  the programmer.
  
  This project will try to find a sweet spot where the Python code can still be
  understandable as WSDL without forcing Python too much. To do so we will try
  to follow one basic design principle: the EDSL will be an *expression language*.
  
  Remember that expressions in Python (and other languages) are any constructs
  that have a value, can be assigned to a variable, passed to a function, etc...
  Contrast this with statements, that are there for side-effects.
  
  Examples of expressions: `1+1`, `sin(x)`. Examples of non expressions `a=1+1`,
  `if`s, `for`s, `def`s...
  
  I think expressions are especially suitable in this case because WCPS language is
  essentially an expression language (eg. queries are essentially more or less
  big expresions that return a result).
  
  Expressions have the nice property that they are _composable_: bigger
  expressions can be built from the combination of smaller ones, which is good
  for reuse and abstraction.
  
  Furthermore, expressions map very naturally into Python syntax. The only
  exception are the _binding_ forms in WSCPS, that is those that "declare"
  variable, namely the `for` (that bind coverage variables) and the
  coverage constructors (that declare index variables). Binding forms in Python
  are not expressions, so a little AST manipulation is needed to bridge that
  gap. Hopefully this will not result in any quirks when writing the code if the
  coder assumes the basic design principle: that the whole EDSL is made of
  expressions.
  
# A sketch of the implementation

  90% of EDSL are just python functions (defined in `dsl.py`) that, when
  composed, build an AST (Abstract Syntax Tree) from the ground up. The root
  node of this AST can later
  be asked to emit the string that represents the WCPS query. The nodes of this
  AST can be seen in the file `ast_nodes.py` and are just Python classes. Note
  that this AST is different from the one needed to parse the WCPS language,
  since we are just interested in code emission, which is easier.
  
  The only piece of magic are the binding forms `For` and `New`, which are
  syntactically expressions but have to be transformed via source inspection and AST walking
  into Python binding forms (functions under the hood). If done right, this
  should be transparent to the coder.
  
  *maybe explain the transformation*

# TODO

- Tests
- Docs
- More language features

# RESOURCES

- https://jupyter.eofrom.space/user/jarnaldich/tree? 
- https://jupyter.eofrom.space/user/jarnaldich/notebooks/jupyter_notebooks/geopython_workshop_2017/Domain_examples.ipynb
- http://earthserver.pml.ac.uk/how_to/ocean

La clau està en l'ús del coverateExpr, que pot avaluar a diferents tipus de 
