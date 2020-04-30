import random

from collections import namedtuple

from odfuzz.generators import EdmDouble, EdmString, RandomGenerator
from odfuzz.encoders import encode_string

StringPropertyMock = namedtuple('StringPropertyMock', 'max_length')


def test_string_generator_with_encoder():
    RandomGenerator._encode = encode_string

    random.seed(14)
    generated_string = EdmString.generate(StringPropertyMock(10))

    assert generated_string == '\'%C3%B1\''


def test_string_generator_without_encoder():
    RandomGenerator._encode = lambda x: x

    random.seed(14)
    generated_string = EdmString.generate(StringPropertyMock(10))

    assert generated_string == '\'ñ\''


def test_double_generator_with_encoder():
    EdmDouble._encode = encode_string

    random.seed(14)
    generated_double = EdmDouble.generate()

    assert generated_double == '1.2712595986497026e%2B39d'


def test_double_generator_without_encoder():
    EdmDouble._encode = lambda x: x

    random.seed(14)
    generated_double = EdmDouble.generate()

    assert generated_double == '1.2712595986497026e+39d'
