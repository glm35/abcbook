===========================
Instructions d'installation
===========================

Récupérer le code de abcbook
============================

Depuis radisnoir::

   $ cd ~/code
   $ git clone /home/gwen/code/git/abcbook.git/


Depuis une autre machine::

   $ cd ~/code
   $ git clone ssh://radisnoir/home/gwen/code/git/abcbook.git/


Installer les dépendances
=========================

abcbook utilise les logiciels suivants:

- Python3
- GNU make
- Sphinx pour la documentation
- LaTeX
- le paquet LaTeX gchords
- lilypond 2.11.26

Installer Python3 et make
-------------------------

Sous Linux Mint::

   $ sudo apt install python3 python3-venv make

Sous Fedora (26)::

   $ sudo dnf install python3 python3-pip make


Installer LaTeX, gchords et lilypond
------------------------------------

Sous Linux Mint::

   $ cd ~/code/abcbook
   $ sudo make install-deps-mint

Sous Fedora::

   $ cd ~/code/abcbook
   $ sudo make install-deps-fedora


.. note:: gchords

   Le paquet gchords https://kasper.phi-sci.com/gchords/ peut se retrouver
   à l'URL https://kasper.phi-sci.com/gchords/gchords.sty.
   J'en garde une copie avec le code de abcbook dans
   ``third-party/gchords/gchords.sty``, et c'est cette copie qui est installée
   à l'aide du Makefile.

   gchords est installée de la manière suivante dans la distribution LaTeX::

      # mkdir -p /usr/local/share/texmf/tex/latex
      # cp gchords.sty /usr/local/share/texmf/tex/latex
      # texhash


Installer abcbook
=================


Générer la documentation
========================

Install Sphinx
--------------

::

   $ pip3 install --user sphinx

Build the doc
-------------

::

   $ cd ~/code/abcbook/docs
   $ make html

Pour lire la doc générée, pointer un navigateur web sur le fichier
~/code/abcbook/docs/_build/html/index.html.
