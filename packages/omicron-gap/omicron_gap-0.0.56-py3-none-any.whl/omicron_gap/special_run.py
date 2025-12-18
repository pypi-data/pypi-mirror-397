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
import textwrap
import time

from gwpy.time import to_gps

start_time = time.time()

import argparse
import logging
from pathlib import Path
import sys
import traceback

try:
    from ._version import __version__
except ImportError:
    __version__ = '0.0.0'

__author__ = 'joseph areeda'
__email__ = 'joseph.areeda@ligo.org'
__process_name__ = Path(__file__).name

logger = None


def parser_add_args(parser):
    """
    Set up command parser
    :param argparse.ArgumentParser parser:
    :return: None but parser object is updated
    """
    parser.add_argument('-v', '--verbose', action='count', default=1,
                        help='increase verbose output')
    parser.add_argument('-V', '--version', action='version',
                        version=__version__)
    parser.add_argument('-q', '--quiet', default=False, action='store_true',
                        help='show only fatal errors')


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
        logger.setLevel(logging.INFO)
    else:
        logger.setLevel(logging.DEBUG)

    # debugging?
    logger.debug(f'{__process_name__} version: {__version__} called with arguments:')
    for k, v in args.__dict__.items():
        logger.debug('    {} = {}'.format(k, v))

    start = int(to_gps('9/11/2025 20:44:30'))
    end = int(to_gps('9/15/2025 20:48:25'))
    duration = 3600

    dag_job_template = textwrap.dedent('''\
        JOB %job_name% /home/joseph.areeda/omicron/4jane/condor/omicron.sub
        RETRY %job_name% 2
        VARS %job_name% macroargument0="%start%" macroargument1="%end%" macroargument2="/home/joseph.areeda/omicron/4jane/condor/parameters.txt"
        CATEGORY %job_name% omicron
        SCRIPT POST %job_name% /home/joseph.areeda/mambaforge/envs/ligo-omicron-3.10/bin/omicron-post-script -vvv --return $RETURN --retry $RETRY --max-retry $MAX_RETRIES --job $JOB --log /home/detchar/omicron/online/L-STD2/202509/20250915-213515/condor/post_script.log
        ## Job %job_name% requires input file /home/joseph.areeda/omicron/4jane/condor/parameters.txt
    ''')

    current = start
    job_num = 1
    dag_file = Path('/home/joseph.areeda/omicron/4jane/condor/imc_wfs.dag')
    dag_file.parent.mkdir(parents=True, exist_ok=True)

    with dag_file.open('w') as f:
        while current < end:
            current_end = min(current + duration, end)
            job_name = f'OMICRON_{job_num:02d}'
            dag_job = dag_job_template.replace('%job_name%', job_name)
            dag_job = dag_job.replace('%start%', str(current))
            dag_job = dag_job.replace('%end%', str(current_end))
            print(dag_job, file=f)

            current += duration
            job_num += 1

    logger.info(f'Wrote dag file {dag_file}')


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
