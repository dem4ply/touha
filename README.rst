=====
touha
=====

.. image:: https://readthedocs.org/projects/touha/badge/?version=latest
        :target: https://touha.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status



tool for backup and restore rasberry pi sd cards


* Free software: WTFPL
* Documentation: https://touha.readthedocs.io.


**********
How to use
**********

backups
=======

.. code-block:: bash

	export sd_block=/dev/sde
	touha backup -b $sd_block

Restore
=======

esta madre no funciona

asdf

Format
======

.. code-block:: bash
	export sd_block=/dev/sde
	touha format -b $sd_block --version 4


Features
--------

* TODO

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
