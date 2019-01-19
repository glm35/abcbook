#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# Standard Python modules:
import argparse
import logging
import os
from pathlib import Path

# Imports from the project library:
from abcparser import Tune, parse_abc_file


ARGS = None  # Command line arguments after parsing


# ----------------------------------------------------------------------------
#     Entry point & CLI arguments parsing
# ----------------------------------------------------------------------------

def main():
    global ARGS

    ARGS = parse_args()
    setup_logging()
    dump_args(ARGS)

    abc_file = Path(ARGS.abc_file[0])
    output_dir = Path(ARGS.output_dir)
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
    return args


def dump_args(args):
    if args.debug:
        logging.debug('debug on')
    if args.verbose:
        logging.debug('verbose on')
    if args.output_dir:
        logging.debug('output dir: %s', args.output_dir)


def setup_logging():
    if ARGS.debug:
        logging_level = logging.DEBUG
    elif ARGS.verbose:
        logging_level = logging.INFO
    else:
        logging_level = logging.WARNING
    logging.basicConfig(level=logging_level, format='<%(levelname)s> %(message)s')


# ----------------------------------------------------------------------------
#     ABC split logic
# ----------------------------------------------------------------------------

def split_abc_file(abc_filepath: Path, output_dir: Path):
    """
    Open a .abc file and create one ABC file per tune and one index

    Args
        filename: Name of the .abc file to split with absolute
            or relative path.
        output_dir: Name of the directory to write the split
            files.

    Return
        None

    """
    logging.info('Splitting: %s', abc_filepath)

    tunes = parse_abc_file(abc_filepath)

    if ARGS.verbose:
        logging.info('Parsed %s tunes:', len(tunes))
        for tune in tunes:
            logging.info('- %s', tune.title)

    if len(tunes) > 0:
        os.makedirs(str(output_dir), exist_ok=True)

    for tune in tunes:
        output_file = output_dir.joinpath(tune.label + '.abc')
        logging.info('Writing file: %s', output_file)
        with open(output_file, 'w') as f:
            f.write(tune.text)
        # Note: if 'tune' has the same label (~ title) as an already processed
        # tune, it will overwrite a previously created output_file.  This is
        # certainly not desirable, but this is checked in gen_tex_tunebook.py,
        # so it is not checked here.


# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------

if __name__ == '__main__':
    main()
