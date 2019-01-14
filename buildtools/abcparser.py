#!/usr/bin/python3
# -*- coding:utf-8 -*-


# Imports from the Python Standard Library:
import logging
from functools import total_ordering
from pathlib import Path
import string
import sys
from typing import List


# ------------------------------------------------------------------------
# Tune object
# ------------------------------------------------------------------------

@total_ordering
class Tune:
    """Store a tune's metadata and can be sorted based on title
    """
    def __init__(self, title=None, tune_type=None, index=None):
        self.index = index  # ABC tune index (X: header)
        self.title = title
        self.type = tune_type  # Reel, Jig, ...
        self.label = None  # Tune label is tune identifier
        self.title_for_index = None
        self.text = ''

        self.set_title(title)

    def set_title(self, title):
        self.title = title
        if self.title is not None:
            self.label = title_to_label(self.title)
            self.title_for_index = demote_determinant(self.title)

    def __eq__(self, other):
        return self.title_for_index.lower() == other.title_for_index.lower()

    def __lt__(self, other):
        return self.title_for_index.lower() < other.title_for_index.lower()

    def __cmp__(self, other):
        x = self.title_for_index.lower()
        y = other.title_for_index.lower()
        if x > y:
            return 1
        elif x == y:
            return 0
        else:  #x < y
            return -1

    def __str__(self):
        return self.title


def demote_determinant(title: str) -> str:
    """Given a tune title, return a title adapted for indexing, eg
       'The Miller's Maggot' => 'Miller's Maggot, The'

    Args:
        title: tune title

    Returns:
        tune title with demoted determinant
    """
    words = title.split()
    if len(words) == 0:
        return title
    determinant = words[0]
    if determinant.lower() in ['the', 'les', 'le']:
        title_for_index = ' '.join(words[1:])
        title_for_index += ', ' + determinant
        return title_for_index
    else:
        return title


def title_to_label(tune_title: str) -> str:
    """
    Generate a tune label from a tune title

    The label is obtained by converting the tune title to lower case
    and then substituting all characters that are neither lower case ascii
    characters nor digits to '_'

    Args:
        tune_title: The tune title, eg "Brid Harper's"

    Returns:
        The tune label, eg 'brid_harper_s'
    """
    label = ''
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
        label += c
    return label


# ----------------------------------------------------------------------------
#     The ABC parser
# ----------------------------------------------------------------------------

class AbcError(Exception):
    def __init__(self, free_text=''):
        self._free_text = free_text

    def __str__(self):
        return self._free_text


class AbcParserError(AbcError):
    pass


class AbcParserStateMachineError(AbcError):
    pass


class AbcParserStateMachine:
    def __init__(self):
        self.S_WAIT_TUNE = 'WAIT_TUNE'
        self.S_WAIT_TITLE = 'WAIT_TITLE'
        self.S_READ_TUNE = 'READ_TUNE'
        self.S_END = 'END'

        self._state = self.S_WAIT_TUNE
        self._lineno = 0

        self._tune = Tune()  # Tentative ABC tune being parsed
        self._tunes = []  # list of parsed Tune's

    def _parse_index(self, index_str: str) -> int:
        """
        Parse the index header string of an ABC tune

        Args:
            index_str: tune index as string, without the 'X:' header name

        Returns:
            Tune index as int

        Throws:
            AbcParserError if the index string is invalid
        """
        try:
            index = int(index_str)
            return index
        except ValueError:
            raise AbcParserError('line {0}: invalid tune index string: \'{1}\''
                                 .format(self._lineno, index_str))

    def _run_with_index(self, stripped_line, line):
        self._tune.index = self._parse_index(stripped_line[2:])
        self._tune.text += line
        logging.debug('AbcParserStateMachine: new index: %d', self._tune.index)
        self._state = self.S_WAIT_TITLE

    def run(self, line):
        self._lineno += 1

        stripped_line = line.strip()
        if stripped_line == '':
            return

        if self._state is self.S_WAIT_TUNE:
            if stripped_line.startswith('X:'):
                self._run_with_index(stripped_line, line)
            else:
                logging.debug('AbcParserStateMachine: skip heading line: %s',
                              stripped_line)

        elif self._state is self.S_WAIT_TITLE:
            if stripped_line.startswith('T:'):
                title = stripped_line[2:].strip()
                if title is '':
                    raise AbcParserError(
                        'line {0}: empty title header field'
                        .format(self._lineno))
                self._tune.set_title(title)
                self._tune.text += line
                logging.debug('AbcParserStateMachine: title: %s',
                              self._tune.title)
                self._state = self.S_READ_TUNE
            else:
                raise AbcParserStateMachineError(
                    'line {0}: tune index not followed by title: \'{1}\''
                    .format(self._lineno, stripped_line))

        elif self._state is self.S_READ_TUNE:
            if stripped_line.startswith('X:'):  # New tune
                self._tunes.append(self._tune)
                self._tune = Tune()
                self._run_with_index(stripped_line, line)
            elif stripped_line.startswith('R:'):  # Header: tune type
                self._tune.type = stripped_line[2:].strip()
                self._tune.text += line
                logging.debug('AbcParserStateMachine: type: %s',
                              self._tune.type)
            else:
                self._tune.text += line
                logging.debug('AbcParserStateMachine: new line: %s',
                              line.strip('\n'))

    def get_tunes(self) -> List[Tune]:
        """Get the list of parsed tunes and stop the state machine

        Returns:
            A list of Tune objects
        """
        if self._tune.title is not None:
            self._tunes.append(self._tune)
            self._tune = Tune()
        self._state = self.S_END
        return self._tunes


# ------------------------------------------------------------------------
# Easy-to-use parse function
# ------------------------------------------------------------------------

def parse_abc_file(abc_filepath: Path) -> List[Tune]:
    """Parse an ABC file and return a list of tunes

    Args:
        abc_filepath: path to a text file containing one or several tunes
            in ABC notation format.

    Returns:
        A list of Tune objects

    """
    parser = AbcParserStateMachine()
    with open(abc_filepath, 'r') as f:
        logging.debug('Parsing ABC file: %s', abc_filepath)
        for line in f:
            try:
                parser.run(line)
            except AbcError:
                logging.error('Failed to parse ABC file: %s',
                              str(abc_filepath), exc_info=True)
                sys.exit(1)
    tunes = parser.get_tunes()

    return tunes
