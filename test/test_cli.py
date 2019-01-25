import os
import shutil
import sys

import tempfile

import pytest

from wof.wofpy_config import cli, makedirs


@pytest.fixture(scope='function')
def mkdtemp():
    _directory = tempfile.mkdtemp()
    _stat = os.stat(_directory)
    yield _directory, _stat
    shutil.rmtree(_directory)


def test_makedirs_do_not_overwrite(mkdtemp):
    _directory, _stat = mkdtemp
    with pytest.raises(OSError):
        makedirs(_directory)


@pytest.mark.skipif(sys.platform == 'win32',
                    reason='st_ino does not work on Windows')
def test_makedirs_overwrite_soft(mkdtemp):
    _directory, _stat = mkdtemp
    makedirs(_directory, overwrite='soft')
    stat = os.stat(_directory)
    assert _stat.st_ino == stat.st_ino



def test_cli_overwrite_hard(mkdtemp):
    _directory, _stat = mkdtemp
    args = {
        'INDIR': _directory,
        '--mode': 'production',
        '--overwrite': 'hard'
    }
    cli(args)
    assert os.path.isdir(os.path.join(_directory, 'production_configs'))
    args.update({'--mode': 'development'})
    cli(args)
    assert not os.path.isdir(os.path.join(_directory, 'production_configs'))
