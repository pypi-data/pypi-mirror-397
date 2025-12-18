from multiprocessing import Process
import signal
import sys
from time import sleep

import psutil

from artefacts.cli import child_process_cleanup


#
# Sub-process with controlled behaviours
#
#   Using multiprocessing, we need module-global functions
#   or multiprocessing cannot pickle.
#
def _plain():
    sleep(0.1)


def _ignores_sigterm():
    signal.signal(signal.SIGTERM, lambda sig, frame: ())
    sleep(10)


#
# Test suite
#
def test_child_process_cleanup_no_child(mocker):
    mocker.patch.object(psutil.Process, "children", return_value=[])
    assert child_process_cleanup() == {
        "found": 0,
        "terminated": 0,
        "killed": 0,
    }


def test_child_process_cleanup_single_child_plain(mocker):
    child = Process(target=_plain)
    child.start()
    report = child_process_cleanup(wait_time_s=0.2)
    expected = {
        "found": 1,
        "terminated": 1,
        "killed": 0,
    }
    if sys.platform == "darwin":
        # Still unclear why an extra process appears on Darwin only
        expected["found"] += 1
        expected["killed"] += 1
    assert report == expected
    child.join()


def test_child_process_cleanup_single_child_ignores_sigterm():
    child = Process(target=_ignores_sigterm)
    child.start()
    report = child_process_cleanup(wait_time_s=0.2)
    expected = {
        "found": 1,
        "terminated": 0,
        "killed": 1,
    }
    if sys.platform == "darwin":
        # Still unclear why an extra process appears on Darwin only
        expected["found"] += 1
        expected["terminated"] += 1
    assert report == expected
    child.join()


def test_child_process_cleanup_multi_child_mixed():
    c1 = Process(target=_plain)
    c2 = Process(target=_ignores_sigterm)
    c1.start()
    c2.start()
    report = child_process_cleanup(wait_time_s=0.2)
    expected = {
        "found": 2,
        "terminated": 1,
        "killed": 1,
    }
    if sys.platform == "darwin":
        # Still unclear why an extra process appears on Darwin only
        expected["found"] += 1
        expected["terminated"] += 1
    assert report == expected
    c1.join()
    c2.join()
