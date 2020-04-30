import urllib


def encode_string(value):
    """Replace and encode all special characters in the passed string.

    Single quotation marks need to be doubled. Therefore, if the string contains a single
    quotation mark, it is going to be replaced by a pair of such quotation marks.
    """
    value = value.replace('\'', '\'\'')
    return urllib.parse.quote(value, safe='')


def decode_string(value):
    """Decode the passed value back to its original state.

    This function is the reverse of `encode_string()`.
    """
    decoded_value = urllib.parse.unquote(value)
    return decoded_value.replace('\'\'', '\'')
