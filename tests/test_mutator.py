import random
import re

from collections import namedtuple

from odfuzz.mutators import DateTimeMutator, DecimalMutator, GuidMutator, StringMutator
from odfuzz.encoders import encode_string

DateTimeProperty = namedtuple('DateTimeProperty', 'precision')
DateTimePropertyMock = namedtuple('DateTimePropertyMock', 'precision scale')

StringPropertyMock = namedtuple('StringPropertyMock', 'max_length')


def test_date_time_mutator():
    date_time = 'datetime\'2019-01-01T10:10:10\''

    incremented_day = DateTimeMutator.increment_day(DateTimeProperty(0), date_time)
    assert incremented_day == 'datetime\'2019-01-02T10:10:10\''

    decremented_day = DateTimeMutator.decrement_day(DateTimeProperty(0), date_time)
    assert decremented_day == 'datetime\'2018-12-31T10:10:10\''

    incremented_month = DateTimeMutator.increment_month(DateTimeProperty(0), date_time)
    assert incremented_month == 'datetime\'2019-02-01T10:10:10\''

    decremented_month = DateTimeMutator.decrement_month(DateTimeProperty(0), date_time)
    assert decremented_month == 'datetime\'2018-12-01T10:10:10\''

    incremented_year = DateTimeMutator.increment_year(DateTimeProperty(0), date_time)
    assert incremented_year == 'datetime\'2020-01-01T10:10:10\''

    decremented_year = DateTimeMutator.decrement_year(DateTimeProperty(0), date_time)
    assert decremented_year == 'datetime\'2018-01-01T10:10:10\''


def test_shift_value_decimal_mutator():
    DecimalMutator._generator = GeneratorMock(randint=[-1])
    assert DecimalMutator.shift_value(DateTimePropertyMock(5, 2), '12.12m') == '1.21m'
    DecimalMutator._generator = GeneratorMock(randint=[-2])
    assert DecimalMutator.shift_value(DateTimePropertyMock(5, 2), '12.12m') == '0.12m'
    DecimalMutator._generator = GeneratorMock(randint=[-3])
    assert DecimalMutator.shift_value(DateTimePropertyMock(5, 2), '12.12m') == '0.01m'
    DecimalMutator._generator = GeneratorMock(randint=[-4])
    assert DecimalMutator.shift_value(DateTimePropertyMock(5, 2), '12.12m') == '0m'
    DecimalMutator._generator = GeneratorMock(randint=[-5])
    assert DecimalMutator.shift_value(DateTimePropertyMock(5, 2), '12.12m') == '0m'

    DecimalMutator._generator = GeneratorMock(randint=[1])
    assert DecimalMutator.shift_value(DateTimePropertyMock(5, 2), '12.12m') == '121.2m'
    DecimalMutator._generator = GeneratorMock(randint=[2])
    assert DecimalMutator.shift_value(DateTimePropertyMock(5, 2), '12.12m') == '1212m'
    DecimalMutator._generator = GeneratorMock(randint=[3])
    assert DecimalMutator.shift_value(DateTimePropertyMock(5, 2), '12.12m') == '12120m'
    DecimalMutator._generator = GeneratorMock(randint=[4])
    assert DecimalMutator.shift_value(DateTimePropertyMock(5, 2), '12.12m') == '21200m'
    DecimalMutator._generator = GeneratorMock(randint=[5])
    assert DecimalMutator.shift_value(DateTimePropertyMock(5, 2), '12.12m') == '12000m'

    DecimalMutator._generator = GeneratorMock(randint=[4])
    assert DecimalMutator.shift_value(DateTimePropertyMock(4, 2), '12.12m') == '1200m'
    DecimalMutator._generator = GeneratorMock(randint=[-1])
    assert DecimalMutator.shift_value(DateTimePropertyMock(4, 3), '12m') == '1.2m'
    DecimalMutator._generator = GeneratorMock(randint=[-2])
    assert DecimalMutator.shift_value(DateTimePropertyMock(4, 3), '12m') == '0.12m'
    DecimalMutator._generator = GeneratorMock(randint=[-3])
    assert DecimalMutator.shift_value(DateTimePropertyMock(4, 3), '12m') == '0.012m'
    DecimalMutator._generator = GeneratorMock(randint=[-4])
    assert DecimalMutator.shift_value(DateTimePropertyMock(4, 3), '12m') == '0.001m'

    DecimalMutator._generator = GeneratorMock(randint=[2])
    assert DecimalMutator.shift_value(DateTimePropertyMock(4, 3), '0m') == '0m'
    DecimalMutator._generator = GeneratorMock(randint=[3])
    assert DecimalMutator.shift_value(DateTimePropertyMock(4, 3), '12m') == '2000m'
    DecimalMutator._generator = GeneratorMock(randint=[4])
    assert DecimalMutator.shift_value(DateTimePropertyMock(4, 3), '12m') == '0m'
    DecimalMutator._generator = GeneratorMock(randint=[0])
    assert DecimalMutator.shift_value(DateTimePropertyMock(4, 3), '0.0m') == '0m'


def test_replace_digit_decimal_mutator():
    DecimalMutator._generator = GeneratorMock(randint=[0, 2])
    assert DecimalMutator.replace_digit(None, '1m') == '2m'
    DecimalMutator._generator = GeneratorMock(randint=[0, 9])
    assert DecimalMutator.replace_digit(None, '10m') == '90m'
    DecimalMutator._generator = GeneratorMock(randint=[2, 1])
    assert DecimalMutator.replace_digit(None, '100m') == '101m'
    DecimalMutator._generator = GeneratorMock(randint=[1, 1])
    assert DecimalMutator.replace_digit(None, '100m') == '110m'

    DecimalMutator._generator = GeneratorMock(randint=[2, 0, 2])
    assert DecimalMutator.replace_digit(None, '10.0m') == '20.0m'
    DecimalMutator._generator = GeneratorMock(randint=[2, 0, 0])
    assert DecimalMutator.replace_digit(None, '10.0m') == '0m'


def test_guid_mutator():
    guid_regex = '[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}' \
                 '-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}'
    guid = 'guid\'dddddddd-dddd-dddd-dddd-dddddddddddd\''

    random.seed(14)
    mutated_guid = GuidMutator.replace_char(guid)

    assert guid != mutated_guid
    assert re.match(f"guid'{guid_regex}'", mutated_guid)


def test_string_mutator_with_encoder():
    string = '\'12345+\''
    StringMutator._encode = encode_string

    random.seed(14)
    mutated_string = StringMutator._mutate(StringPropertyMock(10), string)

    assert mutated_string != string
    assert mutated_string == '\'123t5%2B\''


def test_string_mutator_without_encoder():
    string = '\'12345+\''
    StringMutator._encode = lambda x: x

    random.seed(14)
    mutated_string = StringMutator._mutate(StringPropertyMock(10), string)

    assert mutated_string != string
    assert mutated_string == '\'123t5+\''


class GeneratorMock:
    def __init__(self, randint=None):
        if randint:
            self._randint = iter(randint)

    def randint(self, frm, to):
        return next(self._randint)
