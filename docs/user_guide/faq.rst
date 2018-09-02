=====================
Questions et réponses
=====================

Comment saisir au clavier les caractères accentués gaéliques?
=============================================================

Pour saisir des caractères gaeliques avec Emacs: sélectionner la méthode
de saisie "irish-prefix" avec::

   M-x set-input-method RET irish-prefix

Emacs affiche le mode de saisie dans la barre d'état en bas à
gauche. Pour le gaelique, on voit "GA>".

Exemple d'utilisation (Bríd Harper's): pour écrire í, taper ' puis i.

.. note:: le caractère irlandais passe bien la conversion en Python
   ainsi que le passage par lilypond.
