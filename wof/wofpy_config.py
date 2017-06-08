from __future__ import (absolute_import, division, print_function)

import os
import shutil

import wof

from docopt import docopt

__all__ = [
    'main',
    ]

__doc__ = """
Generate configuration directory structure for running WOFpy.

Usage:
    wofpy_config INDIR
    wofpy_config INDIR [--mode=<development,production>]

    wofpy_config (-h | --help | -v | --version)

Examples:
    wofpy_config wofpyserver

Arguments:
  directory     Configuration directory.

Options:
  -h --help     Show this screen.
  -v --version  Show version.
  --mode=development   deploy mode [default: development]
"""

_ROOT = os.path.abspath(os.path.dirname(wof.__file__))
_CONFIG = os.path.join(_ROOT, 'examples', 'production_configs')
_ODM2_TIMESERIES = os.path.join(_ROOT, 'examples', 'flask', 'odm2', 'timeseries')


def makedirs(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
    else:
        msg = 'Directory {} already exists.'.format
        raise ValueError(msg(directory))


def copytree(src, dst, symlinks=False, ignore=None):
    for item in os.listdir(src):
        if '.pyc' in item:
            continue
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)


def main():
    args = docopt(__doc__, version='0.1.0')
    directory = args.get('INDIR')
    mode = args.get('--mode')
    if mode not in ['development', 'production']:
        raise ValueError('Got mode: {!r}, expected development, or production.'.format(mode))

    makedirs(directory)
    _TEST = os.path.join(directory, 'odm2', 'timeseries')
    makedirs(_TEST)
    copytree(_ODM2_TIMESERIES, _TEST)
    if mode == 'production':
        _PRODUCTION = os.path.join(directory, 'production_configs')
        makedirs(_PRODUCTION)
        copytree(_CONFIG, _PRODUCTION)


if __name__ == '__main__':
    main()
