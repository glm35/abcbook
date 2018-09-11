#!/usr/bin/python

import sys
import re
from optparse import OptionParser


# ------------------------------------------------------------------------
# Global variables
# ------------------------------------------------------------------------

tune_dir = "tunes"
out = "_build/out.stage1"


# ------------------------------------------------------------------------
# Data structures
# ------------------------------------------------------------------------

# The list of the tune labels
#
# Necessary to keep an ordored record of the tunes.

labels = []

# The dictionnary of tunes
#
# For each tune identified by its label, it contains the title and the
# type of the tune.
#
# key: label
# value: dictionnary that contains the data for the tune labelled by the
# key:
#    keys: "title", "type"

tunes = {}


# ------------------------------------------------------------------------
# Parse the command line arguments
# ------------------------------------------------------------------------

def parse_command_line():
    parser = OptionParser()
    parser.add_option("-n", "--name", dest="name", default="tunebook",
                      help="set the tunebook name")
    (options, args) = parser.parse_args()
    return (options, args)


# ------------------------------------------------------------------------
# Get the list of tunes
# ------------------------------------------------------------------------

def get_tune_labels(label_file, labels):
    f = open(label_file)
    while True:
        label = f.readline()
        if label == '':
            # reached end of file
            break
        if label[0] == '#':
            continue
        label = label.strip()
        if label:
            labels.append(label)
        # else: emtpy line
    f.close()


# ------------------------------------------------------------------------
# Get the metadata in a tune
# ------------------------------------------------------------------------

def get_tune_metadata(label):
    title, type = None, None

    for ext in (".ly", ".abc"):
        try:
            f = open(tune_dir + "/" + label + ext)
            tune = f.readlines()
            f.close()
            title, type = get_metadata(tune, ext)
            if not title:
                title = "Unnamed"
            break
        except IOError:
            pass
    else:
        sys.stderr.write("Warning: no tune file for label " + label + "\n")
    return title, type


def get_metadata(tune, ext):
    title, type = None, None

    if ext == ".abc":
        title_re = re.compile('^T:(.*)$')
        type_re = re.compile('^R:(.*)$')
    else:
        title_re = re.compile('^\s*title\s*=\s*"(.*)"$')
        type_re = re.compile('^\s*meter\s*=\s*"(.*)"$')

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


# ------------------------------------------------------------------------
# Manipulate the metadata of a tune
# ------------------------------------------------------------------------

class Tune():

    def __init__(self, label="", title="", type=""):
        self.label = label
        self.title = title
        self.type = type

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

def sort_tunes(tunes):
    sorted_tunes = tunes
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
# Generate a tune
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
    block.append('\\include "' + '../../' + out + '/' + label + '.ly' + '"' + "\n")
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
# Make the index of sets
# ------------------------------------------------------------------------

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
# Generate the book
# ------------------------------------------------------------------------

def eat_up_template(template, tag=None):
    data = []
    while template:
        line = template.pop(0)
        if (line == tag):
            break
        data.append(line)
    return data


def gen_index_of_tunes(tunes):
    sorted_tunes = sort_tunes(tunes)
    latex_index = "\\section*{Index des airs}\n"
    for tune in tunes:
        latex_index += tune.format_index_entry() + "\n\n"
    return latex_index


def gen_index_of_sets(tunes):
    data = []
    data.append('\n\n')
    #data.append('\\pagebreak\n')
    data.append('\\section*{Index des suites}\n')

    try:
        f = open(set_file)
    except:
        sys.stderr.write("Warning: Cannot open " + set_file + "\n")
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
            if not tunes.has_key(label):
                sys.stderr.write(set_file + ":" + str(lineno+1) + " " +
                                 "Warning: No matching tune for index label " +
                                 label + "\n")
                continue
            tune_set.append(Tune(label, tunes[label]['title'], tunes[label]['type']))
        index_entry = format_set_index_entry(tune_set, set_title)
        data.append(index_entry + "\n\n")

    f.close()
    return data


def gen_book():
    get_tune_labels(label_file, labels)

    f_template = open(template_file)
    template = f_template.readlines()
    f_template.close()

    f_tunebook = open(tunebook_file, "w")
    f_tunebook.writelines(eat_up_template(template, "%%INSERT_TUNES\n"))
    obj_tunes = []
    for label in labels:
        title, type = get_tune_metadata(label)
        if not title:
            continue
        tunes[label] = {'title' : title, 'type' : type}
        obj_tunes.append(Tune(label, title, type))
        f_tunebook.writelines(gen_tune(label, title, type))
    f_tunebook.writelines(eat_up_template(template, "%%INSERT_INDEX\n"))
    f_tunebook.write("\\twocolumn\n")
    f_tunebook.write(gen_index_of_tunes(obj_tunes))
    f_tunebook.write("\\onecolumn\n")
    f_tunebook.writelines(gen_index_of_sets(tunes))
    f_tunebook.writelines(eat_up_template(template))
    f_tunebook.close()


# ------------------------------------------------------------------------
# Program entry point
# ------------------------------------------------------------------------
#     (not executed when gen_tex_tunebook.py is imported: needed for
#     unitary tests)
# ------------------------------------------------------------------------

if __name__ == '__main__':
    (options, args) = parse_command_line()

    label_file = "bookspecs/tune_files.txt"
    set_file = "bookspecs/tune_sets.txt"
    template_file = "bookspecs/book_template.tex"
    tunebook_file = out + "/" + options.name + ".lytex"

    gen_book()
