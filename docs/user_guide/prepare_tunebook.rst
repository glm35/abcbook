=================================
Préparer un recueil de partitions
=================================

On prend ici l'exemple d'un recueil appelé "My Tunebook", et toutes les
références au nom de code "my_tunebook" peuvent être personnalisées.


Structure des fichiers et répertoires
=====================================

Les fichiers source du tunebook doivent être placés dans un répertoire
dédié et structuré de la manière suivante::

   my_tunebook/
      my_tunebook.abc    # fichier ABC principal (multi-tune)
      tunes/    # fichiers mono-tune et notes:
         *.abc  # tunes au format ABC (un seul tune par fichier)
         *.ly   # tunes au format LilyPond
         *.tex  # notes pour un tune (format LaTeX)
      bookspecs/
         book_template.tex   # modèle de document
         tune_files.txt      # liste des fichiers musicaux
         tune_sets.txt       # liste des sets
         guitar_chords.tex   # diagrammes d'accord au format gchords
         chord_table.tex     # tableau des accords
      Makefile


Makefile
========

Il faut créer un ``Makefile`` qui permettra la génération du tunebook.
Ce Makefile contient deux lignes. Exemple::

   BOOKNAME = my_tunebook
   include ~/.local/share/abcbook/abcbook.mk

``BOOKNAME`` est le nom de code du tunebook. Il doit correspondre au nom de
fichier ABC principal.

Il faut ensuite inclure ``abcbook.mk``, le makefile qui va réellement se
charger de la génération du tunebook. Par défaut, ce makefile est installé vers:
``~/.local/share/abcbook/abcbook.mk``


Modèle de document
==================

abcbook s'appuie sur LaTeX pour générer un recueil de partition.

``bookspecs/book_template.tex`` est un document LaTeX qui décrit la structure
du recueil de partitions. Il contient deux "balises"
spéciales pour abcbook. Ces balises sont implémentées sous forme de
commentaires LaTeX et doivent être chacunes sur une seule ligne:

   * ``%%INSERT_TUNES``: marque l'endroit où abcbook va placer l'ensemble
     des airs.

   * ``%%INSERT_INDEX``: marque l'endroit où abcbook va placer l'index
     des airs puis l'index des suites.

Voici un exemple de template minimaliste::

   \documentclass[a4paper,12pt]{article}

   \usepackage[frenchb]{babel}
   \usepackage[T1]{fontenc}
   \usepackage[utf8]{inputenc}
   \usepackage[hmargin=2cm]{geometry}
   \usepackage{float}

   \author{My Name}
   \title{My Tunebook}
   \date{\today}

   \begin{document}
   \maketitle
   This is my tunebook. It is full of tunes I like.

   \pagebreak
   %%INSERT_TUNES

   \clearpage
   %%INSERT_INDEX

   \end{document}

Pour pouvoir mettre des accords de guitare dans les fichiers de notes,
inclure aussi dans le template le package ``gchords``::

   \usepackage{gchords}


Liste des fichiers des tunes
============================

abcbook ne cherche pas automatiquement les fichiers des airs au format ABC ou
LilyPond à inclure dans le recueil: il faut lui donner la liste.  Cela permet
de contrôler l'ordre des morceaux et de mettre de côté certains fichiers
lors de la mise au point du recueil.

``bookspecs/tune_files.txt`` contient la liste des fichiers à prendre en
compte.

Exemple::

   tunes/yellow_tinker.abc
   tunes/out_on_the_ocean.abc
   tunes/the_miller_s_maggot.ly
   tunes/the_lark_on_the_strand.abc
   my_tunebook.abc

Règles pour l'écriture du fichier ``bookspecs/tune_files.txt``:

   * Les chemins de fichier sont relatifs au répertoire du tunebook.

   * Les seules extensions reconnues et acceptées sont .abc et .ly.

   * Un seul fichier par ligne.

   * Les lignes vides sont ignorées.

   * Une ligne introduite par le symbole # est un commentaire: la ligne est
     ignorée.

   * Un seul fichier peut contenir plusieurs tunes: le fichier ABC multi-tune
     principal.  Il peut être placé n'importe où dans la liste.


Liste des suites de tunes
=========================

abcbook permet de générer un index contenant des suites de tunes.  Les suites
doivent être listées dans ``bookspecs/tune_sets.txt``. La présence de ce fichier
est obligatoire, mais le fichier peut être vide.

Règles pour l'écriture du fichier des listes de suites:

   * Chaque ligne contient une liste de suites.

   * Les lignes vides sont ignorées.

   * Une ligne introduite par le symbole # est un commentaire: la ligne est
     ignorée.

   * Une suite est définie par une séquence de labels de tunes, où chaque tune
     est séparé du précédent par une virgule.  Exemple::

      yellow_tinker, john_cawley_s, jack_maguire_s

   * Pour trouver le label d'un tune, voir :ref:`tune_labelling`.

   * On peut donner un nom à une suite.  Exemple::

      Kenmare Polka Set: andy_boyle_s, o_sullivan_s_fancy, the_upper_church


Tunes
=====

abcbook accepte les tunes au format ABC (.abc) et lilypond (.ly).  abcbook accepte
aussi des fragments de texte au format LaTeX, et ces fragments peuvent contenir
des éléments musicaux au format lilypond.

Nommage des fichiers
--------------------

Le nom de fichier d'un "single tune" doit correspondre au label du tune.  Par
exemple, un fichier ABC contenant le morceau "Crock of Gold" doit être placé
dans le fichier ``tunes/crock_of_gold.abc``.

.. _tune_labelling:


Trouver le label d'un tune
--------------------------

Pour trouver le label d'un tune:

   * prendre son titre,
   * mettre toutes les lettres en minuscules,
   * remplacer tous les caractères accentués par leur équivalent sans accent,
   * remplacer tous les espaces et caractères non alphanumériques par le
     caractère underscore _.

Exemples:

============================   ============================
Titre                          Label
============================   ============================
Crock of Gold                  crock_of_gold
Father Kelly's                 father_kelly_s
An Cailín Deas Crúite Na mBó   an_cailin_deas_cruite_na_mbo
============================   ============================


Conventions de style pour les fichiers ABC et lilypond
------------------------------------------------------

- Les titres sont écrits au format "title case", c'est à dire avec
  une majuscule en début de chaque mot sauf pour les articles et les formes
  du verbe être (
  http://en.wikipedia.org/wiki/Title_case#Headings_and_publication_titles)

- Un type de morceau (Reel, Jig) commence par une majuscule (champ
  informatif R: en abc, champ meter en lilypond).

- Quand le compositeur n'est pas connu, il vaut "Trad." à condition que ce
  status soit à peu près avéré.


Edition des fichiers ABC
------------------------

Convention de format pour les références discographiques
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

   D:Auteur, "Titre", Année

Exemple::

   D:Nuala Kennedy, "The New Shoes", 2007


Edition des fichiers lilypond
-----------------------------

.. warning:: utiliser le format ABC de préférence, car ses spécifications
   sont plus stables que le format lilypond.  Utiliser lilypond en cas de
   problème bloquant avec ABC.

.. warning:: le format d'entrée pour les fichiers lilypond varie souvent
   ce qui nécessite l'utilisation du script de conversion ly->ly
   qui introduit ses propres problèmes.

Indiquer systématiquement la version lilypond en tête de fichier .ly.
Exemple::

   \version "2.11.23"

