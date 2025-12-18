BIO pype
========

A Python Framework for Bioinformatics Pipeline Management
------------------------------------------------------------

Bio_pype provides a comprehensive framework for building, organizing, and standardizing
bioinformatics tools and pipelines. Built on Python's robust argparse_ module, it offers
both command-line accessibility and programmatic flexibility.

Key Features
------------

- Modular pipeline construction
- Environment management integration (Environment Modules_, Docker_, etc.)
- Multiple queue system support (MOAB_Torque_, SLURM, etc.)
- Version-controlled configurations
- Reproducible execution environments

Installation
------------

**From PyPI**

::

    pip install bio_pype

**Development Version**

::

    git clone https://bitbucket.org/ffavero/bio_pype
    cd bio_pype
    python setup.py test
    python setup.py install

Basic Usage
-----------

Available Commands::

    $ pype
    usage: pype [-p PROFILE] {pipelines,profiles,repos,snippets} ...

    A framework for managing bioinformatics workflows and tools

    Commands:
        pipelines       Execute and manage analysis workflows
        profiles       Configure execution environments
        repos         Manage module repositories
        snippets      Run individual analysis tasks

    Options:
      -p PROFILE, --profile PROFILE
                        Select execution profile (default: default)

Repository Management
---------------------

List available repositories::

    $ pype repos list

Install a repository::

    $ pype repos install -f <repo-name>

Advanced Configuration
----------------------

Environment variables allow custom module locations::

    # Use local snippets
    export PYPE_SNIPPETS=path/to/snippets
    pype snippets

    # Use local pipelines
    export PYPE_PIPELINES=path/to/pipelines
    pype pipelines

For complete documentation, visit our `Read the Docs`_ site.

.. _argparse: https://docs.python.org/3/library/argparse.html
.. _Modules: http://modules.sourceforge.net
.. _Docker: https://www.docker.com
.. _MOAB_Torque: http://www.adaptivecomputing.com
.. _Read the Docs: http://bio-pype.readthedocs.io