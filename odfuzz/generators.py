"""This module contains variety of generators and mutators."""

import random

BASE_CHARSET = 'abcdefghijklmnopqrstuvxyzABCDEFGHIJKLMNOPQRSTUVXYZ0123456789~!$@^*()_+-–—=' \
               '[]|:<>?,./‰¨œƒ…†‡Œ‘’´`“”•™¡¢£¤¥¦§©ª«¬®¯°±²³µ¶·¸¹º»¼½¾¿ÀÁÂÃÄÅÆÇÈÉÊËÌÍ' \
               'ÎÏÐÑÒÓÔÕÖ×ØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõö÷øùúûüýþÿ{} '


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
