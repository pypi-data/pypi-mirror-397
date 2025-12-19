Changes
=======

2.0.0 - 2025-12-17
------------------

* Change to be suitable for Mathics3:
  - use ``pyproject.toml`` for packaging
  - works on Python 3.10 to 3.14
  - uses Mathics3-style precommit hooks and editorconfig

* Change ``ALARM`` list to store absolute time rather than relative time
* Change name from ``stopit`` to ``Timed-Threads`` with module ``timed_threads``


1.1.2 - 2018-02-09
------------------

* Changed license to MIT
* Tested with Python 3.5 and 3.6

1.1.1 - 2015-03-22
------------------

* Fixed bug of timeout context manager as bool under Python 2.x
* Tested with Python 3.4

1.1.0 - 2014-05-02
------------------

* Added support for TIMER signal based timeout control (POSIX OS only)
* API changes due to new timeout controls
* An exhaustive documentation.

1.0.0 - 2014-02-09
------------------

Initial version
