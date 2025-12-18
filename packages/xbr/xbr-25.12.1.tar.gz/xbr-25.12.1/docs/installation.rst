Installation
============

This guide covers installing **wamp-xbr** in your Python environment.

Requirements
------------

* Python 3.9 or later
* CPython or PyPy

Installing from PyPI
--------------------

The recommended way to install wamp-xbr is from PyPI:

.. code-block:: bash

    pip install xbr

This will install wamp-xbr and its dependencies.

Installing from Source
----------------------

To install the latest development version:

.. code-block:: bash

    git clone https://github.com/wamp-proto/wamp-xbr.git
    cd wamp-xbr
    pip install -e .

Verifying Installation
----------------------

Verify the installation by checking the version:

.. code-block:: python

    import xbr
    print(xbr.__version__)

Dependencies
------------

wamp-xbr depends on:

* **web3**: Ethereum interaction library
* **autobahn**: WAMP client library
* **py-eth-sig-utils**: Ethereum signature utilities
