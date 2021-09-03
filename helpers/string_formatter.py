
class StringFormatter(object):
    """
    Formatter for string types
    """

    @staticmethod
    def convert_underscore_to_slash(string):
        return string.replace("_", "/")
