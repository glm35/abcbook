===========================
Instructions d'installation
===========================

Dépendances
===========

- LaTeX
- lilypond 2.11.26
- Perl

gchords
=======

* http://www.aei.mpg.de/~peekas/gchords/
* en cache dans tunebook/tools/gchords/gchords.sty

::

   $ wget http://www.aei.mpg.de/~peekas/gchords/gchords.sty

Installation::

   # mkdir -p /usr/local/share/texmf/tex/latex
   # cp gchords.sty /usr/local/share/texmf/tex/latex
   # texhash
