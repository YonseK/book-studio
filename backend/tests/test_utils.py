from bookstudio.utils import uuid_key, short_key


class TestUuidKey:
    def test_returns_32_char_hex(self):
        key = uuid_key()
        assert len(key) == 32
        assert key.isalnum()

    def test_unique(self):
        keys = {uuid_key() for _ in range(100)}
        assert len(keys) == 100


class TestShortKey:
    def test_returns_8_char_hex(self):
        key = short_key()
        assert len(key) == 8
        assert key.isalnum()

    def test_unique(self):
        keys = {short_key() for _ in range(100)}
        assert len(keys) == 100
