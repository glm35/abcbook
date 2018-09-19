#!/usr/bin/python3

from functools import total_ordering
import sys
import re
from optparse import OptionParser
from pathlib import Path
import string


# TODO list
#
# 1. Refactor
# - obj_tunes vs tunes: keep only one with ordered dict
# - tune file vs tune label
# - other TODO's
#
# 2. Process each ABC file as a multi-tunes file
# - alternatively, or to begin with, only process files without the "tunes/"
# path as multi-tunes files

# ------------------------------------------------------------------------
# Global variables
# ------------------------------------------------------------------------

TUNE_SETS_FILENAME = "bookspecs/tune_sets.txt"

CLI_OPTIONS = None
CLI_ARGS = None


# ----------------------------------------------------------------------------
#     Entry point & CLI arguments parsing
# ----------------------------------------------------------------------------

def main():
    global CLI_OPTIONS
    global CLI_ARGS

    (CLI_OPTIONS, CLI_ARGS) = parse_command_line()

    book_path = Path(CLI_OPTIONS.output_dir)
    book_path = book_path.joinpath(CLI_OPTIONS.bookname + '.lytex')
    gen_book(book_path, Path(CLI_OPTIONS.tune_file_list))


def parse_command_line():
    parser = OptionParser()
    parser.add_option("-b", "--bookname", dest="bookname", default="tunebook",
                      help="set the tunebook name")
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
    (options, args) = parser.parse_args()
    return options, args


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

    # The dictionnary of tunes
    #
    # For each tune identified by its label, it contains the title and the
    # type of the tune.
    #
    # key: label
    # value: dictionnary that contains the data for the tune labelled by the
    # key:
    #    keys: "title", "type"
    tunes = {}  # TODO? use ordered dict to keep order?

    tune_file_paths = read_tune_file_list(tune_files_path)

    with open(CLI_OPTIONS.template, 'r') as f:
        template = f.readlines()

    with open(book_path, 'w') as f:
        # Step 1: copy template lines until %%INSERT_TUNES to tunebook
        f.writelines(eat_up_template(template, "%%INSERT_TUNES\n"))

        # Step 2: insert tunes in tunebook
        obj_tunes = []  # TODO: rename: what's the difference with the "tunes"
                        # global variable?
        for tune_file in tune_file_paths:
            # TODO: process each tune file as if it contained several tunes
            # (even if abcbook.mk can actually deal with only one multi-tune
            # ABC book).
            # Re-use the abcsplit logic (and even code) to do this
            title, tune_type = get_tune_metadata(tune_file)
            if title is None:
                print('Error: no title in tune: ' + str(tune_file))
                sys.exit(1)
            label = title_to_id(title)
            tunes[label] = {'title': title, 'type': tune_type}
            obj_tunes.append(Tune(label, title, tune_type))
            f.writelines(gen_tune(label, title, tune_type))

        # Step 3: copy template lines until %%INSERT_INDEX to tunebook
        f.writelines(eat_up_template(template, "%%INSERT_INDEX\n"))

        # Step 4: generate index of tunes and write it to tunebook
        f.write("\\twocolumn\n")
        f.write(gen_index_of_tunes(obj_tunes))

        # Step 5: generate index of sets and write it to tunebook
        f.write("\\onecolumn\n")
        f.writelines(gen_index_of_sets(tunes))

        # Step 6: copy remaining template lines to tunebook
        f.writelines(eat_up_template(template))


def read_tune_file_list(tune_files_path):
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


# ------------------------------------------------------------------------
# Tune object
# ------------------------------------------------------------------------

@total_ordering
class Tune:
    def __init__(self, label="", title="", type=""):
        self.label = label
        self.title = title
        self.type = type

    def __eq__(self, other):
        return self.title.lower() == other.title.lower()

    def __lt__(self, other):
        return self.title.lower() < other.title.lower()

    def __cmp__(self, other):
        x = self.title.lower()
        y = other.title.lower()
        if x > y:
            return 1
        elif x == y:
            return 0
        else:  #x < y
            return -1

    def __str__(self):
        return self.title

    def format_index_entry(self):
        if self.type == None or self.type == "":
            entry = "\emph{{{0}}},~p.\pageref{{{1}}}".format(self.title, self.label)
        else:
            # Example: \emph{Come Upstairs with Me}~(slip jig),~p.\pageref{come_upstairs_with_me}
            entry = "\emph{{{0}}}~({1}),~p.\pageref{{{2}}}".format(self.title, self.type, self.label)
        return entry


# ------------------------------------------------------------------------
#     Parse tunes, create tune id
# ------------------------------------------------------------------------

def get_tune_metadata(tune_path):
    """
    Find and return the title and type of tune found in the given
    tune file

    Args:
        tune_path: path of the ABC or LilyPond tune file

    Returns:
        a tuple (title, type)
    """
    title, type = None, None

    # TODO: refactor with ABC parser; use one function per type of file

    try:
        with open (tune_path, 'r') as f:
            tune = f.readlines()
    except FileNotFoundError:
        print('Error: File not found: ' + str(tune_path))
        sys.exit(1)

    title, type = get_metadata(tune, tune_path.suffix)
    return title, type


