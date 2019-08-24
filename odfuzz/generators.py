"""This module contains variety of generators and mutators."""

import random
import uuid
import datetime

from odfuzz.constants import BASE_CHARSET, HEX_BINARY

START_DATE = datetime.datetime(1900, 1, 1, 0, 0, 0)
END_DATE = datetime.datetime(9999, 12, 31, 23, 59, 59)
DATE_INTERVAL = (END_DATE - START_DATE).total_seconds()


class EdmGenerator:
    @staticmethod
    def edm_binary():
        prefix = 'X' if random.random() < 0.5 else 'binary'
        binary = ''.join([random.choice(HEX_BINARY) for _ in range(random.randrange(2, 20, 2))])
        return '{0}\'{1}\''.format(prefix, binary)

    @staticmethod
    def edm_boolean():
        boolean = 'true' if random.random() < 0.5 else 'false'
        return boolean

    @staticmethod
    def edm_byte():
        random_int = round(random.random() * 255)
        return str(random_int)

    @staticmethod
    def edm_datetime():
        """
        The format of Edm.DateTime is defined as datetime'yyyy-mm-ddThh:mm[:ss[.fffffff]]'. The attribute Precision,
        which is used for declaring a microsecond as a decimal number, is ignored.
        """
        random_date = START_DATE + datetime.timedelta(seconds=random.randint(0, DATE_INTERVAL))
        return 'datetime\'{0}\''.format(datetime.datetime.strftime(random_date, '%Y-%m-%dT%I:%M:%S'))

    @staticmethod
    def edm_decimal(self):
        divider = random.randint(1, 10 ** self.scale)
        scale_range = random.randint(0, self.scale)
        return '{0:.{1}f}'.format(
            random.randint(1, (10 ** (self.precision - scale_range)) - 1) / divider, scale_range) + 'm'

    @staticmethod
    def edm_double():
        return '{}d'.format(round(random.uniform(2.23e-40, 1.19e+40), 15))

    @staticmethod
    def edm_single():
        return '{0:.7f}'.format(random.uniform(-10000000000, 10000000000)) + 'f'

    @staticmethod
    def edm_guid():
        return 'guid\'{0}\''.format(str(uuid.UUID(int=random.getrandbits(128), version=4)))

    @staticmethod
    def edm_int16():
        return str(random.randint(-32768, 32767))

    @staticmethod
    def edm_int32():
        return str(random.randint(-2147483648, 2147483647))

    @staticmethod
    def edm_int64():
        return str(random.randint(-9223372036854775808, 9223372036854775807)) + 'L'

    @staticmethod
    def edm_sbyte():
        return str(random.randint(-128, 127))

    @staticmethod
    def edm_string(self):
        generated_string = RandomGenerator.random_string(self.max_length)
        return '\'{}\''.format(generated_string)

    @staticmethod
    def edm_time():
        random_time = START_DATE + datetime.timedelta(
            hours=random.randrange(23), minutes=random.randrange(59), seconds=random.randrange(59))
        return 'time\'P{0}\''.format(datetime.datetime.strftime(random_time, 'T%IH%MM%SS'))

    @staticmethod
    def edm_datetimeoffset():
        random_date = START_DATE + datetime.timedelta(seconds=random.randint(0, DATE_INTERVAL))
        formatted_datetime = datetime.datetime.strftime(random_date, '%Y-%m-%dT%I:%M:%S')
        offset = random.choice(['Z', '']) or ''.join(['-', str(random.randint(0, 24)), ':00'])
        return 'datetimeoffset\'{0}{1}\''.format(formatted_datetime, offset)


class RandomGenerator:
    @staticmethod
    def random_string(max_length):
        string_length = round(random.random() * max_length)
        generated_string = ''.join(random.choice(BASE_CHARSET) for _ in range(string_length))
        return generated_string
