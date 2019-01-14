# =============================================================================
#     abcbook.mk
#     ----------
#     Generic Makefile to generate a tunebook in PDF format from a set
#     of tunes in ABC and/or lilypond format.
# =============================================================================


# ------------------------------------------------------------------------ 
#     User-configurable parameters
# ------------------------------------------------------------------------ 

# Base name of the tune book file name, without extension.
# Defaults to "tunebook".
BOOKNAME ?= tunebook

# The following paths must be RELATIVE to the tunebook root directory
GUITAR_CHORDS ?= bookspecs/guitar_chords.tex
CHORD_TABLE ?= bookspecs/chord_table.tex


# ------------------------------------------------------------------------ 
#     General parameters
#     /!\ Some of them are hard-coded in gen_tex_tunebook.py
# ------------------------------------------------------------------------ 

SHELL = /bin/bash
    # Note: by default, GNU Make uses /bin/sh which is /bin/dash on Debian
    # systems, which causes some surprises with the commands. For instance,
    # stdout+stderr IO redirection with "&>" does not work with dash.
LILYPOND_BOOK = lilypond-book
ABC2LY = abc4ly.py

build_outdir = _build
stage1_outdir = $(build_outdir)/out.stage1
stage2_outdir = $(build_outdir)/out.stage2
abcsplit_outdir = $(build_outdir)/splitabc
src = tunes


# ------------------------------------------------------------------------ 
#     Rules
#     (in chronological order)
# ------------------------------------------------------------------------ 

include $(build_outdir)/splitabc.mk

