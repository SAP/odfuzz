"""This module contains variety of generators and mutators."""

import random
import uuid
import datetime
import base64
import time

from odfuzz.constants import BASE_CHARSET, HEX_BINARY
from odfuzz.encoders import EncoderMixin
from odfuzz.config import Config

START_DATE = datetime.datetime(1970, 1, 1, 0, 0, 0)
END_DATE = datetime.datetime(3000, 12, 31, 23, 59, 59)

'''The END_DATE is reduced to 23:59:59 31st DEC 3000 as that is the highest supported timestamp possible on Windows x64 platforms. 
https://docs.microsoft.com/en-us/cpp/c-runtime-library/reference/localtime-localtime32-localtime64 '''

DATE_INTERVAL = (END_DATE - START_DATE).total_seconds()


class EdmBinary:

    def generate_body(value):
        return base64.b64encode(value.encode()).decode()

    @staticmethod
    def generate(generator_format='uri'):
        prefix = 'X' if random.random() < 0.5 else 'binary'
        binary = ''.join([random.choice(HEX_BINARY) for _ in range(random.randrange(2, 20, 2))])
        value = '{0}\'{1}\''.format(prefix, binary)
        if generator_format == 'body':
            return EdmBinary.generate_body(value)
        elif generator_format == 'uri':
            return value
        elif generator_format == 'key':
            return value, EdmBinary.generate_body(value)
        else:
            raise ValueError

class EdmBoolean:

    @staticmethod
    def generate(generator_format='uri'):
        if generator_format == 'body':
            return True if random.random() < 0.5 else False
        elif generator_format == 'uri':
            return 'true' if random.random() < 0.5 else 'false'
        elif generator_format == 'key':
            if random.random() < 0.5:
                return "true", True
            else:
                return "false", False
        else:
            raise ValueError

class EdmByte:
    @staticmethod
    def generate(generator_format='uri'):
        value = round(random.randint(0, 255))
        if generator_format == 'uri':
            return str(value)
        elif generator_format == 'body':
            return value
        elif generator_format == 'key':
            return str(value), value
        else:
            raise ValueError


class EdmDateTime:

    @staticmethod
    def generate(generator_format='uri'):
        """
        The format of Edm.DateTime is defined as datetime'yyyy-mm-ddThh:mm[:ss[.fffffff]]'. The attribute Precision,
        which is used for declaring a microsecond as a decimal number, is ignored.
        """
        body_value = random.randint(0, DATE_INTERVAL)
        random_date = START_DATE + datetime.timedelta(seconds=body_value)
        uri_value = 'datetime\'{0}\''.format(datetime.datetime.strftime(random_date, '%Y-%m-%dT%I:%M:%S'))
        body_value = "/Date({})/".format(body_value)
        if generator_format == 'uri':
            return uri_value
        elif generator_format == 'body':
            return body_value
        elif generator_format == 'key':
            return uri_value, body_value




class EdmDecimal:
    @staticmethod
    def generate(self,generator_format='uri'):
        if self.precision == self.scale:
            rand_decimal = random.randint(1, (10 ** self.precision) - 1) / (10 ** self.scale)
            sap_value = "{}".format(rand_decimal)
        else:
            divider = random.randint(1, 10 ** self.scale)
            scale_range = random.randint(0, self.scale)
            rand_int = random.randint(1, (10 ** (self.precision - scale_range)) - 1)
            sap_value = '{0:.{1}f}'.format(rand_int / divider, scale_range)
        
        generic_value = sap_value + 'm'
        if generator_format == 'uri':
            return generic_value
        elif generator_format == 'body':
            if Config.fuzzer.sap_vendor_enabled == True:
                return sap_value
            else:
                return generic_value
        elif generator_format == 'key':
            if Config.fuzzer.sap_vendor_enabled == True:
                return generic_value, sap_value
            else:
                return generic_value, generic_value
        else:
            raise ValueError

class EdmDouble(EncoderMixin):
    @staticmethod
    def generate(generator_format='uri'):
        random_double = '{}d'.format(round(random.uniform(2.23e-40, 1.19e+40), 15))
        value = EdmDouble._encode_string(random_double)
        if generator_format == 'uri' or generator_format == 'body':
            return value
        elif generator_format == 'key':
            return value , value
        else:
            raise ValueError


class EdmSingle:
    @staticmethod
    def generate(generator_format='uri'):
        value = '{}f'.format(round(random.uniform(1.18e-20, 3.40e+20), 7))
        if generator_format == 'uri' or generator_format == 'body':
            return value
        elif generator_format == 'key':
            return value , value
        else:
            raise ValueError


class EdmGuid:
    @staticmethod
    def generate(generator_format='uri'):
        body_value = str(uuid.UUID(int=random.getrandbits(128), version=4))
        uri_value = 'guid\'{0}\''.format(body_value)
        if generator_format == 'uri':
            return uri_value
        elif generator_format == 'body':
            return body_value
        elif generator_format == 'key':
            return uri_value , body_value
        else:
            raise ValueError


