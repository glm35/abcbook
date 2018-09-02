=======================
Idées de choses à faire
=======================

Structure des données d'entrée
==============================

::

   <tunebook root>/
       xxx-tunebook-template.lytex
       xxx-tunebook-tunes.txt
       xxx-tunebook-sets.txt
       tunes/
          *.abc
          *.ly
          *.tex
       build/
          <generated files>

Modifications à apporter:

- tout générer dans un unique répertoire build (au lieu des out.stage1 et
  out.stage2 actuels).

- mettre le template et les fichiers index à la racine pour simplifier
  la structure.

Paramétrage du build
====================

- nom du tunebook (eg 'cunla-tunebook')

- avec ou sans les notes au format .tex

Structure du tunebook
=====================

- pouvoir définir des sections "latex" dans le tunebook, par exemple
  "Airs sans suite".

Génération des partitions
=========================

- normaliser la casse des types de morceau (commence par une majuscule)

Fichiers d'entrée .abc, .ly et .tex
===================================

- supporter les caractères accentués sur toute la chaîne (à vérifier, c'est
  peut-être déjà le cas)

Index des tunes
===============

- un index par type de tune (reels, jigs, ..., divers)

Index des sets
==============

- pouvoir donner un nom à une suite. e.g. "The Oran Set"

- si tous les airs de la suite ont le même type, notation::

     "The Oran Set (reels): tune A, tune B"

- nom du set en italique

Discographie
============

- discographie: auteur (alphabétique) => album (par année) => liste des
  airs + type et numéro de page

Statistiques
============

- statistiques (nombre d'airs, nombres d'airs par type, nombre d'airs
  par compositeur, ...)

- liste des airs qui ne sont pas dans une suite
