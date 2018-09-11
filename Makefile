# Install abcbook and its dependencies

SHELL = /bin/bash
# Note: by default, GNU Make uses /bin/sh which is /bin/dash on Debian
# systems, which causes some surprises with the commands. For instance,
# stdout+stderr IO redirection with "&>" does not work with dash.


#
# Paths for abcbook and its dependencies
#
# rem: system_local_latex_packages_dir may vary across systems, eg:
# - Mint: system_local_latex_packages_dir=/usr/local/share/texmf/tex/latex
# - Fedora 28: system_local_latex_packages_dir:=/usr/local/texlive/texmf-local/tex/latex/
#

local_share_abcbook_dir = ~/.local/share/abcbook
local_bin_dir = ~/.local/bin
system_local_latex_packages_dir := $(shell kpsewhich -var-value TEXMFLOCAL)/tex/latex


#
# Packages for abcbook
#

MINT_PACKATES = texlive texlive-lang-french lilypond xreader

FEDORA_PACKAGES = texlive-scheme-basic texlive-collection-fontsrecommended \
                  texlive-collection-langfrench lilypond xreader


#
# Install abcbook dependencies
#

install-deps-mint : install-mint-packages ${system_local_latex_packages_dir}/gchords.sty abc4ly

install-mint-packages :
	@echo [APT] Install abcbook dependencies for Mint
	apt install ${MINT_PACKAGES}

install-deps-fedora : install-fedora-packages ${system_local_latex_packages_dir}/gchords.sty abc4ly

install-fedora-packages :
	@echo [DNF] Install abcbook dependencies for Fedora
	dnf install ${FEDORA_PACKAGES}

${system_local_latex_packages_dir}/gchords.sty:
	@echo [INSTALL] gchords.sty system-wide
	mkdir -p ${system_local_latex_packages_dir}
	cp third-party/gchords/gchords.sty ${system_local_latex_packages_dir}
	texhash

abc4ly :
	@which abc4ly.py >& /dev/null || echo YOU MUST INSTALL ABC4LY MANUALLY


#
# Install abcbook
#

install-local : ${local_share_abcbook_dir} ${local_bin_dir}
	@echo [INSTALL] abcbook for local user
	rm -f ${local_bin_dir}/gen_tex_tunebook.py 
	rm -f ${local_share_abcbook_dir}/abcbook.mk
	cp buildtools/gen_tex_tunebook.py ${local_bin_dir}
	cp buildtools/abcbook.mk ${local_share_abcbook_dir}

install-devel-local : ${local_share_abcbook_dir} ${local_bin_dir}
	@echo [INSTALL] devel version of abcbook for local user
	rm -f ${local_bin_dir}/gen_tex_tunebook.py 
	rm -f ${local_share_abcbook_dir}/abcbook.mk
	ln -sr buildtools/gen_tex_tunebook.py ${local_bin_dir}
	ln -sr buildtools/abcbook.mk ${local_share_abcbook_dir}

${local_share_abcbook_dir} :
	mkdir -p ${local_share_abcbook_dir}

${local_bin_dir} :
	mkdir -p ${local_bin_dir}


#
# Clean & help
#

clean :
	@echo [CLEANING]
#	@-rm -rf ${stage1_outdir}

help :
	@echo "Targets:"
	@echo "    install-deps-mint: install abcbook dependencies on Linux Mint (needs root access)"
	@echo "    install-deps-fedora: install abcbook dependencies on Fedora (needs root access)"
	@echo "    install-local: install abcbook for the local user"
	@echo "    install-devel-local: install devel version of abcbook for local user"
	@echo "    clean: remove all the generated files"