class EdmInt16:
    @staticmethod
    def generate(generator_format='uri'):
        value = random.randint(-32768, 32767)
        if generator_format == 'uri':
            return str(value)
        elif generator_format == 'body':
            return value
        elif generator_format == 'key':
            return str(value) , value
        else:
            raise ValueError


class EdmInt32:
    @staticmethod
    def generate(generator_format='uri'):
        value = random.randint(-2147483648, 2147483647)
        if generator_format == 'uri':
            return str(value)
        elif generator_format == 'body':
            return value
        elif generator_format == 'key':
            return str(value) , value
        else:
            raise ValueError


class EdmInt64:
    @staticmethod
    def generate(generator_format='uri'):
        value = str(random.randint(-9223372036854775808, 9223372036854775807)) + 'L'
        if generator_format == 'uri' or generator_format == 'body':
            return value
        elif generator_format == 'key':
            return value , value
        else:
            raise ValueError


class EdmSByte:
    @staticmethod
    def generate(generator_format='uri'):
        value = random.randint(-128, 127)
        if generator_format == 'uri':
            return str(value)
        elif generator_format == 'body':
            return value
        elif generator_format == 'key':
            return str(value) , value
        else:
            raise ValueError

class EdmString:
    @staticmethod
    def generate(self,generator_format='uri'):
        if generator_format == 'uri' or generator_format == 'body':
            if hasattr(self, 'non_negative')== False or self.non_negative==False:
            #if sap:display-format="NonNegative" is used in Edm.String properties, then the string should contain only numeric characters
            #Because of StringSelf in entities.py (used in StringFilterFunctions.func_concat()) doesnt have non-negative property, so hasattr() is used.
                value = '\'{}\''.format(RandomGenerator.random_string(self.max_length, generator_format))
            else:
                upper_limit = (10**self.max_length)-1
                value = '\'{}\''.format(random.randint(0,upper_limit))
            return value
        elif generator_format == 'key':
            if hasattr(self, 'non_negative')== False or self.non_negative==False:
                uri_value,body_value = RandomGenerator.random_string(self.max_length, 'key')
            else:
                upper_limit = (10**self.max_length)-1
                uri_value = body_value = str(random.randint(0,upper_limit))
            uri_value = '\'{}\''.format(uri_value)
            return uri_value , body_value
        else:
            raise ValueError


class EdmTime:
    @staticmethod
    def generate(generator_format='uri'):
        random_time = START_DATE + datetime.timedelta(
            hours=random.randrange(23), minutes=random.randrange(59), seconds=random.randrange(59))
        sap_value = 'P{}'.format(datetime.datetime.strftime(random_time, 'T%IH%MM%SS'))
        generic_value = 'time\'{0}\''.format(sap_value)
        if generator_format == 'uri':
            return generic_value
        elif generator_format == 'body':
            if Config.fuzzer.sap_vendor_enabled == True:
                return sap_value
            else:
                return generic_value
        elif generator_format == 'key':
            if Config.fuzzer.sap_vendor_enabled == True:
                return generic_value, sap_value
            else:
                return generic_value, generic_value
        else:
            raise ValueError


class EdmDateTimeOffset:

    @staticmethod
    def generate(generator_format='uri'):
        random_date = START_DATE + datetime.timedelta(seconds=random.randint(0, DATE_INTERVAL))
        formatted_datetime = datetime.datetime.strftime(random_date, '%Y-%m-%dT%I:%M:%S')
        offset = f'{random.randint(0, 1439):04d}'
        offset_operator = random.choice('+-')
        sap_offset = ''.join([offset_operator,offset])
        div, mod  = divmod(int(offset),60)
        generic_offset = ''.join([offset_operator, f'{div:02d}',':', f'{mod:02d}'])
        generic_value = 'datetimeoffset\'{0}{1}\''.format(formatted_datetime, generic_offset)
        sap_value = "/Date({0}{1})/".format(int(random_date.timestamp()),sap_offset)
        if Config.fuzzer.sap_vendor_enabled == True:
            if generator_format == 'uri':
                return generic_value
            elif generator_format == 'body':
                return sap_value
            elif generator_format == 'key':
                return generic_value, sap_value
            else:
                raise ValueError

        else:
            if generator_format == 'body' or generator_format == 'uri':
                return generic_value
            elif generator_format == 'key':
                return generic_value, generic_value
            else:
                raise ValueError

class RandomGenerator(EncoderMixin):
    @staticmethod
    def random_string(max_length, generator_format = 'uri'):
        string_length = round(random.random() * max_length)
        generated_string = ''.join(random.choice(BASE_CHARSET) for _ in range(string_length))
        if generator_format == 'uri':
            return RandomGenerator._encode_string(generated_string)
        elif generator_format == 'body':
            return generated_string
        else:
            return (RandomGenerator._encode_string(generated_string) , generated_string)
