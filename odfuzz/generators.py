"""This module contains variety of generators and mutators."""

import random


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
    def invert_chars():
        pass

    @staticmethod
    def add_char():
        pass

    @staticmethod
    def delete_char():
        pass


class NumberMutator(object):
    @staticmethod
    def flip_bit(number):
        pass

    @staticmethod
    def increment_value(number):
        pass

    @staticmethod
    def decrement_value(number):
        pass

    @staticmethod
    def add_value():
        pass

    @staticmethod
    def remove_value():
        pass
