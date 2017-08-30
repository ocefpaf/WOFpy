import os
import shutil
import sys

import tempfile

import pytest

from wof.wofpy_config import makedirs


@pytest.fixture(scope='function')
def mkdtemp():
    _directory = tempfile.mkdtemp()
    _stat = os.stat(_directory)
    yield _directory, _stat
    shutil.rmtree(_directory)


def test_makedirs_do_not_overwrite():
    _directory, _ = mkdtemp().next()
    with pytest.raises(OSError):
        makedirs(_directory)


@pytest.mark.skipif(sys.platform == 'win32',
                    reason='st_ino does not work on Windows')
def test_makedirs_overwrite_soft():
    _directory, _stat = mkdtemp().next()
    makedirs(_directory, overwrite='soft')
    stat = os.stat(_directory)
    assert _stat.st_ino == stat.st_ino


@pytest.mark.skipif(sys.platform == 'win32',
                    reason='st_ino does not work on Windows')
def test_makedirs_overwrite_hard():
    _directory, _stat = mkdtemp().next()
    makedirs(_directory, overwrite='hard')
    stat = os.stat(_directory)
    assert _stat.st_ino != stat.st_ino
