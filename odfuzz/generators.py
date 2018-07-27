"""This module contains variety of generators and mutators."""

import random
import uuid
import datetime

HEX_BINARY = 'ABCDEFabcdef0123456789'
BASE_CHARSET = 'abcdefghijklmnopqrstuvxyzABCDEFGHIJKLMNOPQRSTUVXYZ0123456789~!$@^*()_+-–—=' \
               '[]|:<>.‰¨œƒ…†‡Œ‘’´`“”•™¡¢£¤¥¦§©ª«¬®¯°±²³µ¶·¸¹º»¼½¾¿ÀÁÂÃÄÅÆÇÈÉÊËÌÍ' \
               'ÎÏÐÑÒÓÔÕÖ×ØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõö÷øùúûüýþÿ{} '

START_DATE = datetime.datetime(1900, 1, 1, 0, 0, 0)
END_DATE = datetime.datetime(9999, 12, 31, 23, 59, 59)
DATE_INTERVAL = (END_DATE - START_DATE).total_seconds()

SEMICOLON = 0x3B
APOSTROPHE = 0x27
NEW_LINE = 0x0A
FORBIDDEN_CHARS = (SEMICOLON, APOSTROPHE, NEW_LINE)
GUID_DASH_INDEXES = (8, 13, 18, 23)


class StringMutator(object):
    @staticmethod
    def flip_bit(self, original_string):
        string = original_string[1:-1]
        if not string:
            return original_string

        index = round(random.random() * (len(string) - 1))
        ord_char = ord(string[index])
        ord_char ^= 1 << round(random.random() * ord_char.bit_length()) + 1
        ord_char = 0x10FFFF if ord_char > 0x10FFFF else ord_char
        ord_char = replace_if_is_semicolon(ord_char)
        generated_string = ''.join([string[:index], chr(ord_char), string[index + 1:]]).encode(errors='surrogatepass')
        return '\'' + generated_string.decode(errors='replace') + '\''

    @staticmethod
    def replace_char(self, original_string):
        string = original_string[1:-1]
        if not string:
            return original_string

        index = round(random.random() * (len(string) - 1))
        ord_char = round(random.random() * (0x10ffff - 1) + 1)
        ord_char = replace_if_is_semicolon(ord_char)
        generated_string = ''.join([string[:index], chr(ord_char), string[index + 1:]]).encode(errors='surrogatepass')
        return '\'' + generated_string.decode(errors='replace') + '\''

    @staticmethod
    def swap_chars(self, original_string):
        string = original_string[1:-1]
        if not string:
            return original_string

        index_length = len(string) - 1
        index1 = round(random.random() * index_length)
        index2 = round(random.random() * index_length)
        if index1 == index2:
            index2 = round(random.random() * index_length)

        list_char = list(string)
        list_char[index1], list_char[index2] = string[index2], string[index1]
        return '\'' + ''.join(list_char) + '\''

    @staticmethod
    def invert_chars(self, original_string):
        string = original_string[1:-1]
        if len(string) < 3:
            return original_string

        index_len = len(string) - 1
        start_index = round(random.random() * (index_len - 2))
        end_index = round(random.random() * (index_len - start_index - 1)) + start_index + 2
        slice_char = string[start_index:end_index]

        list_char = list(string)
        list_char[start_index:end_index] = slice_char[::-1]
        return '\'' + ''.join(list_char) + '\''

    @staticmethod
    def add_char(self, string):
        string = string[1:-1]
        index = round(random.random() * (len(string)))
        new_char = random.choice(BASE_CHARSET)
        generated_string = ''.join([string[:index], new_char, string[index:]])
        if self.max_string_length < len(generated_string):
            generated_string = generated_string[:-1]
        return '\'' + generated_string + '\''

    @staticmethod
    def delete_char(self, original_string):
        string = original_string[1:-1]
        if len(string) >= 3:
            index = round(random.random() * (len(string) - 1))
            return '\'' + ''.join([string[:index], string[index + 1:]]) + '\''
        else:
            return original_string


class NumberMutator(object):
    @staticmethod
    def increment_value(self, string_number):
        if not string_number:
            string_number = '0'
        return str(int(string_number) + 1)

    @staticmethod
    def decrement_value(self, string_number):
        if not string_number:
            string_number = '0'
        value = int(string_number) - 1
        if value < 0:
            value = 0
        return str(value)

    @staticmethod
    def add_digit(self, string_number):
        digit = round(random.random() * 9)
        position = round(random.random() * len(string_number))
        string_number = ''.join([string_number[:position], str(digit), string_number[position:]])
        return string_number

    @staticmethod
    def delete_digit(self, string_number):
        if not string_number:
            return '0'
        if len(string_number) > 1:
            index = round(random.random() * (len(string_number) - 1))
            generated_number = ''.join([string_number[:index], string_number[index + 1:]])
        else:
            return '0'
        return generated_number


class GuidMutator(object):
    @staticmethod
    def replace_char(string_guid):
        without_dashes = string_guid
        index = round(random.random() * (len(string_guid) - 1))
        if index in GUID_DASH_INDEXES:
            index -= 1
        rand_hex_char = HEX_BINARY[round(random.random() * (len(HEX_BINARY) - 1))]
        without_dashes = ''.join([without_dashes[:index], rand_hex_char, without_dashes[index + 1:]])
        return without_dashes


class RandomGenerator(object):
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
        random_date = START_DATE + datetime.timedelta(seconds=random.randint(0, DATE_INTERVAL))
        return 'datetime\'{0}\''.format(datetime.datetime.strftime(random_date, '%Y-%m-%dT%I:%M'))

    @staticmethod
    def edm_decimal(self):
        divider = random.randint(1, 10 ** self.scale)
        scale_range = random.randint(0, self.scale)
        return '{0:.{1}f}'.format(
            random.randint(1, (10 ** (self.precision - scale_range)) - 1)
            / divider, scale_range) + 'm'

    @staticmethod
    def edm_double():
        return str(round(random.uniform(-1.79e+30, 1.79e+30), 15)) + 'd'

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
        string_length = round(random.random() * self.max_string_length)
        string = ''.join(random.choice(BASE_CHARSET) for _ in range(string_length))
        return '\'{}\''.format(string)

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


def replace_if_is_semicolon(hex_char):
    if hex_char in FORBIDDEN_CHARS:
        return hex_char - 1
    return hex_char
