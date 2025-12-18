import re
import getpass
from typing import Callable, Any, Iterable

from .exceptions import ValidationError, ConversionError, APIError
from .patterns import INT, ANY
from .validators import is_in_list
from .utils import format_iterable, format_table, try_until_ok


def get_input(prompt: str = "",
              pattern: str | re.Pattern = ANY,
              validator: Callable[[str], bool] = lambda x: True,
              converter: Callable[[str], Any] = str,
              default: Any | None = None,
              *,
              retry: bool = True,
              if_invalid: str = "invalid input!",
              on_keyboard_interrupt: Callable | None = None) -> Any:
    """
    Prompts the user for input and performs validation, with optional retry logic.

    This function is the core of validated input handling, combining single-pass
    validation (when retry=False) and repeated attempts (when retry=True).
    The validation sequence is strict: 1) RegEx Pattern Check, 2) Custom Validator Check,
    3) Conversion.

    :param prompt: The message displayed to the user before input.
    :param pattern: A regex pattern (str or re.Pattern) the input must fully match.
                    Defaults to ANY (r'.*').
    :param validator: A custom function (Callable[[str], bool]) for additional logical checks.
                      It receives the input string before conversion.
    :param converter: A function (Callable[[str], Any]) to convert the validated input string
                      to the desired type (e.g., int, float). Defaults to str.
    :param default: The value to return if the user presses Enter (provides empty input).
                    Can be any type (Any), as this value bypasses validation and conversion.
    :param retry: If False, the function acts as a single-pass validator:
                  it raises exceptions upon failure. If True (default), it loops, prompting
                  the user until valid input is provided.
    :param if_invalid: The error message displayed upon validation/conversion failure (used only if retry=True).
    :param on_keyboard_interrupt: Action to take when user press Ctrl+C
                     - Callable: A function to call
                     - None (default): Prints \n and causes sys.exit(0)

    :returns: The converted input value (Any).

    :raises ValidationError: If the input does not match the 'pattern' or fails
                             the 'validator' check, and retry=False.
    :raises ConversionError: If the 'converter' function raises an exception
                             (e.g., ValueError, TypeError) during type conversion, and retry=False.
    """
    if retry:
        return try_until_ok(
            get_input,
            prompt=prompt,
            pattern=pattern,
            validator=validator,
            converter=converter,
            default=default,
            exceptions=ValidationError,
            retry=False,
            on_exception=if_invalid,
            on_keyboard_interrupt=on_keyboard_interrupt
        )

    input_text = input(prompt)

    if default is not None and input_text == '':
        return default

    if isinstance(pattern, str):
        pattern = re.compile(pattern)

    if pattern.fullmatch(input_text) and validator(input_text):
        try:
            return converter(input_text)
        except Exception as e:
            raise ConversionError(f"conversion failed: {e}") from e
    else:
        raise ValidationError("invalid input format!")


def get_password(
    prompt: str = "Password: ",
    pattern: str | re.Pattern = ANY,
    validator: Callable[[str], bool] = lambda x: True,
    *,
    retry: bool = True,
    if_invalid: str = "Invalid password format!",
    on_keyboard_interrupt: Callable | None = None,
) -> str:
    """
    Prompts the user for sensitive input (password) without echoing characters
    to the console, and applies validation with optional retry logic.

    This function uses getpass.getpass() for secure input handling. It defaults
    to retry=True because password input often requires multiple attempts to
    satisfy complexity requirements.

    :param prompt: The message displayed to the user. Defaults to 'Password: '.
    :param pattern: A regex pattern (str or re.Pattern) the password must fully match.
                    Defaults to ANY (r'.*').
    :param validator: A custom function (Callable[[str], bool]) for additional logical checks.
                      It receives the input string before conversion.
    :param retry: If True (default), loops until a valid password is given, displaying
                  'if_invalid' message. If False, raises exceptions upon failure.
    :param if_invalid: The error message displayed upon validation failure (used only if retry=True).
    :param on_keyboard_interrupt: Action to take when user press Ctrl+C
                     - Callable: A function to call
                     - None (default): Prints \n and causes sys.exit(0)

    :returns: The validated password string.

    :raises ValidationError: If retry=False and validation fails.
    """
    if retry:
        return try_until_ok(
            get_password,
            prompt=prompt,
            pattern=pattern,
            validator=validator,
            exceptions=ValidationError,
            retry=False,
            on_exception=if_invalid,
        )

    password = getpass.getpass(prompt=prompt)

    if isinstance(pattern, str):
        pattern = re.compile(pattern)

    if pattern.fullmatch(password) and validator(password):
        return password
    else:
        raise ValidationError("invalid password format!")


