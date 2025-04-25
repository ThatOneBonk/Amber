import re
import sys
import logging
import argparse
import urllib.parse
from typing import Optional
from datetime import datetime

from states import States

from api_handler import InvokeOptions, get_api_response
from io_handler import config_pull, pull_message_template

logging.basicConfig(encoding='utf-8', level=logging.NOTSET)
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

program_states = States()

def console_survey() -> tuple[int, str, Optional[str]]:
    """
    Surveys the user for input. 
    Captures the `--group` argument if passed, queries the user if not.
    Members of `InvokeOptions` (Enum) is considered valid user input.

    Args:
        None.
    
    Returns:
        int: An `InvokeOptions` (Enum) member's value.
        str: The group name which should be put into the API URL.
        Optional[str]: Path to a certificate that needs to be used during the SSL context setup.
    """
    parser = argparse.ArgumentParser(description="Timetable API wrapper")

    parser.add_argument("-m", "--mode", required=False, 
    choices=["headless", "faceless"],
    default="headless",
    help="run either headless (in TTY) or faceless (as Telegram bot)")

    parser.add_argument("-l", "--logging_level", required=False,
    choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
    help="debugging level that needs to be set; defaults to the value in `config`")

    parser.add_argument("-c", "--certificate", required=False,
    metavar="PATH_TO_CERT",
    help="path to a .pem certificate file if the endpoint requires a special one")

    parser.add_argument("-g", "--group", 
    required=False,
    help="your group (in Cyrillic, \"ЛОК-512\")")

    args = parser.parse_args()

    if not args.logging_level:
        logging_level = config_pull("logging_level")
    else:
        logging_level = args.logging_level

    try:
        logging.getLogger().setLevel(logging.getLevelName(logging_level.upper()))
    except ValueError as e:
        logging.getLogger().setLevel(logging.INFO)
        logging.error("Logging setup failed with %s; defaulting to INFO", e)

    match args.mode:
        case "faceless":
            faceless(args)
        case "headless":
            headless(args)

def faceless(args: argparse.Namespace):
    """
    Run in faceless (Telegram bot) mode.

    Args:
        args (argparse.Namespace): Arguments harvested by console_survey().

    Returns:
        None.
    """
    # FIXME implement
    print("Not implemented :(")

def headless(args: argparse.Namespace):
    """
    Run in headless (TTY) mode.

    Args:
        args (argparse.Namespace): Arguments harvested by console_survey().

    Returns:
        None.
    """
    # FIXME there's absolutely a library to make a pretty TUI
    group = args.group
    cert = args.certificate

    print(f"\n{datetime.today().strftime("%b %d, %A")}\n")

    if not group:
        print("Please enter your group.\n---\n-> ", end="")
        group = str(input())
        print("")

    pattern = r"[А-Я]+-[0-9]+"
    if not re.search(pattern, group):
        logging.warning("[console_survey] The entered group %s does not abide the expected group name format.", group[:10])
    else:
        group = urllib.parse.quote(group)

    print("Please select the date. Here are your options:")
    for option in InvokeOptions:
        print(f"{option.name} ({option.value})")
    print("---\n-> ", end="")

    try:
        option = int(input())
    except ValueError as e:
        raise SystemExit("Invalid selection.") from e

    print("\nGive me a moment...")

    # pylint: disable=E1101
    # url_timetable member is added to the states() class dynamically
    # and triggers a pylint false positive.
    api_response, return_as_requested = \
        get_api_response(program_states.url_timetable.replace("!group", group), \
        InvokeOptions(option), \
        cert)

    day_template, key_list = pull_message_template()
    output = ""

    # TODO fix timezones
    # TODO get current time and compare to start/end times, displaying the gap
    # TODO store parsed stuff as cache and remove cache older than a few hours old
    # TODO add single day options to whole week choices (get specific day)

    match api_response:
        case list(): # whole week parsing
            for day in api_response:
                # -- working space with day as day --
                human_date = datetime.strptime(day["date"], "%Y-%m-%d").strftime("%b %d, %A")
                output += f"\n===--  {human_date} --===\n"
                for lesson in day["list"]:
                    unit = day_template
                    for key in key_list:
                        unit = unit.replace(key, lesson[key[1:]])
                    output += f"{unit}\n---\n"
                output = output[:-4] + "\n\n"

        case dict(): # single day parsing
            if not return_as_requested:
                output += "\nThe day specified doesn't have classes. Here's the earliest day that has a timetable instead:\n"
            # -- working space with api_response as day --
            human_date = datetime.strptime(api_response["date"], "%Y-%m-%d").strftime("%b %d, %A")
            output += f"\n===--  {human_date} --===\n"
            for lesson in api_response["list"]:
                unit = day_template
                for key in key_list:
                    unit = unit.replace(key, lesson[key[1:]])
                output += f"{unit}\n---\n"
            output = output[:-4]

    if not output:
        output = "[Nothing here...]"

    print("\n" + output.strip())

if __name__ == "__main__":
    console_survey()
