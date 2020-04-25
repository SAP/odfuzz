import random

from datetime import datetime
from dateutil.relativedelta import relativedelta

from odfuzz.constants import BASE_CHARSET, HEX_BINARY, INT_MAX

class StringMutator:
    _methods = []

    @staticmethod
    def _mutate(proprty, value):
        if not StringMutator._methods:
            StringMutator._methods = [func_name for func_name in StringMutator.__dict__ if not func_name.startswith('_')]
        func_name = random.choice(StringMutator._methods)
        mutated_value = getattr(StringMutator, func_name)(proprty, value)
        return mutated_value

    @staticmethod
    def flip_bit(self, original_string):
        string = original_string[1:-1]
        if not string:
            return original_string

        index = round(random.random() * (len(string) - 1))
        ord_char = ord(string[index])
        ord_char ^= 1 << round(random.random() * ord_char.bit_length()) + 1
        ord_char = 0x10FFFF if ord_char > 0x10FFFF else ord_char # see https://stackoverflow.com/questions/52203351/why-unicode-is-restricted-to-0x10ffff
        ord_char = normalize_surrogates(ord_char)
        generated_string = ''.join([string[:index], chr(ord_char), string[index + 1:]])
        return '\'' + generated_string + '\''

    @staticmethod
    def replace_char(self, original_string):
        string = original_string[1:-1]
        if not string:
            return original_string

        index = round(random.random() * (len(string) - 1))
        ord_char = round(random.random() * (0x10ffff - 1) + 1) #see https://stackoverflow.com/questions/52203351/why-unicode-is-restricted-to-0x10ffff
        ord_char = normalize_surrogates(ord_char)
        generated_string = ''.join([string[:index], chr(ord_char), string[index + 1:]])
        return '\'' + generated_string + '\''

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
        if self.max_length < len(generated_string):
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


class NumberMutator:
    _methods = []

    @staticmethod
    def _mutate(proprty, value):
        if not NumberMutator._methods:
            NumberMutator._methods = [func_name for func_name in NumberMutator.__dict__ if not func_name.startswith('_')]
        func_name = random.choice(NumberMutator._methods)
        mutated_value = getattr(NumberMutator, func_name)(proprty, value)
        return mutated_value

    @staticmethod
    def increment_value(self, string_number):
        if not string_number:
            string_number = '0'
        if string_number.endswith('L'):
            appendix = 'L'
            string_number = string_number[:-1]
        else:
            appendix = ''

        number = int(string_number) + 1
        if number > INT_MAX:
            number = 1
        return str(number) + appendix

    @staticmethod
    def decrement_value(self, string_number):
        if not string_number:
            string_number = '0'
        if string_number.endswith('L'):
            appendix = 'L'
            string_number = string_number[:-1]
        else:
            appendix = ''
        value = int(string_number) - 1
        if value < 0:
            value = 0
        return str(value) + appendix

    @staticmethod
    def add_digit(self, string_number):
        if string_number.endswith('L'):
            appendix = 'L'
            string_number = string_number[:-1]
        else:
            appendix = ''

        if string_number.startswith('-'):
            prefix = '-'
            string_number = string_number[1:]
        else:
            prefix = ''

        digit = round(random.random() * 9)
        position = round(random.random() * len(string_number))
        string_number = ''.join([string_number[:position], str(digit), string_number[position:]])

        number = int(string_number)
        if number > INT_MAX:
            number = number - INT_MAX
        return prefix + str(number) + appendix

    @staticmethod
    def delete_digit(self, string_number):
        """
        Remove a digit at random position.

        This method has a side effect. A minus sign may be removed from the number as well. Therefore, the value
        of mutated number may be higher than expected (e.g. -123 is changed to 123).
        """
        if not string_number:
            return '0'
        if string_number.endswith('L'):
            appendix = 'L'
            string_number = string_number[:-1]
        else:
            appendix = ''
        if len(string_number) > 1:
            index = round(random.random() * (len(string_number) - 1))
            generated_number = ''.join([string_number[:index], string_number[index + 1:]])
        else:
            return '0'
        return generated_number + appendix


class GuidMutator:
    GUID_DASH_INDEXES = (8, 13, 18, 23)  # mandatory part of GUUID, "-"

    @staticmethod
    def replace_char(string_guid):
        # get the proper index to the string array by skipping the prefix "guid'"
        # and trimming the last single quote enclosing the GUUID part
        index = round(random.random() * (len(string_guid) - 2 - 5)) + 5
        if index in GuidMutator.GUID_DASH_INDEXES:
            index -= 1
        rand_hex_char = HEX_BINARY[round(random.random() * (len(HEX_BINARY) - 1))]
        mutated_guid = ''.join([string_guid[:index], rand_hex_char, string_guid[index + 1:]])
        return mutated_guid


