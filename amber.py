import urllib.parse
import logging
import sys

from datetime import datetime
from states import states

from io_handler import config_pull, pull_message_template
from api_handler import InvokeOptions, get_api_response

logging.basicConfig(encoding='utf-8', level=logging.NOTSET)
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

try:
    logging.getLogger().setLevel(logging.getLevelName(config_pull("logging_level").upper()))
except ValueError as e:
    logging.getLogger().setLevel(logging.INFO)
    logging.error("Logging setup failed with %s; defaulting to INFO", e)

program_states = states()

def console_survey() -> int:
    """
    Surveys the user for input. Valid input is an `InvokeOptions` (Enum) member.
    The member's value is returned by the function.

    Args:
        None.
    
    Returns:
        int: An `InvokeOptions` (Enum) member's value.
    """
    print(f"\n{datetime.today().strftime("%b %d, %A")}\n")

    print("Please select the date. Here are your options:")
    for option in InvokeOptions:
        print(f"{option.name} ({option.value})")
    print("---\n-> ", end="")

    try:
        option = int(input())
    except ValueError as e:
        raise SystemExit("Invalid selection.") from e

    return option

group = urllib.parse.quote("GROUP_NAME")

# pylint: disable=E1101
# url_timetable member is added to the states() class dynamically 
# and triggered a pylint false positive.
api_response, return_as_requested = \
    get_api_response(program_states.url_timetable.replace("!group", group), InvokeOptions(console_survey()))

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
            output = output[:-4]

    case dict(): # single day parsing
        if not return_as_requested:
            print("\nThe day specified doesn't have classes. Here's the earliest day that has a timetable instead:")
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

print(output)
