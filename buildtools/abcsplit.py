#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# Standard Python modules:
import argparse
import os
import pathlib
import string
import sys

ARGS = None  # Command line arguments after parsing


# ----------------------------------------------------------------------------
#     Entry point & CLI arguments parsing
# ----------------------------------------------------------------------------

def main():
    global ARGS
    global PARAMS
    global SERVER

    ARGS = parse_args()
    abc_file = pathlib.Path(ARGS.abc_file[0])
    output_dir = pathlib.Path(ARGS.output_dir)
    split_abc_file(abc_file, output_dir)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug',
                        help='show debug messages',
                        action='store_true')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='verbosity level')
    parser.add_argument('-o', '--output-dir', type=str, default='.',
                        help='directory to write the split ABC files')
    parser.add_argument('abc_file', help='path to the .abc file to split', nargs=1)

    args = parser.parse_args()
    if args.debug:
        dump_args(args)
    return args


def dump_args(args):
    if args.debug:
        print('<debug> debug on')
    if args.verbose:
        print('<debug> verbose on')
    if args.output_dir:
        print('<debug> output dir:', args.output_dir)


# ----------------------------------------------------------------------------
#     ABC split logic
# ----------------------------------------------------------------------------

def split_abc_file(filename, output_dir):
    """
    Open a .abc file and create one ABC file per tune and one index

    Args
        filename: pathlib.Path: Name of the .abc file to split with absolute
            or relative path.
        output_dir: pathlib.Path: Name of the directory to write the split
            files.

    Return
        None

    """
    if ARGS.verbose:
        print('Splitting ' + str(filename) + '...')

    parser = AbcParserStateMachine()
    with open(str(filename), 'r') as f:
        for line in f:
            try:
                parser.run(line)
            except AbcError as e:
                print('Fatal error while parsing ' + filename + ': ' + str(e))
                sys.exit(1)

    tunes = parser.get_tunes()

    if ARGS.verbose:
        print('Parsed {0} tunes:'.format(len(tunes)))
        for tune in tunes:
            print('- {0}'.format(tune.title))

    if len(tunes) > 0:
        os.makedirs(str(output_dir), exist_ok=True)

    for tune in tunes:
        id = title_to_id(tune.title)
        output_file = output_dir.joinpath(id + '.abc')
        if ARGS.verbose:
            print('Writing file: ' + str(output_file))
        with open(str(output_file), 'w') as f:
            f.write(tune.text)


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
            c = '_'
        id += c
    return id


# ----------------------------------------------------------------------------
#     The ABC parser
# ----------------------------------------------------------------------------

class AbcTune:
    def __init__(self):
        self.index = None
        self.title = None
        self.text = ''


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

        self._tune = AbcTune()  # Tentative ABC tune being parsed
        self._tunes = []  # list of parsed AbcTune's

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
        if ARGS.debug:
            print(
                '<debug> [state-machine] new index: '
                + str(self._tune.index))
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
                if ARGS.debug:
                    print(
                        '<debug> [state-machine] skipping heading line: '
                        + stripped_line)

        elif self._state is self.S_WAIT_TITLE:
            if stripped_line.startswith('T:'):
                title = stripped_line[2:].strip()
                if title is '':
                    raise AbcParserError(
                        'line {0}: empty title header field'
                        .format(self._lineno))
                self._tune.title = title
                self._tune.text += line
                if ARGS.debug:
                    print('<debug> [state-machine] title: ' + self._tune.title)
                self._state = self.S_READ_TUNE
            else:
                raise AbcParserStateMachineError(
                    'line {0}: tune index not followed by title: \'{1}\''
                    .format(self._lineno, stripped_line))

        elif self._state is self.S_READ_TUNE:
            if stripped_line.startswith('X:'):  # New tune
                self._tunes.append(self._tune)
                self._tune = AbcTune()
                self._run_with_index(stripped_line, line)
            else:
                self._tune.text += line
                if ARGS.debug:
                    print('<debug> [state-machine] new line: '
                          + line.strip('\n'))

    def get_tunes(self):
        """Get the list of parsed tunes and stop the state machine

        Returns:
            A list of AbcTune's
        """
        if self._tune.title is not None:
            self._tunes.append(self._tune)
            self._tune = AbcTune()
        self._state = self.S_END
        return self._tunes


# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------

if __name__ == '__main__':
    main()
