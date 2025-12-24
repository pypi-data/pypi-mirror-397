# pyetcd3

[![version](https://img.shields.io/pypi/v/pyetcd3-sdk.svg?color=blue)](https://pypi.org/project/pyetcd3-sdk/)
[![Supported Python Versions](https://img.shields.io/pypi/pyversions/pyetcd3-sdk?logo=python&logoColor=blue)](https://pypi.org/project/pyetcd3-sdk/)
[![Downloads](https://pepy.tech/badge/pyetcd3-sdk)](https://pepy.tech/project/pyetcd3-sdk)
[![Downloads](https://pepy.tech/badge/pyetcd3-sdk/month)](https://pepy.tech/project/pyetcd3-sdk/month)
[![license](https://img.shields.io/hexpm/l/plug.svg?color=green)](https://github.com/wwyoyo03/pyetcd3/blob/main/LICENSE)

Python client for the etcd API v3, supported python >= 3.7, under active maintenance

## Install
```shell
pip install pyetcd3-sdk
```
## Differences from python-etcd3 and pyetcd
This package is a maintained fork of pyetcd with the following key improvements:

- Updated grpcio version and support for etcd authentication (username/password).
- Automatic token refresh to maintain authenticated sessions without manual reconnection.

These enhancements make pyetcd3-sdk more suitable for production environments that require secure, long-running connections to etcd clusters.


## Basic usage:

```python
import pyetcd3

etcd = pyetcd3.client()

etcd.get('foo')
etcd.put('bar', 'doot')
etcd.delete('bar')

# locks
lock = etcd.lock('thing')
lock.acquire()
# do something
lock.release()

with etcd.lock('doot-machine') as lock:
    # do something

# transactions
etcd.transaction(
    compare=[
        etcd.transactions.value('/doot/testing') == 'doot',
        etcd.transactions.version('/doot/testing') > 0,
    ],
    success=[
        etcd.transactions.put('/doot/testing', 'success'),
    ],
    failure=[
        etcd.transactions.put('/doot/testing', 'failure'),
    ]
)

# watch key
watch_count = 0
events_iterator, cancel = etcd.watch("/doot/watch")
for event in events_iterator:
    print(event)
    watch_count += 1
    if watch_count > 10:
        cancel()

# watch prefix
watch_count = 0
events_iterator, cancel = etcd.watch_prefix("/doot/watch/prefix/")
for event in events_iterator:
    print(event)
    watch_count += 1
    if watch_count > 10:
        cancel()

# recieve watch events via callback function
def watch_callback(event):
    print(event)

watch_id = etcd.add_watch_callback("/anotherkey", watch_callback)

# cancel watch
etcd.cancel_watch(watch_id)

# recieve watch events for a prefix via callback function
def watch_callback(event):
    print(event)

watch_id = etcd.add_watch_prefix_callback("/doot/watch/prefix/", watch_callback)

# cancel watch
etcd.cancel_watch(watch_id)
```

## Credits

Many thx to  [python-etcd3](https://github.com/kragniz/python-etcd3) and [pyetcd](https://github.com/XuanYang-cn/pyetcd)
