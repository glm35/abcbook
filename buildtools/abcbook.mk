SHELL=/bin/bash
# Note: by default, GNU Make uses /bin/sh which is /bin/dash on Debian
# systems, which causes some surprises with the commands. For instance,
# stdout+stderr IO redirection with "&>" does not work with dash.

#TODO: for each step: give the name of the log file

#TODO: be more consistent with variable reference: use {} or () but not both

# ------------------------------------------------------------------------ 
#     User-configurable parameters
# ------------------------------------------------------------------------ 

# Base name of the tune book file name, without extension.
# Defaults to "tunebook".
BOOKNAME ?= tunebook


# ------------------------------------------------------------------------ 
#     General parameters
#     /!\ Some of them are hard-coded in gen_tex_tunebook.py
# ------------------------------------------------------------------------ 

LILYPOND_BOOK=lilypond-book
ABC2LY=abc4ly.py
#CONVERT_LY=convert-ly
#TODO: warn if abc4ly or gen_tex_tunebook is missing

build_outdir = _build
stage1_outdir = ${build_outdir}/out.stage1
stage2_outdir = ${build_outdir}/out.stage2
src = tunes


# ------------------------------------------------------------------------ 
#     Receipes
# ------------------------------------------------------------------------ 

lyfiles := $(patsubst ${src}/%.abc,${stage1_outdir}/%.ly,$(wildcard ${src}/*.abc))
lyfiles2 := $(patsubst ${src}/%.ly,${stage1_outdir}/%.ly,$(wildcard ${src}/*.ly))
texfiles := $(wildcard ${src}/*.tex)

${stage2_outdir}/$(BOOKNAME).dvi : ${stage1_outdir} ${stage2_outdir} ${stage2_outdir}/${BOOKNAME}.tex ${stage2_outdir}/lilypond-book.log
	@echo [LATEX -- PASS 1] ${BOOKNAME}.lytex \(see error in ${stage2_outdir}/${BOOKNAME}.log\)
	@cd ${stage2_outdir} && latex -halt-on-error -interaction=batchmode ${BOOKNAME}.tex > latex1.log
	@echo [LATEX -- PASS 2] ${BOOKNAME}.lytex \(see error in ${stage2_outdir}/${BOOKNAME}log\)
	@cd ${stage2_outdir} && latex -interaction=batchmode ${BOOKNAME}.tex > ${BOOKNAME}.log
# Note: we call LaTeX twice to get the cross refs right (index)
# Note 2: we add the dependency to lilypond-book.log because sometimes
# lilypond-book just updates the files included in
# ${stage2_outdir}/${BOOKNAME}.tex. Looking at the log file shows that
# lilypond-book was run and that latex is (probably) to be run again.

${stage2_outdir}/${BOOKNAME}.tex : ${stage1_outdir}/${BOOKNAME}.lytex ${lyfiles} ${lyfiles2}
	@echo [LILYPOND-BOOK `${LILYPOND_BOOK} --version`] -o ${stage2_outdir}/${BOOKNAME}.tex ${stage1_outdir}/${BOOKNAME}.lytex
	cd ${stage2_outdir} && ${LILYPOND_BOOK} ../../${stage1_outdir}/${BOOKNAME}.lytex &> lilypond-book.log

${stage1_outdir}/%.ly : ${src}/%.ly
#	@echo [CONVERT-LY] $<
#	@${CONVERT_LY} $< > $@ 2>${stage1_outdir}/convert-ly.log
	@echo [CP] $<
	@cp $< $@
# Note: convert-ly looses the encoding (uses UTF-8?)
# Note: invoking convert-ly does not work when the input version is the same
# as the output version

${stage1_outdir}/%.ly : ${src}/%.abc
	@echo [ABC2LY] $<
	@${ABC2LY} -o $@ $< 2>${stage1_outdir}/abc2ly.log
	@cat ${stage1_outdir}/abc2ly.log |grep Warning |grep -v "Q specification" || true
# Note:
# - split into two commands to be able to filter abc2ly output without losing
# the return code
# - we don't care about grep return code

${stage1_outdir}/${BOOKNAME}.lytex: ${lyfiles} ${lyfiles2} ${texfiles} \
                                  ./bookspecs/book_template.tex ./bookspecs/tune_files.txt ./bookspecs/tune_sets.txt \
                                  ./bookspecs/guitar_chords.tex
	@echo [GEN-TEX-TUNEBOOK]
	gen_tex_tunebook.py --name ${BOOKNAME}

${build_outdir} :
	@echo [MKDIR] ${build_outdir}
	@mkdir ${build_outdir}

${stage1_outdir} : ${build_outdir}
	@echo [MKDIR] ${stage1_outdir}
	@mkdir ${stage1_outdir}

${stage2_outdir} : ${build_outdir}
	@echo [MKDIR] ${stage2_outdir}
	@mkdir ${stage2_outdir}

ps: ${stage2_outdir}/$(BOOKNAME).ps
# Note: It's better to use PostScript than pdf. As a matter of fact, the #'s
# (sharps) of LilyPond chordnames are lost during the call to dvipdf

${stage2_outdir}/$(BOOKNAME).ps : ${stage2_outdir}/$(BOOKNAME).dvi
	@echo [DVIPS] ${BOOKNAME}.dvi
	@cd ${stage2_outdir} && dvips -o ${BOOKNAME}.ps ${BOOKNAME}.dvi

pdf: ${stage2_outdir}/$(BOOKNAME).pdf

${stage2_outdir}/$(BOOKNAME).pdf : ${stage2_outdir}/$(BOOKNAME).ps
	@echo [PS2PDF] ${BOOKNAME}.ps
	@cd ${stage2_outdir} && ps2pdf -sPAPERSIZE=a4 $(BOOKNAME).ps
#	@cd ${stage2_outdir} && dvipdf ${BOOKNAME}.dvi
# dvipdf: prb: sortie "US letter" au lieu de "A4".
# dvips cunla.dvi && ps2pdf -sPAPERSIZE=a4 cunla.ps

# ------------------------------------------------------------------------ 
#     View the tunebook
# ------------------------------------------------------------------------ 

view: ${stage2_outdir}/$(BOOKNAME).dvi
	@echo [XDVI] ${stage2_outdir}/$(BOOKNAME).dvi
	@xdvi ${stage2_outdir}/$(BOOKNAME).dvi &

viewps: ${stage2_outdir}/$(BOOKNAME).ps
	@echo [XREADER] ${stage2_outdir}/$(BOOKNAME).ps
	@xreader ${stage2_outdir}/$(BOOKNAME).ps &

viewpdf: ${stage2_outdir}/$(BOOKNAME).pdf
	@echo [XREADER] ${stage2_outdir}/$(BOOKNAME).pdf
	@xreader ${stage2_outdir}/$(BOOKNAME).pdf &


# ------------------------------------------------------------------------ 
#     Chord table
# ------------------------------------------------------------------------ 

table: ${stage2_outdir}/chord_table.dvi

${stage2_outdir}/chord_table.dvi: ${stage2_outdir} bookspecs/chord_table.tex bookspecs/guitar_chords.tex
	@echo [LATEX] bookspecs/chord_table.tex
	@cd ${stage2_outdir} && latex bookspecs/chord_table.tex

# View chord table
vtable: ${stage2_outdir}/chord_table.dvi
	@echo [XDVI] ${stage2_outdir}/chord_table.dvi
	@xdvi ${stage2_outdir}/chord_table.dvi &


# ------------------------------------------------------------------------ 
#     Clean, archive, help
# ------------------------------------------------------------------------ 

clean :
	@echo [CLEANING]
	-rm -rf ${stage1_outdir}
	-rm -rf ${stage2_outdir}
	-rm -f src/*.mid
	-rm -f *~
	-rm -f src/*~
	-rm -f doc/*~

arch:
	@echo [ARCHIVING]
	@tar cvfj save/${BOOKNAME}-`date "+%Y%m%d-%Hh%M"`.tar.bz2 bugs/* doc/* Makefile src/* tools/*
#	@gzip ${BOOKNAME}-`date "+%Y%m%d-%Hh%M"`.tar
#	@mv *.tar.gz save

arch2:
	@echo [ARCHIVING v2]
	@tar cvfj ../${BOOKNAME}-`date "+%Y%m%d-%Hh%M"`.tar.bz2 ../tunebook --exclude=out*

help:
	@echo "Targets to build the book:"
	@echo "        default: dvi format"
	@echo "        ps: Postcript format"
	@echo "        pdf: pdf format (broken output: use ps)"
	@echo "Other targets:"
	@echo "        view: view the book in dvi format"
	@echo "        viewpdf: view the book in PDF format"
	@echo "        viewps: view the book in PostScript format"
	@echo "        table: build the chord table"
	@echo "        vtable: view the chord table"
	@echo "        clean: remove all the generated files"
	@echo "        arch: create an archive with the source and doc files"
	@echo "        arch2: create an archive with all but the out* directories"
