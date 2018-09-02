==============================================
Fichiers d'entrée et structure des répertoires
==============================================

abcbook accepte les tunes au format ABC (.abc) et lilypond (.ly).  abcbook accepte
aussi des fragments de texte au format LaTeX, et ces fragments peuvent contenir
des éléments musicaux au format lilypond.


Structure des fichiers et répertoires
=====================================

Organisation du répertoire Tunebook::

   metadata/
      cunla-tunebook-sets.txt        # liste des sets
      cunla-tunebook-template.lytex  # modèle de document
      cunla-tunebook-tunes.txt       # liste des tunes
   tunes/
      *.abc  # tune au format ABC (format préféré)
      *.ly   # tune au format lilypond
      *.tex  # notes pour un tune au format LaTeX


Conventions de style pour les fichiers ABC et lilypond
======================================================

- Les titres sont écrits au format "title case", c'est à dire avec
  une majuscule en début de chaque mot sauf pour les articles et les formes
  du verbe être (
  http://en.wikipedia.org/wiki/Title_case#Headings_and_publication_titles)

- Un type de morceau (Reel, Jig) commence par une majuscule (champ
  informatif R: en abc, champ meter en lilypond).

- Quand le compositeur n'est pas connu, il vaut "Trad." à condition que ce
  status soit à peu près avéré.


Edition des fichiers ABC
========================

Format d'une entrée discographie
--------------------------------

::

   D:Auteur, "Titre", Année

Exemple::

   D:Nuala Kennedy, "The New Shoes", 2007


Edition des fichiers lilypond
=============================

.. warning:: utiliser le format ABC de préférence, car ses spécifications
   sont plus stables que le format lilypond.  Utiliser lilypond en cas de
   problème bloquant avec ABC.

.. warning:: le format d'entrée pour les fichiers lilypond varie souvent
   ce qui nécessite l'utilisation du script de conversion ly->ly
   qui introduit ses propres problèmes.

Indiquer systématiquement la version lilypond en tête de fichier .ly.
Exemple::

   \version "2.11.23"

