#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: nu:ai:ts=4:sw=4

#
#  Copyright (C) 2025 Joseph Areeda <joseph.areeda@ligo.org>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

""""""
import socket
import time
from datetime import datetime
from astropy.time import Time
from gwpy.time import from_gps

start_time = time.time()

import argparse
import logging
from pathlib import Path
import re
import sys
import traceback

from gwdatafind import find_latest

try:
    from ._version import __version__
except ImportError:
    __version__ = '0.0.0'

__author__ = 'joseph areeda'
__email__ = 'joseph.areeda@ligo.org'
__process_name__ = Path(__file__).name

from .gap_utils import std_frames, v1_frames, TOO_MUCH, get_default_ifo

logger = None


# use: logger.log(TOO_MUCH, <message>)


def parser_add_args(parser):
    """
    Set up the command parser
    :param argparse.ArgumentParser parser:
    :return: None but the parser object is updated
    """
    parser.add_argument('-v', '--verbose', action='count', default=1,
                        help='increase verbose output')
    parser.add_argument('-V', '--version', action='version',
                        version=__version__)
    parser.add_argument('-q', '--quiet', default=False, action='store_true',
                        help='show only fatal errors')
    parser.add_argument('ifo', choices=['H1', 'L1', 'V1'], nargs='?', help='IFO to process')


def main():
    global logger

    log_file_format = "%(asctime)s - %(levelname)s - %(funcName)s %(lineno)d: %(message)s"
    log_file_date_format = '%m-%d %H:%M:%S'
    logging.basicConfig(format=log_file_format, datefmt=log_file_date_format)
    logger = logging.getLogger(__process_name__)
    logger.setLevel(logging.DEBUG)

    parser = argparse.ArgumentParser(description=__doc__, prog=__process_name__,
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser_add_args(parser)
    args = parser.parse_args()
    verbosity = 0 if args.quiet else args.verbose

    if verbosity < 1:
        logger.setLevel(logging.CRITICAL)
    elif verbosity < 2:
        logger.setLevel(logging.WARNING)
    elif verbosity < 3:
        logger.setLevel(logging.INFO)
    elif verbosity < 4:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(TOO_MUCH)

    # debugging?
    logger.debug(f'{__process_name__} version: {__version__} host: {socket.gethostname()} ')
    logger.debug(f'logger level set to {logger.getEffectiveLevel()}')

    for k, v in args.__dict__.items():
        logger.debug('    {} = {}'.format(k, v))

    fpat = '^(.+)-(\\d+)-(\\d+).(.+)$'
    fmatch = re.compile(fpat)

    ifo, host = get_default_ifo()
    if args.ifo:
        ifo = args.ifo
    nowdt: datetime.datetime = Time.now().datetime
    print(f'At {nowdt.strftime("%Y-%m-%d %H:%M:%S UTC")} for {ifo} running on {host}')

    frames = list(std_frames) + list(v1_frames)
    frames.sort()
    results = list()

    for f in frames:
        frame_type = f.replace('{ifo}-', "")
        frame_type = frame_type.replace('{ifo}', ifo)
        logger.debug(f'Finding latest frame for {ifo[0]}-{frame_type}')
        try:
            last_frame = find_latest(ifo[0], frame_type)
        except Exception as ex:
            logger.error(f'Error finding latest frame for {ifo[0]}-{frame_type}: {ex}')
            continue
        if last_frame is None or len(last_frame) == 0:
            continue
        last_frame = last_frame[0]
        logger.debug(f'Latest frame for {ifo[0]}-{frame_type}: {last_frame}')
        last_frame_match = fmatch.match(last_frame)
        if last_frame_match:
            gps_start = int(last_frame_match.group(2))
            fr_length = int(last_frame_match.group(3))
            gps_end = gps_start + fr_length
            date_start = from_gps(gps_start).strftime('%Y-%m-%d %H:%M:%S')
            date_end = from_gps(gps_end).strftime('%Y-%m-%d %H:%M:%S')
            age = nowdt - from_gps(gps_end)

            result = [f'{ifo[0]}-{frame_type}', f'{gps_start}', f'{fr_length}', f'{date_start}', f'{date_end}', f'{age}']
            results.append(result)
    if len(results) == 0:
        print('No frames found')
        return
    result = results[0]

    col_len = [len(r) for r in result]
    for result in results:
        for i in range(len(result)):
            col_len[i] = max(col_len[i], len(result[i]))

    print('\n\n')

    head_line = f'{"Frame Type":^{col_len[0]}} | {"GPS Start":^{col_len[1]}} | {"Len":^{col_len[2]}} | '\
                f'{"Start Date":^{col_len[3]}} | {"End Date":^{col_len[4]}} | {"Age":^{col_len[5]}} |'
    hl = len(head_line)
    print('-' * hl)
    print(head_line)

    print('-' * hl)

    for r in results:
        for i, col in enumerate(r):
            print(f'{col:>{col_len[i]}}', end=' | ')
        print()
    print('-' * hl)


if __name__ == "__main__":
    try:
        main()
    except (ValueError, TypeError, OSError, NameError, ArithmeticError, RuntimeError) as ex:
        print(ex, file=sys.stderr)
        traceback.print_exc(file=sys.stderr)

    if logger is None:
        logging.basicConfig()
        logger = logging.getLogger(__process_name__)
        logger.setLevel(logging.DEBUG)
    # report our run time
    logger.info(f'Elapsed time: {time.time() - start_time:.1f}s')
