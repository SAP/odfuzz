"""This module contains variety of generators and mutators."""

import random
import uuid
import datetime
import base64
import time

from odfuzz.constants import BASE_CHARSET, HEX_BINARY
from odfuzz.encoders import EncoderMixin

START_DATE = datetime.datetime(1900, 1, 1, 0, 0, 0)
END_DATE = datetime.datetime(9999, 12, 31, 23, 59, 59)
DATE_INTERVAL = (END_DATE - START_DATE).total_seconds()


class EdmBinary:

    def generate_body(value):
        return base64.b64encode(value.encode()).decode()

    @staticmethod
    def generate(format='uri'):
        prefix = 'X' if random.random() < 0.5 else 'binary'
        binary = ''.join([random.choice(HEX_BINARY) for _ in range(random.randrange(2, 20, 2))])
        value = '{0}\'{1}\''.format(prefix, binary)
        if format == 'body':
            return EdmBinary.generate_body(value)
        else:
            return value


class EdmBoolean:

    def generate_body():
        return True if random.random() < 0.5 else False

    @staticmethod
    def generate(format='uri'):
        if format == 'body':
            return EdmBoolean.generate_body()
        else:
            return 'true' if random.random() < 0.5 else 'false'


class EdmByte:
    @staticmethod
    def generate(format='uri'):
        return str(round(random.randint(0, 255)))


class EdmDateTime:

    def generate_body():
        return "\'/Date("+str(int(time.time()*1000))+")/\'"

    @staticmethod
    def generate(format='uri'):
        """
        The format of Edm.DateTime is defined as datetime'yyyy-mm-ddThh:mm[:ss[.fffffff]]'. The attribute Precision,
        which is used for declaring a microsecond as a decimal number, is ignored.
        """
        if format == 'body':
            return EdmDateTime.generate_body()
        else:
            random_date = START_DATE + datetime.timedelta(seconds=random.randint(0, DATE_INTERVAL))
            return 'datetime\'{0}\''.format(datetime.datetime.strftime(random_date, '%Y-%m-%dT%I:%M:%S'))


class EdmDecimal:
    @staticmethod
    def generate(self,format='uri'):
        divider = random.randint(1, 10 ** self.scale)
        scale_range = random.randint(0, self.scale)
        rand_int = random.randint(1, (10 ** (self.precision - scale_range)) - 1)
        return '{0:.{1}f}'.format(rand_int / divider, scale_range) + 'm'


class EdmDouble(EncoderMixin):
    @staticmethod
    def generate(format='uri'):
        random_double = '{}d'.format(round(random.uniform(2.23e-40, 1.19e+40), 15))
        return EdmDouble._encode_string(random_double)


class EdmSingle:
    @staticmethod
    def generate(format='uri'):
        return '{}f'.format(round(random.uniform(1.18e-20, 3.40e+20), 7))


class EdmGuid:
    @staticmethod
    def generate(format='uri'):
        return 'guid\'{0}\''.format(str(uuid.UUID(int=random.getrandbits(128), version=4)))


class EdmInt16:
    @staticmethod
    def generate(format='uri'):
        return str(random.randint(-32768, 32767))


class EdmInt32:
    @staticmethod
    def generate(format='uri'):
        return str(random.randint(-2147483648, 2147483647))


class EdmInt64:
    @staticmethod
    def generate(format='uri'):
        return str(random.randint(-9223372036854775808, 9223372036854775807)) + 'L'


class EdmSByte:
    @staticmethod
    def generate(format='uri'):
        return str(random.randint(-128, 127))


class EdmString:
    @staticmethod
    def generate(self,format='uri'):
        return '\'{}\''.format(RandomGenerator.random_string(self.max_length))


class EdmTime:
    @staticmethod
    def generate(format='uri'):
        random_time = START_DATE + datetime.timedelta(
            hours=random.randrange(23), minutes=random.randrange(59), seconds=random.randrange(59))
        return 'time\'P{0}\''.format(datetime.datetime.strftime(random_time, 'T%IH%MM%SS'))


class EdmDateTimeOffset:

    def generate_body():
        value = EdmDateTime.generate_body().rstrip(")/\'") + random.choice("+-") + str(random.randrange(720)) + ")/\'"
        return value

    @staticmethod
    def generate(format='uri'):
        if format == 'body':
            return EdmDateTimeOffset.generate_body()
        else:
            random_date = START_DATE + datetime.timedelta(seconds=random.randint(0, DATE_INTERVAL))
            formatted_datetime = datetime.datetime.strftime(random_date, '%Y-%m-%dT%I:%M:%S')
            offset = random.choice(['Z', '']) or ''.join(['-', str(random.randint(0, 24)), ':00'])
            return 'datetimeoffset\'{0}{1}\''.format(formatted_datetime, offset)


class RandomGenerator(EncoderMixin):
    @staticmethod
    def random_string(max_length,format='uri'):
        string_length = round(random.random() * max_length)
        generated_string = ''.join(random.choice(BASE_CHARSET) for _ in range(string_length))
        return RandomGenerator._encode_string(generated_string)
