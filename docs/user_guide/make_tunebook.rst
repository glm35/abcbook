================================
Générer un recueil de partitions
================================

Version courte::

   $ cd /chemin/vers/my_tunebook
   $ make pdf

Le recueil de partitions est généré dans le fichier:
``/chemin/vers/my_tunebook/_build/out.stage2/my_tunebook.pdf``

D'autres options de génération sont possibles, notamment:

   * générer uniquement le tunebook au format DVI: plus rapide, utile en phase
     de mise au point::

      $ make

   * générer le PDF et le visualiser dans la foulée::

      $ make viewpdf

Et pour voir toutes les facilités offertes par le Makefile, faire::

   $ make help
