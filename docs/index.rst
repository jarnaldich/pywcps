.. PyWCPS documentation master file, created by
   sphinx-quickstart on Thu Jul 05 09:54:21 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to PyWCPS's documentation!
==================================

The problem: accessing WCPS from Python often means generating a string with the query source code and then sending it to the server endpoint via REST or POST. For non trivial queries, generating the string from Python code can be cumbersome because of:

- Lack of tooling support (editor indentation, paren matching, etc...).
- The code is mostly generated with ad-hoc interpolation and concatenation of strings, which is weak in terms of abstraction and composability.
- WCPS code gets obscured since it is intertwined with Python code.

These problems can be greatly reduced by designing an Embedded Domain Specific Language (EDSL). The EDSL design pattern aims to map the syntax of the embedded language (here the WCPS language) into the syntax of a host language (here Python). This allows for automatically reusing the abstraction capabilities and tooling of the host language.


Contents:

.. toctree::
   :maxdepth: 2

.. automodule:: pywcps.ast_rewrite 
 
.. autoclass:: pywcps.ast_rewrite.Rewrite
    :members:
 
Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


- http://tutorial.rasdaman.org/rasdaman-and-ogc-ws-tutorial/#rasql-querying-the-data
- 08-068r2_Web_Coverage_Processing_Service_WCPS_Language_Interface_Standard.pdf