class BooleanMutator:
    @staticmethod
    def flip_value(boolean):
        return 'true' if boolean == 'false' else 'false'


class DecimalMutator:
    _generator = random
    _methods = []

    @staticmethod
    def _mutate(proprty, value):
        if not DecimalMutator._methods:
            DecimalMutator._methods = [func_name for func_name in DecimalMutator.__dict__ if not func_name.startswith('_')]
        func_name = random.choice(DecimalMutator._methods)
        mutated_value = getattr(DecimalMutator, func_name)(proprty, value)
        return mutated_value

    @staticmethod
    def replace_digit(self, decimal_value):
        # remove trailing m|M
        decimal_value = decimal_value[:-1]

        # get index of random digit
        max_index = len(decimal_value) - 1
        random_index = DecimalMutator._generator.randint(0, max_index)
        while decimal_value[random_index] == '.':
            random_index = DecimalMutator._generator.randint(0, max_index)

        # replace selected digit with random digit
        digit = str(DecimalMutator._generator.randint(0, 9))
        decimal_value = ''.join((decimal_value[:random_index], digit, decimal_value[random_index + 1:]))

        if not float(decimal_value):
            return '0m'
        else:
            return decimal_value + 'm'

    @staticmethod
    def shift_value(self, decimal_value):
        # remove trailing m|M
        decimal_value = decimal_value[:-1]

        # init index of shifted decimal point
        point_index = decimal_value.find('.')
        if point_index == -1:
            point_index = len(decimal_value)
        decimal_value = decimal_value.replace('.', '')
        to_shift = DecimalMutator._generator.randint(-self.precision, self.precision)
        abs_shift = abs(to_shift)
        shifted_point_index = abs_shift + point_index + to_shift

        # create valid right and left parts to the decimal point
        max_sized_decimal = ''.join(('0' * abs_shift, decimal_value, '0' * abs_shift))
        left_part = max_sized_decimal[:shifted_point_index].lstrip('0')
        right_part = max_sized_decimal[shifted_point_index:].rstrip('0')

        # normalize value
        left_part = left_part[-self.precision:]
        right_part = right_part[:self.scale].rstrip('0')
        if not left_part or int(left_part) == 0:
            left_part = '0'
        if not right_part:
            mutated_value = ''.join((left_part, 'm'))
        else:
            mutated_value = ''.join((left_part, '.', right_part, 'm'))

        return mutated_value


class DateTimeMutator:
    _methods = []

    @staticmethod
    def _mutate(proprty, value):
        if not DateTimeMutator._methods:
            DateTimeMutator._methods = [func_name for func_name in DateTimeMutator.__dict__ if not func_name.startswith('_')]
        func_name = random.choice(DateTimeMutator._methods)
        mutated_value = getattr(DateTimeMutator, func_name)(proprty, value)
        return mutated_value

    @staticmethod
    def _mutate_date(date_time, time_delta):
        converted_date = datetime.strptime(date_time.replace('datetime', '').replace('\'', ''), '%Y-%m-%dT%I:%M:%S')
        mutated_date = converted_date + time_delta
        return 'datetime\'{}\''.format(datetime.strftime(mutated_date, '%Y-%m-%dT%I:%M:%S'))

    @staticmethod
    def increment_day(self, date_time):
        return DateTimeMutator._mutate_date(date_time, relativedelta(days=1))

    @staticmethod
    def decrement_day(self, date_time):
        return DateTimeMutator._mutate_date(date_time, -relativedelta(days=1))

    @staticmethod
    def increment_month(self, date_time):
        return DateTimeMutator._mutate_date(date_time, relativedelta(months=1))

    @staticmethod
    def decrement_month(self, date_time):
        return DateTimeMutator._mutate_date(date_time, -relativedelta(months=1))

    @staticmethod
    def increment_year(self, date_time):
        return DateTimeMutator._mutate_date(date_time, relativedelta(years=1))

    @staticmethod
    def decrement_year(self, date_time):
        return DateTimeMutator._mutate_date(date_time, -relativedelta(years=1))


def normalize_surrogates(ord_char):
    if 0xD800 <= ord_char <= 0xDFFF:
        return 0xD7FF
    return ord_char
