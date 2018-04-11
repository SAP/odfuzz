"""This module contains variety of generators and mutators."""

import random
import uuid
import datetime

HEX_BINARY = 'ABCDEFabcdef0123456789'
BASE_CHARSET = 'abcdefghijklmnopqrstuvxyzABCDEFGHIJKLMNOPQRSTUVXYZ0123456789~!$@^*()_+-–—=' \
               '[]|:<>?,./‰¨œƒ…†‡Œ‘’´`“”•™¡¢£¤¥¦§©ª«¬®¯°±²³µ¶·¸¹º»¼½¾¿ÀÁÂÃÄÅÆÇÈÉÊËÌÍ' \
               'ÎÏÐÑÒÓÔÕÖ×ØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõö÷øùúûüýþÿ{} '

START_DATE = datetime.datetime(1900, 1, 1, 0, 0, 0)
END_DATE = datetime.datetime(9999, 12, 31, 23, 59, 59)
DATE_INTERVAL = (END_DATE - START_DATE).total_seconds()


class StringMutator(object):
    @staticmethod
    def flip_bit(string):
        index = round(random.random() * (len(string) - 1))
        ord_char = ord(string[index])
        ord_char ^= 1 << round(random.random() * (ord_char.bit_length()))
        return ''.join([string[:index], chr(ord_char), string[index + 1:]])

    @staticmethod
    def replace_char(string):
        index = round(random.random() * (len(string) - 1))
        rand_char = chr(round(random.random() * 0x10ffff))
        return ''.join([string[:index], rand_char, string[index + 1:]])

    @staticmethod
    def swap_chars(string):
        index_length = len(string) - 1
        index1 = round(random.random() * index_length)
        index2 = round(random.random() * index_length)
        while index1 == index2:
            index2 = round(random.random() * index_length)

        list_char = list(string)
        list_char[index1], list_char[index2] = string[index2], string[index1]
        return ''.join(list_char)

    @staticmethod
    def invert_chars(string):
        index_len = len(string) - 1
        start_index = round(random.random() * (index_len - 2))
        end_index = round(random.random() * (index_len - start_index - 1)) + start_index + 2
        slice_char = string[start_index:end_index]

        list_char = list(string)
        list_char[start_index:end_index] = slice_char[::-1]
        return ''.join(list_char)

    @staticmethod
    def add_char(string):
        index = round(random.random() * (len(string)))
        new_char = random.choice(BASE_CHARSET)
        return ''.join([string[:index], new_char, string[index:]])

    @staticmethod
    def delete_char(string):
        index = round(random.random() * (len(string) - 1))
        return ''.join([string[:index], string[index + 1:]])


class NumberMutator(object):
    @staticmethod
    def flip_bit(number):
        pass

    @staticmethod
    def increment_value(number):
        return number + 1

    @staticmethod
    def decrement_value(number):
        return number - 1

    @staticmethod
    def add_digit(number):
        pass

    @staticmethod
    def delete_digit(number):
        pass


class RandomGenerator(object):
    @staticmethod
    def edm_binary():
        prefix = 'X' if random.random() < 0.5 else 'binary'
        binary = ''.join([random.choice(HEX_BINARY) for _ in range(random.randint(0, 20000))])
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
    def edm_decimal(precision, scale):
        divider = random.randint(1, 10 ** scale)
        scale_range = random.randint(0, scale)
        return '{0:.{1}f}'.format(
            random.randint(1, (10 ** (precision - scale_range)) - 1) / divider, scale_range) + 'm'

    @staticmethod
    def edm_double():
        return str(round(random.uniform(2.23e-30, 1.79e+308), 15)) + 'd'

    @staticmethod
    def edm_single():
        return '{0:.7f}'.format(random.uniform(-10000000000, 10000000000)) + 'f'

    @staticmethod
    def edm_guid():
        return 'guid\'{0}\''.format(str(uuid.UUID(int=random.getrandbits(128))))

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
    def edm_string(min_length, max_length):
        string = ''.join(random.choice(BASE_CHARSET)
                         for _ in range(random.randint(min_length, max_length)))
        return '\'{}\''.format(string)

    @staticmethod
    def edm_time():
        random_time = START_DATE + datetime.timedelta(hours=random.randrange(23),
                                                      minutes=random.randrange(59),
                                                      seconds=random.randrange(59))
        return 'time\'P{0}\''.format(datetime.datetime.strftime(random_time, 'T%IH%MM%SS'))

    @staticmethod
    def edm_datetimeoffset():
        random_date = START_DATE + datetime.timedelta(seconds=random.randint(0, DATE_INTERVAL))
        formatted_datetime = datetime.datetime.strftime(random_date, '%Y-%m-%dT%I:%M:%S')
        offset = random.choice(['Z', '']) or ''.join(['-', str(random.randint(0, 24)), ':00'])
        return 'datetimeoffset\'{0}{1}\''.format(formatted_datetime, offset)
