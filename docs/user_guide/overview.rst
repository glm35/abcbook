=================
Aperçu de abcbook
=================

abcbook permet de générer un recueil de partitions au format PDF à partir d'un
ou de plusieurs fichiers au format ABC, lilypond ou LaTeX.

abcbook s'appuie sur lilypond et LaTeX.

abcbook génère automatiquement un index des tunes.  abcbook permet aussi de
décrire des suites de tunes.

Index des tunes
===============

- L'index est construit automatiquement.

- Les tunes sont classés par ordre alphabétique après mise en retrait du
  déterminant à la fin du tune. Par exemple, "The Yellow Tinker" devient
  "Yellow Tinker, The".

- L'index est présenté sur 2 colonnes.

- Le nom du morceau est en italique.

Format d'une entrée de l'index::

   nom[, déterminant] (type) page

Exemple::

   Yellow Wattle, The (Jig) p.37


Index des sets
==============

- S'il y a au moins deux tunes dans le set et si tous les tunes du set de ont
  le même type, le type de tune est écrit en premier. Exemple::

     Jigs: Father O'Flynn (p.12), Brid Harper's (p.12)

- Sinon, le type de chaque tune est placé après le tune. Exemple::

     Humours of Ballylaughlin (jig, p.15) / Four Courts (reel, p.16)
