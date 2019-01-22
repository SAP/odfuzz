from sys import stderr, stdout
from abc import ABCMeta, abstractmethod

from odfuzz.statistics import Stats


class OutputHandler(metaclass=ABCMeta):
    def __init__(self, bind):
        self._bind = bind

    @abstractmethod
    def print_status(self, status):
        pass

    @abstractmethod
    def print_test_num(self):
        pass


class StandardOutput(OutputHandler):
    def print_status(self, status):
        stdout.write(status + '\n')

    def print_test_num(self):
        stdout.write('Generated tests: {} | Failed tests: {} | Raised exceptions: {} \r'
                     .format(Stats.tests_num, Stats.fails_num, Stats.exceptions_num))
        stdout.flush()


class BindOutput(OutputHandler):
    def print_status(self, status):
        self._bind.update_state(
            state='PROGRESS',
            meta={
                'tests_num': Stats.tests_num, 'fails_num': Stats.fails_num,
                'exceptions_num': Stats.exceptions_num, 'status': status})
    
    def print_test_num(self):
        self._bind.update_state(
            state='PROGRESS',
            meta={
                'tests_num': Stats.tests_num, 'fails_num': Stats.fails_num,
                'exceptions_num': Stats.exceptions_num, 'status': 'Fuzzing...'})