def get_choice(options: list[str],
               prompt: str = "Choose option: ",
               if_invalid: str = "Incorrect option!",
               case_sensitive: bool = False,
               show: bool = False,
               pattern: str = "- {}",
               join_by: str = "\n",
               start: str = "",
               end: str = "",
               ) -> str:
    """
    Prompts the user to input a string and validates that the input exactly
    matches one of the provided options from the list.

    The function uses 'get_input' with retry = True and 'is_in_list' validator.

    :param options: List of acceptable string choices.
    :param prompt: Text displayed to the user before input.
    :param if_invalid: Text displayed to the user if input is incorrect.
    :param case_sensitive: If True, validation is case-sensitive;
                           if False (default), case is ignored during comparison.
    :param show: If True, prints the list of 'options' using 'print_iterable'
                 before prompting the user. Defaults to False (e.g., for 'Y/n' prompts).
    :param pattern: Format string passed to 'print_iterable' for displaying each item
                    (e.g., '- {}'). Used only if 'show' is True.
    :param join_by: Separator placed between formatted elements. Used only if 'show' is True.
    :param start: Prefix string placed at the beginning of the output. Used only if 'show' is True.
    :param end: Suffix string placed at the end of the output. Used only if 'show' is True.
    :raises APIError: If the 'options' list is empty.
    :return: The string that the user successfully entered from the 'options' list.
    """
    if not options:
        raise APIError("options list can't be empty.")

    if show:
        print_iterable(options, item_pattern=pattern, join_by=join_by, start=start, end=end)

    return get_input(prompt=prompt,
                     validator=is_in_list(options, case_sensitive),
                     retry=True,
                     if_invalid=if_invalid)


def menu(options: dict[int, str],
         prompt: str = "Choose option: ",
         if_invalid: str = "Incorrect option!",
         pattern="{}. {}",
         join_by: str = "\n",
         start: str = "",
         end: str = "",
         show_options: bool = True) -> int:
    """
    Print a numbered menu and ask the user to pick an option by its number.

    The **keys** of the dictionary are the exact numbers the user must type.
    The order is preserved (Python 3.7+ dicts are ordered).

    Perfect for the ultra-clean pattern:
        match menu(options):
            case 1: ...
            case 0: break

    Parameters
    ----------
    options : dict[int, str]
        Menu items. Keys = numbers the user types, values = displayed text.
        Common pattern: 1, 2, 3, 0 for "Exit".
    prompt : str, default "Choose option: "
        Text shown before input.
    if_invalid : str, default "Incorrect option!"
        Message shown on invalid input.
    pattern : str, default "{}. {}"
        Row format string for ``print_table``. First placeholder = number, second = text.
    join_by, start, end : str
        Formatting options passed directly to ``print_table``.
    show_options : bool, default True
        If True, the function prints the numbered menu options to the console
        before asking for input. Set to **False** if you want to display the
        options using custom formatting logic.

    Returns
    -------
    int
        The number (key) that user entered.

    Example
    -------
    >>> options = {1: "Play", 2: "Rating", 0: "Exit"}
    >>> while True:
    ...     match menu(options, pattern="{}. {}"):
    ...         case 1: play()
    ...         case 2: show_rating()
    ...         case 0: break
    """
    if show_options:
        print_table(options.items(), pattern, join_by=join_by, start=start, end=end)
    return get_input(prompt=prompt,
                     pattern=INT,
                     validator=is_in_list([str(key) for key in options.keys()], case_sensitive=False),
                     converter=lambda t: int(t),
                     retry=True,
                     if_invalid=if_invalid,)


