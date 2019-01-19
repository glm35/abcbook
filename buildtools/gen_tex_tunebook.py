#!/usr/bin/python3
# -*- coding:utf-8 -*-

# Imports from the Python Standard Library:
import logging
from optparse import OptionParser
from pathlib import Path
import re
import sys
from typing import List

# Imports from the project library:
from abcparser import Tune, parse_abc_file


# ------------------------------------------------------------------------
# Global variables
# ------------------------------------------------------------------------

TUNE_SETS_FILENAME = 'bookspecs/tune_sets.txt'

CLI_OPTIONS = None
CLI_ARGS = None


# ----------------------------------------------------------------------------
#     Entry point & CLI arguments parsing
# ----------------------------------------------------------------------------

def main():
    global CLI_OPTIONS
    global CLI_ARGS

    (CLI_OPTIONS, CLI_ARGS) = parse_command_line()
    setup_logging()

    book_path = Path(CLI_OPTIONS.output_dir)
    book_path = book_path.joinpath(CLI_OPTIONS.bookname + '.lytex')
    gen_book(book_path, Path(CLI_OPTIONS.tune_file_list))


def parse_command_line():
    parser = OptionParser()
    parser.add_option('-b', '--bookname', dest='bookname', default='tunebook',
                      help='set the tunebook name')
    parser.add_option('-o', '--output-dir', dest='output_dir', type=str,
                      default='_build/out.stage1',
                      help='directory to write the lilypond book '
                           'and read the lilypond files')
    parser.add_option('-t', '--template', dest='template', type=str,
                      default='bookspecs/book_template.tex',
                      help='path to the tunebook TeX template file')
    parser.add_option('-f', '--tune-file-list', dest='tune_file_list', type=str,
                      default='bookspecs/tune_files.txt',
                      help='path to the file with the list of ABC and lilypond '
                           'files to add to the book.')
    parser.add_option('-d', '--debug',
                      help='show debug messages',
                      action='store_true')
    parser.add_option('-v', '--verbose', action='store_true',
                        help='verbosity level')
    (options, args) = parser.parse_args()
    return options, args


def setup_logging():
    if CLI_OPTIONS.debug:
        logging_level = logging.DEBUG
    elif CLI_OPTIONS.verbose:
        logging_level = logging.INFO
    else:
        logging_level = logging.WARNING
    logging.basicConfig(level=logging_level, format='<%(levelname)s> %(message)s')


# ------------------------------------------------------------------------
#     Generate the book
# ------------------------------------------------------------------------

def gen_book(book_path: Path, tune_files_path: Path):
    """
    Generate a tunebook in LilyPond book format.

    Args:
        book_path: path of the tunebook to be generated

        tune_files_path: path of the text file containing the list of
            tune files to be incorporated in the tunebook.

    Returns:
        None
    """

    tune_file_paths = read_tune_file_list(tune_files_path)

    with open(CLI_OPTIONS.template, 'r') as f:
        template = f.readlines()

    with open(book_path, 'w') as f:
        # Step 1: copy template lines until %%INSERT_TUNES to tunebook
        f.writelines(eat_up_template(template, '%%INSERT_TUNES\n'))

        # Step 2: insert tunes in tunebook
        tunes = []  # List of Tune objects
        for path in tune_file_paths:
            new_tunes = []

            if path.suffix == '.abc':
                # Here we process each ABC file as if it contained
                # several tunes, even if abcbook.mk can actually deal with
                # only one multi-tune ABC file.
                new_tunes = parse_abc_file(path)

                if book_path.stem != path.stem:
                    # We are not processing the main ABC file, so we should
                    # have a single-tune abc file: we will
                    # do a few checks to help troubleshooting when
                    # lilypond-book fails.

                    if len(new_tunes) == 0:
                        logging.warning('No tune in ABC file: %s', path)
                    elif len(new_tunes) == 1:
                        if new_tunes[0].label != path.stem:
                            logging.warning('ABC file name does not match '
                                            'ABC tune title: %s', path)
                            logging.warning('    (should be: %s)',
                                            path.parent /
                                            Path(new_tunes[0].label + '.abc'))
                    else:
                        logging.warning('More than one tune in ABC file: %s',
                                        path)

            elif path.suffix == '.ly':
                title, tune_type = get_lilypond_tune_metadata(path)
                new_tunes.append(Tune(title, tune_type, path=path))

            else:
                logging.error('Unsupported tune file type for: %s', path)
                logging.error('--- Supported types: ABC (.abc), LilyPond (.ly)')
                sys.exit(1)

            for tune in new_tunes:
                assert_tune_uniqueness(new_tune=tune, tunes=tunes)
                tunes.append(tune)
                f.writelines(gen_tune(tune.label, tune.title, tune.type))

        # Step 3: copy template lines until %%INSERT_INDEX to tunebook
        f.writelines(eat_up_template(template, '%%INSERT_INDEX\n'))

        # Step 4: generate index of tunes and write it to tunebook
        f.write('\\twocolumn\n')
        f.write(gen_index_of_tunes(tunes))

        # Step 5: generate index of sets and write it to tunebook
        f.writelines(gen_index_of_sets(TUNE_SETS_FILENAME, tunes))

        # Step 6: copy remaining template lines to tunebook
        f.writelines(eat_up_template(template))


