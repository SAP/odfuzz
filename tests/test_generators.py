import random
import pytest

from collections import namedtuple

from odfuzz.generators import EdmDecimal, EdmDouble, EdmString, EdmTime, RandomGenerator
from odfuzz.encoders import encode_string
from odfuzz.config import Config

StringPropertyMock = namedtuple('StringPropertyMock', 'max_length')
StringNonNegativeMock = namedtuple('StringNonNegativeMock',['max_length','non_negative'])
DecimalMock = namedtuple('DecimalMock', ['precision','scale'])

@pytest.fixture(autouse=True, scope="module")
def teardown_module():
    #setup part of the fixture
    yield None #control back to the test instance
    RandomGenerator._reset() #teardown part of the fixture


def test_string_generator_with_encoder():
    RandomGenerator._encode = encode_string

    random.seed(14)
    generated_string = EdmString.generate(StringPropertyMock(10))

    assert generated_string == '\'%C3%B2\''


def test_string_generator_without_encoder():
    RandomGenerator._encode = lambda x: x

    random.seed(14)
    generated_string = EdmString.generate(StringPropertyMock(10))

    assert generated_string == '\'ò\''


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

def test_string_generator_with_nonnegative():
    random.seed(10)

    mckString = StringNonNegativeMock(5,True)
    generated_string = EdmString.generate(mckString)
    
    assert generated_string == "\'74894\'"

def test_string_generator_without_nonnegative():
    random.seed(10)
    
    mckString = StringNonNegativeMock(5,False)
    generated_string = EdmString.generate(mckString)
    
    assert generated_string == "\'ªºÒ\'"

def test_decimal_precision_equals_scale():
    random.seed(10)

    mckdecimal = DecimalMock(3,3)
    generated_decimal = EdmDecimal.generate(mckdecimal)
    
    assert generated_decimal == '0.586m'

def test_decimal_precision_scale_zero():
    random.seed(10)

    mckdecimal = DecimalMock(3,0)
    generated_decimal = EdmDecimal.generate(mckdecimal)
    
    assert generated_decimal == '8.00m'


def test_decimal_for_sap_vendor_enabled():
    random.seed(10)
    Config.fuzzer.sap_vendor_enabled = True
    
    mckdecimal = DecimalMock(15,14)
    generated_decimal = EdmDecimal.generate(mckdecimal,generator_format='body')
    Config.fuzzer.sap_vendor_enabled = False

    assert generated_decimal == '0.00000177'


def test_time_for_sap_vendor_enabled():
    random.seed(10)
    Config.fuzzer.sap_vendor_enabled = True

    generated_time = EdmTime.generate(generator_format='body')
    Config.fuzzer.sap_vendor_enabled = False

    assert generated_time == 'PT06H02M27S'
