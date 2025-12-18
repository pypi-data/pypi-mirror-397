# test authorization
# noqa: F401

import configparser
import re
import shutil
import subprocess
import traceback
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path

from ja_webutils.PageItem import PageItemImage, PageItemLink
from matplotlib import use
import time

from requests import exceptions

start_time = time.time()

import os
import sys

# if launched from a terminal with no display
# Must be done before modules like pyplot are imported
if len(os.getenv('DISPLAY', '')) == 0:
    use('Agg')  # nopep8

import argparse
import logging
from gwpy.time import to_gps, tconvert, from_gps  # noqa: E402
try:
    from omicron_gap._version import __version__
except ImportError:
    __version__ = '0.0.0'

from gwpy.segments import DataQualityFlag, Segment, SegmentList  # noqa: E402
from gwpy.plot.segments import SegmentAxes
from omicron_gap.gap_utils import gps2utc, find_frame_availability, find_trig_seg, \
    get_default_ifo, get_gps_day, gps2dirname  # noqa: E402
import matplotlib   # noqa: E402
from gwpy.plot import Plot
from ja_webutils.Page import Page
from igwn_auth_utils.scitokens import default_bearer_token_file

start = 1401464000
end = 1401464100
seg_name = 'L1:DMT-ANALYSIS_READY:1'
seg_server = 'https://segments.ligo.org'

try:
    seg_data = DataQualityFlag.query_dqsegdb(seg_name, start, end, url=seg_server)
    print('Successful dqsegdb query')
    print('Successful dqsegdb query', file=sys.stderr)
except Exception as e:
    print(f'Failed dqsegdb query: {e}', file=sys.stderr)

# try a datafind request
ifo = 'H1'
frame_type = 'H1_HOFT_C00'
datafind_server = 'https://datafind.igwn.org'

cmd = ['gw_data_find', '-o', ifo[0], '-t', frame_type, '-s', str(int(start)), '-e', str(int(end)),
       '--gaps', '-r', datafind_server]
print(cmd)
ret = subprocess.run(cmd, check=False, capture_output=True)
if ret.returncode == 0:
    print('Successful datafind query')
    print('Successful datafind query', file=sys.stderr)
else:
    print(f'Failed dqsegdb query: {ret.stderr.decode("utf-8")}', file=sys.stderr)
