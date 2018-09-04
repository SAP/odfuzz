from collections import namedtuple

from odfuzz.mutators import DecimalMutator

SelfMock = namedtuple('SelfMock', 'precision scale')


def test_shift_value_decimal_mutator():
    DecimalMutator._generator = GeneratorMock(randint=[-1])
    assert DecimalMutator.shift_value(SelfMock(5, 2), '12.12m') == '1.21m'
    DecimalMutator._generator = GeneratorMock(randint=[-2])
    assert DecimalMutator.shift_value(SelfMock(5, 2), '12.12m') == '0.12m'
    DecimalMutator._generator = GeneratorMock(randint=[-3])
    assert DecimalMutator.shift_value(SelfMock(5, 2), '12.12m') == '0.01m'
    DecimalMutator._generator = GeneratorMock(randint=[-4])
    assert DecimalMutator.shift_value(SelfMock(5, 2), '12.12m') == '0m'
    DecimalMutator._generator = GeneratorMock(randint=[-5])
    assert DecimalMutator.shift_value(SelfMock(5, 2), '12.12m') == '0m'

    DecimalMutator._generator = GeneratorMock(randint=[1])
    assert DecimalMutator.shift_value(SelfMock(5, 2), '12.12m') == '121.2m'
    DecimalMutator._generator = GeneratorMock(randint=[2])
    assert DecimalMutator.shift_value(SelfMock(5, 2), '12.12m') == '1212m'
    DecimalMutator._generator = GeneratorMock(randint=[3])
    assert DecimalMutator.shift_value(SelfMock(5, 2), '12.12m') == '12120m'
    DecimalMutator._generator = GeneratorMock(randint=[4])
    assert DecimalMutator.shift_value(SelfMock(5, 2), '12.12m') == '21200m'
    DecimalMutator._generator = GeneratorMock(randint=[5])
    assert DecimalMutator.shift_value(SelfMock(5, 2), '12.12m') == '12000m'

    DecimalMutator._generator = GeneratorMock(randint=[4])
    assert DecimalMutator.shift_value(SelfMock(4, 2), '12.12m') == '1200m'
    DecimalMutator._generator = GeneratorMock(randint=[-1])
    assert DecimalMutator.shift_value(SelfMock(4, 3), '12m') == '1.2m'
    DecimalMutator._generator = GeneratorMock(randint=[-2])
    assert DecimalMutator.shift_value(SelfMock(4, 3), '12m') == '0.12m'
    DecimalMutator._generator = GeneratorMock(randint=[-3])
    assert DecimalMutator.shift_value(SelfMock(4, 3), '12m') == '0.012m'
    DecimalMutator._generator = GeneratorMock(randint=[-4])
    assert DecimalMutator.shift_value(SelfMock(4, 3), '12m') == '0.001m'

    DecimalMutator._generator = GeneratorMock(randint=[2])
    assert DecimalMutator.shift_value(SelfMock(4, 3), '0m') == '0m'
    DecimalMutator._generator = GeneratorMock(randint=[3])
    assert DecimalMutator.shift_value(SelfMock(4, 3), '12m') == '2000m'
    DecimalMutator._generator = GeneratorMock(randint=[4])
    assert DecimalMutator.shift_value(SelfMock(4, 3), '12m') == '0m'
    DecimalMutator._generator = GeneratorMock(randint=[0])
    assert DecimalMutator.shift_value(SelfMock(4, 3), '0.0m') == '0m'


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


class GeneratorMock:
    def __init__(self, randint=None):
        if randint:
            self._randint = iter(randint)

    def randint(self, frm, to):
        return next(self._randint)
