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
    wofpy_config INDIR [--mode=<development,production>] [--overwrite=<soft,hard,none>]

    wofpy_config (-h | --help | -v | --version | -m | --mode | -o | --overwrite)

Examples:
    wofpy_config wofpyserver
    wofpy_config wofpyserver --mode=production --overwrite=soft

Arguments:
  directory               Configuration directory.

Options:
  -h --help               Show this screen.
  -v --version            Show version.
  -m --mode=development   Deploympent mode [default: development].
  -o --overwrite=none     Overwrite everything *hard*,
                          or only adds extra files to an exsting directory *soft*
                          [default: none].
"""

_ROOT = os.path.abspath(os.path.dirname(wof.__file__))
_CONFIG = os.path.join(_ROOT, 'examples', 'production_configs')
_ODM2_TIMESERIES = os.path.join(_ROOT, 'examples', 'flask', 'odm2', 'timeseries')


def makedirs(directory, overwrite=None):
    if not os.path.exists(directory):
        os.makedirs(directory)
    elif os.path.exists(directory) and overwrite in ['soft', 'hard']:
        if overwrite == 'hard':
            shutil.rmtree(directory)
            os.makedirs(directory)
    else:
        msg = 'Directory {} already exists.'.format
        raise ValueError(msg(directory))


def copytree(src, dst, symlinks=False, ignore=None, overwrite='none'):
    for item in os.listdir(src):
        if '.pyc' in item:
            continue
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.exists(d) and overwrite == 'soft':
            continue
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)


def main():
    args = docopt(__doc__, version='1.0.0')
    directory = args.get('INDIR')

    mode = args.get('--mode').lower()
    if mode not in ['development', 'production']:
        raise ValueError('Got mode: {!r}, expected development, or production.'.format(mode))

    overwrite = args.get('--overwrite').lower()
    if overwrite not in ['hard', 'soft', 'none']:
        msg = 'Got overwrite: {!r}, expected none, hard, or soft.'.format
        raise ValueError(msg(overwrite))
    elif overwrite == 'hard':
        print('Overwriting directory {}.'.format(directory))
    elif overwrite == 'soft':
        print('Adding files to directory {}.'.format(directory))

    makedirs(directory, overwrite)
    _TEST = os.path.join(directory, 'odm2', 'timeseries')
    makedirs(_TEST, overwrite)
    copytree(_ODM2_TIMESERIES, _TEST, overwrite=overwrite)
    if mode == 'production':
        _PRODUCTION = os.path.join(directory, 'production_configs')
        makedirs(_PRODUCTION, overwrite)
        copytree(_CONFIG, _PRODUCTION, overwrite=overwrite)


if __name__ == '__main__':
    main()
