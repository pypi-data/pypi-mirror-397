import base64
from contextlib import contextmanager
import json
import os
import signal
import string
import subprocess
import tempfile
import threading
import time

import grpc

from hypothesis import given, settings
from hypothesis.strategies import characters

import mock

import pytest

from urllib.parse import urlparse

from tenacity import retry, stop_after_attempt, wait_fixed

import pyetcd3
import pyetcd3.etcdrpc as etcdrpc
import pyetcd3.exceptions
import pyetcd3.utils as utils
from pyetcd3.client import EtcdTokenCallCredentials


os.environ['ETCDCTL_API'] = '3'
#  os.environ['PYTHON_ETCD_HTTP_URL'] = "localhost:2379"

# Don't set any deadline in Hypothesis
settings.register_profile("default", deadline=None)
settings.load_profile("default")
