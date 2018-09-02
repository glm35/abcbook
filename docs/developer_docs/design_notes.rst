===================
Notes de conception
===================

Génération du tunebook lilypond-book
====================================

Les tunes
---------

- titre, type de morceau et auteur sont générés par lilypond et ne sont pas
  dans le code latex du tunebook: un tune n'est pas une section latex.

L'index des tunes
-----------------

L'index des airs est affiché sur 2 colonnes
(http://texblog.wordpress.com/2007/08/11/creating-two-columns-in-article-report-or-book/)
en ne tenant pas compte du déterminant: "the", "a", ...

Longueur de la portée
---------------------

Pour définir la longueur de la portée:

- redéfinir les marges à l'aide du paquet latex "geometry"
- regénérer tout le livre

Remarque: dans mon cas, l'option line-width de lilypond-book ne
fonctionne pas (avec et sans ragged-margin)

Espacement vertical entre deux tunes
------------------------------------

Pour avoir un espacement vertical minimal raisonnable entre deux
morceaux: commencer un nouveau paragraphe à chaque morceau avec
\paragraph{}.

Conversion ABC vers LilyPond
============================

Même si le fichier .ly est généré automatiquement, il est utile d'avoir
un fichier le plus lisible possible:

- utile lors de la mise au point du convertisseur
- permet d'éditer manuellement plus simplement le .ly après conversion
  si cela est nécessaire (e.g. spécifier manuellement le groupement des
  notes).

Makefile
========

https://stackoverflow.com/questions/10164924/code-generation-and-make-rule-expansion

