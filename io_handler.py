import json
import os.path
import logging
import re

def strtobool (val: str) -> bool:
    """
    Convert a string representation of truth to true (1) or false (0).

    Args:
        val (str): Function input.
            - True values are 'y', 'yes', 't', 'true', 'on', and '1'.
            - False values are 'n', 'no', 'f', 'false', 'off', and '0'.
    
    Returns:
        bool: Function output.
    """
    val = val.lower()
    if val in ('y', 'yes', 't', 'true', 'on', '1'):
        return True
    elif val in ('n', 'no', 'f', 'false', 'off', '0'):
        return False
    else:
        raise ValueError(f"invalid truth value {val}")

def config_create():
    """
    Creates a brand new config file in case the old one doesn't exist or isn't satisfactory.

    Args:
        None.
    
    Returns:
        None.
    """
    config_initial = {
        "url_timetable": "",
        "logging_level": ""
    }
    with open(f"{script_dir}/file/config.json", "w", encoding="utf-8") as config_json_file:
        json.dump(config_initial, config_json_file, ensure_ascii=False, indent=4)
    raise SystemExit("[config_create] Brand new config had to be made. Please fill it in.")

def config_pull(element_name: str) -> str | bool:
    """
    Returns a single config element, matched by its exact name.

    Args:
        element_name (str): The element name (key) the value of which will be returned.

    Returns:
        str/bool: Value by the passed key.
    """
    try:
        with open(f"{script_dir}/file/config.json", "r", encoding="utf8") as config_json_file:
            config_file = json.load(config_json_file)
            config_element = config_file[element_name]
            try:
                return bool(strtobool(config_element))
            except ValueError:
                return config_element
    except FileNotFoundError:
        config_create()
    except json.JSONDecodeError:
        logging.error("[config_pull] No such variable in config or unable to parse JSON")
        return "null"

def token_pull():
    """
    Returns the API key stored in a dedicated .txt file.

    Args:
        None.

    Returns:
        The API key.
    """
    try:
        with open(f"{script_dir}/file/credentials.txt", "r", encoding="utf8") as token_file:
            return(token_file.read())
    except FileNotFoundError:
        logging.critical("[token_pull] Credentials file not found!")
        raise

def pull_message_template():
    """
    This function is used by the API handler module to get the desired template and the set of keys.

    Args:
        None.
    
    Returns:
        str: The template loaded from ./timetable_template.md
        list: Keys (API JSON keys) that are to be replaced downstream with the respective data.
            - The !date key requires special treatment so it is always removed from the key list.
    """
    try:
        with open(f"{script_dir}/file/timetable_template.md", "r", encoding="utf8") as template_file:
            template_text = template_file.read()
    except (FileNotFoundError, IOError):
        logging.warning("[pull_message_template] Template missing or invalid.")
        return("Missing template")

    matches = re.findall(r"!\w+", template_text)

    if "!date" in matches: matches.remove('!date')

    return template_text, matches

script_dir = os.path.dirname(os.path.abspath(__file__))
