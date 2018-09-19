========================================
Installing abcbook (development version)
========================================

Install Python3
---------------

Under Linux Mint::

   $ sudo apt install python3 python3-venv

Under Fedora (26)::

   $ sudo dnf install python3 python3-pip


Install Sphinx
--------------

::

   $ pip3 install --user sphinx

Get abcbook source code
-----------------------

::

   $ cd ~/code
   $ git clone https://github.com/glm35/abcbook.git

Build the doc
-------------

::

   $ cd ~/code/abcbook/docs
   $ make html
