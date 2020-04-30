from odfuzz.utils import encode_string, decode_string


def test_double_encoding():
    assert encode_string('2e+2d') == '2e%2B2d'
    assert encode_string('0e+2d') == '0e%2B2d'

    assert encode_string('2.286428418907951e+39d') == '2.286428418907951e%2B39d'

def test_double_decoding():
    assert decode_string('2e%2B2d') == '2e+2d'
    assert decode_string('0e%2B2d') == '0e+2d'

    assert decode_string('2.286428418907951e%2B39d') == '2.286428418907951e+39d'


def test_string_encoding():
    assert encode_string('') == ''
    assert encode_string('\'\'') == r'%27%27%27%27'
    assert encode_string('\'') == r'%27%27'

    assert encode_string('asd++asd') == r'asd%2B%2Basd'
    assert encode_string('asd\'asd\'\'') == r'asd%27%27asd%27%27%27%27'
    assert encode_string('asd&asd') == r'asd%26asd'

    assert encode_string('!//') == r'%21%2F%2F'
    assert encode_string('¬³hÒ\x90Ú') == r'%C2%AC%C2%B3h%C3%92%C2%90%C3%9A'


def test_string_decoding():
    assert decode_string('') == ''
    assert decode_string(r'%27%27%27%27') == '\'\''
    assert decode_string(r'%27%27') == '\''

    assert decode_string(r'asd%2B%2Basd') == 'asd++asd'
    assert decode_string(r'asd%27%27asd%27%27%27%27') == 'asd\'asd\'\''
    assert decode_string(r'asd%26asd') == 'asd&asd'

    assert decode_string(r'%21%2F%2F') == '!//'
    assert decode_string(r'%C2%AC%C2%B3h%C3%92%C2%90%C3%9A') == '¬³hÒ\x90Ú'
