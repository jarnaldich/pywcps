# pyWCPS

Library for writing Web Coverage Processing Service (WCPS) queries in
Python, including an Embedded Domain Specific Language (EDSL) for generating the
WCPS Language queries.

* NOT USABLE YET, API LIKELY TO CHANGE *
# GOALS

- To make it possible to express WCPS Language queries as python constructs. All
  WCPS functionality should be available, although not every syntactic variant
  will be produced; for example, structs in WCPSL can be stated as "struct {}"
  or just "{...}". Whenever this happens, the library will opt for one variant.
  
  When designing a DSL, some compromises have to be made. One can imagine trying
  to make the surface syntax as close to the embedded language (WCPS) as possible,
  at the expense of forcing the syntax of the host language (being un-pythonic),
  or to ignore the syntax of the host language whatsoever and just provide a
  library for the host, at the expense of making this library counter intuitive for
  the users of the embedded language. 
  
  This project will try to find a sweet spot where the python code can still be
  understandable as WSDL without forcing Python too much.

  Generating WCPL queries as python code has the following advantadges:
  
  - Tooling, syntax highlighting, etc...
  - Abstraction (one can factor away sub-expressions as functions, parameterize
    the queries just as Python functions do, etc...)

# TODO

- The coverage constuctor. This would probably work best with a "with" statement...
- Tests
- Docs
- More language features


# RESOURCES

- https://jupyter.eofrom.space/user/jarnaldich/tree? 
- https://jupyter.eofrom.space/user/jarnaldich/notebooks/jupyter_notebooks/geopython_workshop_2017/Domain_examples.ipynb
- http://earthserver.pml.ac.uk/how_to/ocean

La clau està en l'ús del coverateExpr, que pot avaluar a diferents tipus de 
