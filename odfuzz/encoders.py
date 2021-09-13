from odfuzz.config import Config
from odfuzz.utils import encode_string, decode_string

Config.init()


class EncoderMixin:
    _encode = encode_string if Config.fuzzer.use_encoder else lambda x: x

    @classmethod
    def _encode_string(cls, value):
        return cls._encode(value)

    @classmethod
    def _reset(cls):
        cls._encode = encode_string if Config.fuzzer.use_encoder else lambda x: x


class DecoderMixin:
    _decode = decode_string if Config.fuzzer.use_encoder else lambda x: x

    @classmethod
    def _decode_string(cls, value):
        return cls._decode(value)
