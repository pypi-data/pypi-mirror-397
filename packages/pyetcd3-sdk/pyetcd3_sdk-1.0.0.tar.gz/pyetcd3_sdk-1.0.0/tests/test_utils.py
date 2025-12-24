class TestUtils(object):
    def test_prefix_range_end(self):
        assert pyetcd3.utils.prefix_range_end(b'foo') == b'fop'
        assert pyetcd3.utils.prefix_range_end(b'ab\xff') == b'ac\xff'
        assert (pyetcd3.utils.prefix_range_end(b'a\xff\xff\xff\xff\xff')
                == b'b\xff\xff\xff\xff\xff')

    def test_to_bytes(self):
        assert isinstance(pyetcd3.utils.to_bytes(b'doot'), bytes) is True
        assert isinstance(pyetcd3.utils.to_bytes('doot'), bytes) is True
        assert pyetcd3.utils.to_bytes(b'doot') == b'doot'
        assert pyetcd3.utils.to_bytes('doot') == b'doot'