def get_metadata(tune, ext):
    title, type = None, None

    if ext == '.abc':
        title_re = re.compile('^T:(.*)$')
        type_re = re.compile('^R:(.*)$')
    elif ext == '.ly':
        title_re = re.compile('^\s*title\s*=\s*"(.*)"$')
        type_re = re.compile('^\s*meter\s*=\s*"(.*)"$')
    else:
        return None, None
        #TODO: issue an error (unsupported file type)

    for line in tune:
        if title and type:
            break

        if not title:
            m = title_re.match(line)
            if m:
                title = m.group(1).strip()
                continue

        if not type:
            m = type_re.match(line)
            if m:
                type = m.group(1).strip().lower()
                continue

    return title, type


def title_to_id(tune_title: str) -> str:
    """
    Generate a tune identifier from a tune title

    The identifier is obtained by converting the tune title to lower case
    and then substituting all characters that are neither lower case ascii
    characters nor digits to '_'

    Args:
        tune_title: The tune title, eg "Brid Harper's"

    Returns:
        The tune id, eg 'brid_harper_s'
    """
    id = ''
    for c in tune_title.lower():
        if not (c in string.ascii_lowercase or c in string.digits):
            if c is 'í':
                c = 'i'
            elif c is 'ú':
                c = 'u'
            elif c is 'ó':
                c = 'o'
            else:
                c = '_'
        id += c
    return id
    #TODO: move to abc.py and factorize with abcsplit.py


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
    header = "\\begin{figure}[H]\n"
    return header


def gen_tune_label(label):
    tex_label = ['\\label{', label, '}\n']
    return "".join(tex_label)


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

    return "".join(block)


def gen_tune(label, title, type):
    data = []
    data.append(gen_tune_header(title, type))
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

def gen_index_of_tunes(tunes):
    sorted_tunes = sort_tunes(tunes)
    latex_index = "\\section*{Index des airs}\n"
    for tune in tunes:
        latex_index += tune.format_index_entry() + "\n\n"
    return latex_index


def sort_tunes(tunes):
    sorted_tunes = tunes  # TODO: Useless: object is sorted in place
                          # (also: no need to return)
                          # Alternatively: make a copy of the list
    for tune in sorted_tunes:
        tune.title = demote_determinant(tune.title)
    sorted_tunes.sort()
    return sorted_tunes


def demote_determinant(title):
    words = title.split()
    if words == []:
        return title
    determinant = words[0]
    if determinant.lower() in ["the", "les", "le"]:
        index_title = " ".join(words[1:])
        index_title += ", " + determinant
        return index_title
    else:
        return title


# ------------------------------------------------------------------------
#     Generate the index of sets
# ------------------------------------------------------------------------

def gen_index_of_sets(tunes):
    data = []
    data.append('\n\n')
    #data.append('\\pagebreak\n')
    data.append('\\section*{Index des suites}\n')

    try:
        f = open(TUNE_SETS_FILENAME)
    except:
        sys.stderr.write("Warning: Cannot open " + TUNE_SETS_FILENAME + "\n")
        return []

    for lineno, line in enumerate(f):
        # Each line contains a comma separated list of labels.
        # A line can be empty
        # A line can be a comment starting with #
        line = line.strip()
        if line == '':
            continue
        if line[0] == '#':
            continue
        (set_title, set_tunes) = split_title_and_tunes(line)
        labels = set_tunes.split(',')
        entry = []
        tune_set = []
        for label in labels:
            label = label.strip()
            if label not in tunes.keys():
                sys.stderr.write(TUNE_SETS_FILENAME + ":" + str(lineno + 1) + " " +
                                 "Warning: No matching tune for index label " +
                                 label + "\n")
                continue
            tune_set.append(Tune(label, tunes[label]['title'], tunes[label]['type']))
        index_entry = format_set_index_entry(tune_set, set_title)
        data.append(index_entry + "\n\n")

    f.close()
    return data


def split_title_and_tunes(index_entry):
    if -1 == index_entry.find(":"):
        # No title
        return ("", index_entry.strip())

    l = index_entry.split(":")
    tunes = l[1].strip()
    title = l[0].strip()
    return (title, tunes)

def format_set_index_entry(tunes, title=""):
    entry = ""

    # Do all the tunes have the same type?
    same_type = True
    set_type = ""
    for tune in tunes:
        if tune.type == None:
            tune.type = ""
        if set_type == "":
            set_type = tune.type
        else:
            if set_type != tune.type:
                same_type = False
                break

    if title != "":
        entry = '\emph{' + title + '}'

    factorize_type = False
    if len(tunes) >= 2:
        if same_type and set_type != "":
            if title != "":
                entry += " (" + set_type.lower() + "s" + ")"
            else:
                entry += set_type.capitalize() + "s"
            factorize_type = True

    if title != "" or factorize_type:
        entry += ': '

    first_tune = True
    for tune in tunes:
        tune_ref = '\emph{' + tune.title + '}'
        tune_ref += '~('
        if tune.type != "" and tune.type != None and not factorize_type:
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
