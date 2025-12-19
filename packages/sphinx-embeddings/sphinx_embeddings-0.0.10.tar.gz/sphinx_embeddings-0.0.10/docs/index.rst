=================
sphinx-embeddings
=================

Embeddings-powered features for Sphinx projects

.. _foo:

.. _bar:

-----------
Development
-----------

Setup
=====

.. code-block:: console

   curl -LsSf https://astral.sh/uv/install.sh | sh
   uv venv
   source .venv/bin/activate
   uv pip install -r requirements.txt

Build
=====

.. code-block:: console

   source .venv/bin/activate
   sphinx-build -b html . _build
