codebackup
==========

A simple command line tool to backup all of your Github and Bitbucket
repositories to the specified directory.

Installing
----------

::
    $ python3.7 -m venv .
    $ ./bin/pip install -e .


Usage
-----

::

    $ ./bin/codebackup --github-user=srid --bitbucket-user=srid ~/Dropbox/codebackup

Credits
-------

- `github-simple-backup`_, original inspiration
- `Distribute`_
- `Buildout`_
- `modern-package-template`_

.. _`github-simple-backup`: http://github.com/jbalogh/github-simple-backup
.. _Buildout: http://www.buildout.org/
.. _Distribute: http://pypi.python.org/pypi/distribute
.. _`modern-package-template`: http://pypi.python.org/pypi/modern-package-template