def yes_no(prompt: str = 'Confirm [y/n]: ',
           yes: list = None,
           no: list = None,
           if_invalid: str = 'Incorrect option!',
           ) -> bool:
    """
        Prompts the user for a yes/no confirmation with input validation.

        Parameters
        ----------
        prompt : str
            The prompt text displayed to the user.
            'Confirm [y/n]: ' by default.
        yes : list[str]
            A list of allowed strings for a 'Yes' response.
            ['y', 'yes'] by default.
        no : list[str]
            A list of allowed strings for a 'No' response.
            ['n', 'no'] by default.
        if_invalid : str
            The message displayed when invalid input is entered.
            ['Incorrect option!'] by default.

        Returns
        -------
        bool
            True if the user entered an option from 'yes'; False if from 'no'.
        """
    if no is None:
        no = ['n', 'no']
    else:
        no = [string.lower() for string in no]
    if yes is None:
        yes = ['y', 'yes']
    else:
        yes = [string.lower() for string in yes]
    inp = get_input(prompt,
                    validator=is_in_list(yes + no,
                                         case_sensitive=False),
                    retry=True,
                    if_invalid=if_invalid).lower()

    return inp in yes


def print_iterable(iterable: Iterable[Any],
                   item_pattern: str = "{}",
                   join_by: str = "\n",
                   start: str = "",
                   end: str = ""
                   ) -> None:
    """
    Conveniently prints all elements of a one-dimensional iterable, formatted
    using the logic of format_iterable().

    :param iterable: The iterable whose elements are to be formatted and printed.
    :param item_pattern: The format string used for each individual item (e.g., 'Item: {}').
    :param join_by: The separator placed between the formatted elements.
    :param start: A prefix string placed at the beginning of the output.
    :param end: A suffix string placed at the end of the output.
    :return: None. The result is printed directly to stdout.
    """
    print(format_iterable(iterable, item_pattern, join_by, start, end))


def print_table(iterable: Iterable[Iterable[Any]],
                row_pattern: str = "{}: {}",
                join_by: str = "\n",
                start: str = "",
                end: str = "",
                ) -> None:
    """
    Conveniently prints elements of an iterable containing unpackable items (e.g., pairs, tuples),
    formatted using the logic of format_table().

    This is useful for tables and items produced by enumerate(), zip(), dict.items(), etc.

    :param iterable: The iterable containing elements that can be unpacked (e.g., [(1, 'a'), (2, 'b')]).
                     Each inner element is unpacked using Python's *item syntax.
    :param row_pattern: The format string used for each inner unpackable element.
                         The number of elements in each inner item MUST match the number of placeholders
                         in 'item_pattern' (e.g., '{}: {}' requires two elements).
    :param join_by: The separator placed between the formatted elements.
    :param start: A prefix string placed at the beginning of the output.
    :param end: A suffix string placed at the end of the output.
    :return: None. The result is printed directly to stdout.
    """
    print(format_table(iterable, row_pattern, join_by, start, end))


def print_header(header: str,
                 char: str = "~",
                 *,
                 width: int | None = None,
                 space: int = 0
                 ) -> None:
    """
    Prints a nice centered header with decorative lines.

    :param header: Text to display
    :param char: Symbol for the lines (default: '~')
    :param width: Force specific line width. If None — uses length of header.
    :param space: Number of spaces added on both sides of the header (default: 0)
    """
    header = " " * space + header + " " * space
    line = char * (width or len(header))
    print(f"{line}\n{header}\n{line}")
