=====
Usage
=====

Chemical registry
=================

``graphmix`` provides a chemical registry that can be used to store and retrieve chemicals. A SQLite database is used.
Whenever a chemical is not found in the database, it is fetched from PubChem and stored in the database.

.. code-block:: python

    import graphmix
    chem_reg = graphmix.ChemicalRegistry()
    etoh = chem_reg.Chemical("Ethanol")
    print(etoh)

    # Output:

.. code-block:: python

    import graphmix
    graphmix.compute(...)
