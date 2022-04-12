"""Helper functions to analyse code behaviour."""

import logging
import os
import sys
import time

import psutil

logger = logging.getLogger("analyse")
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler(sys.stdout)

formatter = logging.Formatter("%(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)


def print_memory(topic):
    """
    Print pid, timestamp, memory in bytes & topic (comma seperated).

    Can be used in a multiprocess / multithreading scenario.
    """
    pid = os.getpid()
    process = psutil.Process(pid)
    memory_info = process.memory_info()
    size_in_bytes = memory_info.rss
    timestamp = time.time()
    result = ",".join([str(pid), str(timestamp), str(size_in_bytes), topic])
    logger.debug(result)
