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

- L'index des airs est affiché sur 2 colonnes
  (http://texblog.wordpress.com/2007/08/11/creating-two-columns-in-article-report-or-book/)
  en ne tenant pas compte du déterminant: "the", "a", ...

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


L'index des suites
------------------

- S'il y a au moins deux tunes dans le set et si tous les tunes du set de ont
  le même type, le type de tune est écrit en premier. Exemple::

     Jigs: Father O'Flynn (p.12), Brid Harper's (p.12)

- Sinon, le type de chaque tune est placé après le tune. Exemple::

     Humours of Ballylaughlin (jig, p.15) / Four Courts (reel, p.16)


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

Conversion LilyPond vers Lilypond
=================================

Historiquement::

   ${stage1_outdir}/%.ly : ${src}/%.ly
    @echo [CONVERT-LY] $<
    @${CONVERT_LY} $< > $@ 2>${stage1_outdir}/convert-ly.log

Problèmes:

* convert-ly looses the encoding (uses UTF-8?)
* invoking convert-ly does not work when the input version is the same
  as the output version

Aujourd'hui, plus de conversion, la règle réalise une simple copie.  A l'usage
sur plusieurs années (2005-2018), cela ne pose pas de problème.

Genération du PDF
=================

::

   dvi --dvips--> ps --dvipdf--> pdf

On ne génère pas directement le PDF à partir du DVI avec dvipdf.  Plusieurs
problèmes à l'usage si on le fait:

- les caractères # (dièse) des noms d'accord LilyPond sont perdus lors d'un
  appel à dvipdf;
- le format de la page est "US letter" au lieu de "A4".

Makefile
========

https://stackoverflow.com/questions/10164924/code-generation-and-make-rule-expansion