def read_tune_file_list(tune_files_path: Path) -> List[Path]:
    """
    Read the file containing the list of music files (ABC, LilyPond) and
    return the list.

    Args:
        tune_files_path: path to he file containing the list

    Returns:
        A list of tune file paths
    """
    file_paths = []
    with open(tune_files_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line != '' and line[0] != '#':
                file_paths.append(Path(line))
    return file_paths


def eat_up_template(template, tag=None):
    data = []
    while template:
        line = template.pop(0)
        if (line == tag):
            break
        data.append(line)
    return data


def assert_tune_uniqueness(new_tune: Tune, tunes: List[Tune]):
    """
    Check that a tune is not already present in a list of tunes and stop
    the program with an explanatory error if so.

    The check is based on the uniqueness of tune labels.  In some cases,
    different tune titles could lead to same labels

    Args:
        new_tune: tune that should not be already in list of tunes
        tunes: list of tunes

    Returns:
        None
    """
    for tune in tunes:
        if tune.label == new_tune.label:
            logging.error('Found two tunes with same label (~ title):')
            logging.error('--- "%s" in %s', tune.title, tune.path)
            logging.error('--- "%s" in %s', new_tune.title, new_tune.path)
            sys.exit(1)


# ------------------------------------------------------------------------
#     LilyPond file parser
# ------------------------------------------------------------------------

def get_lilypond_tune_metadata(filepath: Path):
    """
    Find the title and optionally the type of a tune in a LilyPond file.
    Abort program execution if the file cannot be opened or if there is
    no title in the file.

    Args:
        filepath: path of the LilyPond tune file

    Returns:
        A tuple (title, tune_type)
        Depending on what is found, title and/or type can be None
    """
    title, tune_type = None, None

    try:
        with open(filepath, 'r') as f:
            title_re = re.compile('^\s*title\s*=\s*"(.*)"$')
            type_re = re.compile('^\s*meter\s*=\s*"(.*)"$')

            for line in f.readlines():
                if title and tune_type:
                    break

                if not title:
                    m = title_re.match(line)
                    if m:
                        title = m.group(1).strip()
                        continue

                if not tune_type:
                    m = type_re.match(line)
                    if m:
                        tune_type = m.group(1).strip().lower()
                        continue

    except FileNotFoundError:
        logging.error('File not found: %s', filepath)
        sys.exit(1)

    if title is None:
        logging.error('Missing tune title in LilyPond file: %s', filepath)
        sys.exit(1)

    return title, tune_type


# ------------------------------------------------------------------------
#     Generate individual tunes
# ------------------------------------------------------------------------

def gen_tune_header(title, type=None):
    #header = ["\n\n\\pagebreak\n", "\\section{" + title, "}\n"]
    #header = ["\n\n", "\\section{" + title, "}\n"]
    #if type != None:
    #    header.insert (2, " (" + type + ")")
    #return "".join(header)
    #header = "\\paragraph{}\n\\begin{figure}[p]\n"
    header = '\\begin{figure}[H]\n'
    return header


def gen_tune_label(label):
    tex_label = ['\\label{', label, '}\n']
    return ''.join(tex_label)


def gen_lilypond_block(label):
    block = []
    block.append('\\begin{lilypond}\n')
    #block.append('\\paper {\n')
    #block.append('  bookTitleMarkup = \\markup {\n')
    #block.append('    \\fill-line {\n')
    ## append an empty string to have the composer right aligned:
    #block.append('      ""\n')
    #block.append('      \\fromproperty #\'header:composer\n')
    #block.append('    }\n')
    #block.append('  }\n')
    #block.append('}\n')
    block.append('\\include "' + '../../' + CLI_OPTIONS.output_dir + '/' + label + '.ly' + '"' + "\n")
    block.append('\\end{lilypond}\n')
    block.append('\\end{figure}\n')
    #block.append('\\linebreak\n')
    #block.append('\\clearpage\n')

    return ''.join(block)


def gen_tune(label, title, tune_type):
    data = []
    data.append(gen_tune_header(title, tune_type))
    data.append(gen_tune_label(label))
#    try:
#        f = open(tune_dir + "/" + label + ".tex")
#        for line in f:
#            if line.strip() == '\\tune':
#                data.append(gen_lilypond_block(label))
#                continue
#            data.append(line)
#        f.close()
#    except IOError:
#        data.append(gen_lilypond_block(label))
    data.append(gen_lilypond_block(label))
    return data


# ------------------------------------------------------------------------
#     Generate the index of tunes
# ------------------------------------------------------------------------

def gen_index_of_tunes(tunes: List[Tune]):
    tunes.sort()
    latex_index = '\\section*{Index des airs}\n'
    for tune in tunes:
        latex_index += format_index_entry(tune) + '\n\n'
    return latex_index


def format_index_entry(tune: Tune) -> str:
    if tune.type is None or tune.type == '':
        entry = '\emph{{{0}}},~p.\pageref{{{1}}}'.format(
            tune.title_for_index, tune.label)
    else:
        # Example: \emph{Come Upstairs with Me}~(slip jig),~p.\pageref{come_upstairs_with_me}
        entry = '\emph{{{0}}}~({1}),~p.\pageref{{{2}}}'.format(
            tune.title_for_index, tune.type, tune.label)
    return entry


# ------------------------------------------------------------------------
#     Generate the index of sets
# ------------------------------------------------------------------------

def gen_index_of_sets(tune_sets_filename: str, tunes: List[Tune]) -> List[str]:
    """
    Build the index of tune sets

    Args:
        tune_sets_filename: name of the file that contains the list of sets

        tunes: list of tunes in tunebook

    Returns:
        A list of lines in LaTeX format to be added to the tunebook.  If no
        tune set can be found, return an empty list.
    """
    try:
        f = open(tune_sets_filename)
    except:
        logging.warning('Cannot open: %s', tune_sets_filename)
        logging.warning('---- I will not generate an index of sets')
        return []

    data = []
    data.append('\\onecolumn\n')
    data.append('\n\n')
    #data.append('\\pagebreak\n')
    data.append('\\section*{Index des suites}\n')

    nb_of_sets = 0
    for lineno, line in enumerate(f, start=1):
        # Each line contains a comma separated list of labels.
        # A line can be empty
        # A line can be a comment starting with #
        line = line.strip()
        if line == '':
            continue
        if line[0] == '#':
            continue
        (set_title, set_tunes) = split_title_and_tunes(line)
        tunes_in_set = []
        for label in set_tunes.split(','):
            label = label.strip()
            try:
                tune = [tune for tune in tunes if tune.label == label][0]
                tunes_in_set.append(tune)
            except IndexError:
                logging.warning('%s:%d: no tune match label: %s',
                                tune_sets_filename, lineno, label)
        index_entry = format_set_index_entry(tunes_in_set, set_title)
        data.append(index_entry + '\n\n')
        nb_of_sets += 1

    f.close()

    if nb_of_sets == 0:
        logging.warning('No set in tune sets file: %s', tune_sets_filename)
        logging.warning('--- I will not generate an index of sets')
        return []
    else:
        return data


def split_title_and_tunes(index_entry):
    if -1 == index_entry.find(':'):
        # No title
        return ('', index_entry.strip())

    l = index_entry.split(':')
    tunes = l[1].strip()
    title = l[0].strip()
    return (title, tunes)


def format_set_index_entry(tunes_in_set: List[Tune], title=''):
    entry = ''

    # Do all the tunes have the same type?
    same_type = True
    set_type = ''
    for tune in tunes_in_set:
        if tune.type is None:
            tune.type = ''
        if set_type == '':
            set_type = tune.type
        else:
            if set_type != tune.type:
                same_type = False
                break

    if title != '':
        entry = '\emph{' + title + '}'

    factorize_type = False
    if len(tunes_in_set) >= 2:
        if same_type and set_type != '':
            if title != '':
                entry += ' (' + set_type.lower() + 's' + ')'
            else:
                entry += set_type.capitalize() + 's'
            factorize_type = True

    if title != '' or factorize_type:
        entry += ': '

    first_tune = True
    for tune in tunes_in_set:
        tune_ref = '\emph{' + tune.title + '}'
        tune_ref += '~('
        if tune.type != '' and tune.type != None and not factorize_type:
            tune_ref += tune.type + ',~'
        tune_ref += 'p.\pageref{' + tune.label + '}'
        tune_ref += ')'
        if not first_tune:
            entry += '~/ '
        first_tune = False
        entry += tune_ref
    return entry


# ------------------------------------------------------------------------
# ------------------------------------------------------------------------

if __name__ == '__main__':
    main()
