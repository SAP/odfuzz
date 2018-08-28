from collections import namedtuple

from odfuzz.mutators import DecimalMutator


def test_decimal_mutator():
    SelfMock = namedtuple('SelfMock', 'precision scale')
    assert DecimalMutator.shift_value(SelfMock(5, 2), '12.12m', -1) == '1.21m'
    assert DecimalMutator.shift_value(SelfMock(5, 2), '12.12m', -2) == '0.12m'
    assert DecimalMutator.shift_value(SelfMock(5, 2), '12.12m', -3) == '0.01m'
    assert DecimalMutator.shift_value(SelfMock(5, 2), '12.12m', -4) == '0m'
    assert DecimalMutator.shift_value(SelfMock(5, 2), '12.12m', -5) == '0m'

    assert DecimalMutator.shift_value(SelfMock(5, 2), '12.12m', 1) == '121.2m'
    assert DecimalMutator.shift_value(SelfMock(5, 2), '12.12m', 2) == '1212m'
    assert DecimalMutator.shift_value(SelfMock(5, 2), '12.12m', 3) == '12120m'
    assert DecimalMutator.shift_value(SelfMock(5, 2), '12.12m', 4) == '21200m'
    assert DecimalMutator.shift_value(SelfMock(5, 2), '12.12m', 5) == '12000m'

    assert DecimalMutator.shift_value(SelfMock(4, 2), '12.12m', 4) == '1200m'
    assert DecimalMutator.shift_value(SelfMock(4, 3), '12m', -1) == '1.2m'
    assert DecimalMutator.shift_value(SelfMock(4, 3), '12m', -2) == '0.12m'
    assert DecimalMutator.shift_value(SelfMock(4, 3), '12m', -3) == '0.012m'
    assert DecimalMutator.shift_value(SelfMock(4, 3), '12m', -4) == '0.001m'

    assert DecimalMutator.shift_value(SelfMock(4, 3), '0m', 2) == '0m'
    assert DecimalMutator.shift_value(SelfMock(4, 3), '12m', 3) == '2000m'
    assert DecimalMutator.shift_value(SelfMock(4, 3), '12m', 4) == '0m'