lyfiles := $(patsubst $(src)/%.abc,$(stage1_outdir)/%.ly,$(wildcard $(src)/*.abc))
lyfiles2 := $(patsubst $(src)/%.ly,$(stage1_outdir)/%.ly,$(wildcard $(src)/*.ly))
lyfiles3 := $(patsubst $(abcsplit_outdir)/%.abc,$(stage1_outdir)/%.ly,$(SPLIT_ABC))
texfiles := $(wildcard $(src)/*.tex)

# The default rule:
dvi : $(stage2_outdir)/$(BOOKNAME).dvi

$(build_outdir) :
	@echo [MKDIR] $(build_outdir)
	@mkdir $(build_outdir)

$(stage1_outdir) : $(build_outdir)
	@echo [MKDIR] $(stage1_outdir)
	@mkdir $(stage1_outdir)

$(stage2_outdir) : $(build_outdir)
	@echo [MKDIR] $(stage2_outdir)
	@mkdir $(stage2_outdir)

$(build_outdir)/splitabc.mk : $(BOOKNAME).abc $(build_outdir)
	@echo [ABCSPLIT] $(BOOKNAME).abc
	abcsplit.py -o $(abcsplit_outdir) $(BOOKNAME).abc
	echo "SPLIT_ABC=`echo $(abcsplit_outdir)/*.abc`" > $(build_outdir)/splitabc.mk

$(stage1_outdir)/%.ly : $(src)/%.abc
	@echo [ABC2LY] $<
# We split the recipe into two commands to be able to filter abc2ly output
# without losing the return code:
	@$(ABC2LY) -o $@ $< 2>$(stage1_outdir)/abc2ly.log
	@cat $(stage1_outdir)/abc2ly.log |grep Warning \
            |grep -v "Q specification" || true

$(stage1_outdir)/%.ly : $(abcsplit_outdir)/%.abc
	@echo [ABC2LY] $<
# We split the recipe into two commands to be able to filter abc2ly output
# without losing the return code:
	@$(ABC2LY) -o $@ $< 2>$(stage1_outdir)/abc2ly.log
	@cat $(stage1_outdir)/abc2ly.log |grep Warning \
            |grep -v "Q specification" || true

$(stage1_outdir)/%.ly : $(src)/%.ly
	@echo [CP] $<
	@cp $< $@

lytex : $(stage1_outdir)/$(BOOKNAME).lytex

$(stage1_outdir)/$(BOOKNAME).lytex : $(BOOKNAME).abc \
                                     $(lyfiles) $(lyfiles2) $(texfiles) \
                                     bookspecs/book_template.tex \
                                     bookspecs/tune_files.txt \
                                     bookspecs/tune_sets.txt \
                                     $(GUITAR_CHORDS)
	@echo [GEN-TEX-TUNEBOOK]
	gen_tex_tunebook.py --bookname $(BOOKNAME) --output-dir $(stage1_outdir)

$(stage2_outdir)/$(BOOKNAME).tex : $(stage1_outdir)/$(BOOKNAME).lytex \
                                   $(lyfiles) $(lyfiles2) $(lyfiles3) \
                                   $(build_outdir)/splitabc.mk
	@echo [LILYPOND-BOOK `$(LILYPOND_BOOK) --version`] \
            -o $(stage2_outdir)/$(BOOKNAME).tex \
            $(stage1_outdir)/$(BOOKNAME).lytex
	@echo "(See error in $(stage2_outdir)/lilypond-book.log)"
	cd $(stage2_outdir) && \
            $(LILYPOND_BOOK) ../../$(stage1_outdir)/$(BOOKNAME).lytex \
            &> lilypond-book.log

$(stage2_outdir)/$(BOOKNAME).dvi : $(stage1_outdir) $(stage2_outdir) \
                                   $(stage2_outdir)/$(BOOKNAME).tex \
                                   $(stage2_outdir)/lilypond-book.log
# Note: we call LaTeX twice to get the cross refs right (index)
# Note 2: we add the dependency to lilypond-book.log because sometimes
# lilypond-book just updates the files included in
# $(stage2_outdir)/$(BOOKNAME).tex. Looking at the log file shows that
# lilypond-book was run and that latex is (probably) to be run again.
	@echo [LATEX pass 1] $(BOOKNAME).lytex \
            \(see error in $(stage2_outdir)/$(BOOKNAME).log\)
	@cd $(stage2_outdir) && latex -halt-on-error \
            -interaction=batchmode $(BOOKNAME).tex > latex1.log
	@echo [LATEX pass 2] $(BOOKNAME).lytex \
            \(see error in $(stage2_outdir)/$(BOOKNAME)log\)
	@cd $(stage2_outdir) && \
            latex -interaction=batchmode $(BOOKNAME).tex > $(BOOKNAME).log

ps : $(stage2_outdir)/$(BOOKNAME).ps

$(stage2_outdir)/$(BOOKNAME).ps : $(stage2_outdir)/$(BOOKNAME).dvi
	@echo [DVIPS] $(BOOKNAME).dvi
	@cd $(stage2_outdir) && dvips -o $(BOOKNAME).ps $(BOOKNAME).dvi

pdf : $(stage2_outdir)/$(BOOKNAME).pdf

$(stage2_outdir)/$(BOOKNAME).pdf : $(stage2_outdir)/$(BOOKNAME).ps
	@echo [PS2PDF] $(BOOKNAME).ps
	@cd $(stage2_outdir) && ps2pdf -sPAPERSIZE=a4 $(BOOKNAME).ps


# ------------------------------------------------------------------------ 
#     View the tunebook
# ------------------------------------------------------------------------ 

view : $(stage2_outdir)/$(BOOKNAME).dvi
	@echo [XDVI] $(stage2_outdir)/$(BOOKNAME).dvi
	@xdvi $(stage2_outdir)/$(BOOKNAME).dvi &

viewps : $(stage2_outdir)/$(BOOKNAME).ps
	@echo [XREADER] $(stage2_outdir)/$(BOOKNAME).ps
	@xreader $(stage2_outdir)/$(BOOKNAME).ps &

viewpdf : $(stage2_outdir)/$(BOOKNAME).pdf
	@echo [XREADER] $(stage2_outdir)/$(BOOKNAME).pdf
	@xreader $(stage2_outdir)/$(BOOKNAME).pdf &


# ------------------------------------------------------------------------ 
#     Chord table
# ------------------------------------------------------------------------ 

table : $(stage2_outdir)/chord_table.dvi

$(stage2_outdir)/chord_table.dvi : $(stage2_outdir) \
                                   $(CHORD_TABLE) $(GUITAR_CHORDS)
	@echo [LATEX] $(CHORD_TABLE)
	@cd $(stage2_outdir) && latex ../../$(CHORD_TABLE)

# View chord table
viewtable : $(stage2_outdir)/chord_table.dvi
	@echo [XDVI] $(stage2_outdir)/chord_table.dvi
	@xdvi $(stage2_outdir)/chord_table.dvi &


# ------------------------------------------------------------------------ 
#     Clean, archive, help
# ------------------------------------------------------------------------ 

clean :
	@echo [CLEANING]
	-rm -rf $(stage1_outdir)
	-rm -rf $(stage2_outdir)
	-rm -rf $(abcsplit_outdir)
	-rm -f $(build_outdir)/splitabc.mk
	-rm -f src/*.mid
	-rm -f *~
	-rm -f src/*~
	-rm -f doc/*~

tarball :
# Requires that the tunebook directory name is $(BOOKNAME)
	@echo [ARCHIVING]
	@tar cvfj $(BOOKNAME)-`date "+%Y%m%d-%Hh%M"`.tar.bz2 \
            --exclude=$(BOOKNAME)/_build \
            --exclude=$(BOOKNAME)/.git \
	    --exclude=*.tar.bz2 \
	    ../$(BOOKNAME)

help :
	@echo "Targets to build the book:"
	@echo "        default: dvi format"
	@echo "        ps: Postcript format"
	@echo "        pdf: pdf format (broken output: use ps)"
	@echo "Other targets:"
	@echo "        view: view the book in dvi format"
	@echo "        viewpdf: view the book in PDF format"
	@echo "        viewps: view the book in PostScript format"
	@echo "        table: build the chord table"
	@echo "        viewtable: view the chord table"
	@echo "        clean: remove all the generated files"
	@echo "        tarball: create an archive including tunes, bookspecs and pdf"

