import re
import os


def request_regex_pattern(input_message):
    """Requests a regular expression from user and creates an SRE_Pattern
    object that ignores case sensitivity.

    Repeats request if input is not valid. Does not repeat if nothing is entered.

    Parameters:
        input_message (string): A terminal message to display before entry request.
    Returns:
        regex_pattern (SRE_Pattern): The regular expression input by the user.
    """
    regex_pattern = None
    while True:
        regex = input(input_message)

        if not regex:
            print("No Regex provided.")
            break

        try:
            regex_pattern = re.compile(regex, re.IGNORECASE)
            break
        except re.error:
            print("The input was not valid regular expression")
            continue

    return regex_pattern


def request_list_of_int(input_message, min_value=None, max_value=None):
    """Requests a space separated list of integers from the user
    Repeats request if input is not valid, specifying what part of the
    previous input was incorrect. Does not repeat if nothing is entered."""
    while True:
        int_list = input(input_message).split()
        if not int_list:
            print("No list of numbers provided.")
            break

        non_int_input = [i for i in int_list if not __represents_int(i)]
        if non_int_input:
            list_string = _list_to_string(non_int_input)
            print(f"!WARNING! The following entries are not integers :\n{list_string}")
            continue

        int_list = [int(i) for i in int_list]
        if min_value is not None:
            below_min_int = [i for i in int_list if i < min_value]
            if below_min_int:
                list_string = _list_to_string(below_min_int)
                print(f"!WARNING! The following entries are below the allowed minimum of {min_value}:\n{list_string}")
                continue

        if max_value is not None:
            above_max_int = [i for i in int_list if i > max_value]
            if above_max_int:
                list_string = _list_to_string(above_max_int)
                print(f"!WARNING! The following entries are above the allowed maximum of {max_value} :\n{list_string}")
                continue

        break
    return int_list


def request_items_of_list(input_message, target_list):
    """Requests a list of space separated item from a given list from the user.

    Repeats request if any entry given by the user does not occur in target_list.
    Does not repeat if input is empty.

    Parameters:
        input_message (string): A terminal message showing what input is needed.
        target_list (list): List of strings. Any input item must occur in this
                                    list or target_list2.
    """
    while True:
        item_list = input(input_message).split()
        if not item_list:
            print("No item provided.")
            break

        non_item_input = [item for item in item_list if item not in target_list]
        if non_item_input:
            list_str = _list_to_string(non_item_input)
            print(f"!WARNING! The following entries are not in the list of possible items:\n{list_str}")
            continue

        break
    return item_list


def __represents_int(input_string):
    """Tests whether a given string represents a number or not."""
    try:
        int(input_string)
        return True
    except ValueError:
        return False


def _list_to_string(input_list):
    """Turns a list into a string that is more human readable."""
    return str(input_list).translate(str.maketrans({'[': '', ']': '', '\'': '', '\"': '', ',': ' '}))


def request_filepath(input_message):
    """Requests a filepath from the user.
    Repeats request if user input is not a valid filepath. Does not loop
    if input is empty, '', 'q', 'exit', 'stop' or 'esc'.
    Parameters:
        input_message (string): A terminal message showing what input is needed.
    Returns:
        string: A valid path to an SFDB file.
        None: When user does not provide a filepath.
    """
    while True:
        file_path = input(input_message)

        user_forces_exit = file_path.lower() in ['', 'q', 'exit', 'stop', 'esc']
        if user_forces_exit:
            print("No path provided. Exiting file-reading process...")
            break

        elif not os.path.isfile(file_path):
            print(f"{file_path} is not a valid filepath.")
            continue

        break
    return file_path
