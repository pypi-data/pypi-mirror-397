'''Utilities for handling text formatting.'''

from .text_format import TextFormat


class FormattedText:
    """
    Represents text with optional formatting options applied.

    :param text: The text content to be formatted.
    :param options: Optional formatting options to be applied to the text.
    """
    
    def __init__(self, text: str, *options: bytes):
        self.text = text
        self.options = options

    def get_format(self) -> str:
        """
        Constructs the formatting string based on the provided options.

        :returns: A string representing the combined formatting options.
        """

        result = ''

        for option in self.options:
            if option is not None:
                result += option.decode()

        return result

    @staticmethod
    def reset_format() -> str:
        """
        Provides the reset formatting string to clear any applied styles.

        :returns: A string representing the reset formatting option.
        """

        return TextFormat.RESET.decode()

    def __str__(self) -> str:
        if len(self.options) == 0:
            return self.text

        result = ''
        result += self.get_format()
        result += self.text
        result += self.reset_format()

        return result

    def __repr__(self) -> str:
        return self.__str__()
    