from api_handler import InvokeOptions, get_api_response, get_groups
from datetime import datetime, timedelta
from states import states
from io_handler import *
import urllib.parse
import logging
import sys

logging.basicConfig(encoding='utf-8', level=logging.NOTSET)
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

try:
    logging.getLogger().setLevel(logging.getLevelName(config_pull("logging_level").upper()))
except Exception as e:
    logging.getLogger().setLevel(logging.INFO)
    logging.error(f"Logging setup failed with {e}; defaulting to INFO")

program_states = states()

def console_survey():
    # print(f"Please enter your year.\n-> ", end="")
    # try:
    #     year = int(input())
    # except ValueError:
    #     raise SystemExit("Invalid selection.")
    # print(f"Please select your group. Type it in Cyrillic.\n-> ", end="")
    # group = input()
    # if group.strip() not in get_groups(program_states.url_groups.replace("!course", str(year))):
    #     print("This group isn't available. Did you spell it right?")
    #     exit()

    print(f"Please select the date. Here are your options:")
    for option in InvokeOptions:
        print(f"{option.name} ({option.value})")
    print("---\n-> ", end="")

    try:
        option = int(input())
    except ValueError:
        raise SystemExit("Invalid selection.")

    return option

group = urllib.parse.quote("GROUP_NAME")

api_response, return_as_requested = get_api_response(program_states.url_timetable.replace("!group", group), InvokeOptions(console_survey()))

day_template, key_list = pull_message_template()
output = ""

# TODO fix timezones
# TODO get current time and compare to start/end times, displaying the gap
# TODO store parsed stuff as cache and remove cache older than a few hours old

match api_response:
    case list(): # whole week parsing
        for day in api_response:
            # -- working space with day as day --
            output += f"\n===--  {day["date"]} --===\n"
            for lesson in day["list"]:
                unit = day_template
                for key in key_list:
                    unit = unit.replace(key, lesson[key[1:]])
                output += f"{unit}\n---\n"
            output = output[:-4]

    case dict(): # single day parsing
        if not return_as_requested:
            print("The day specified doesn't have classes. Here's the earliest day that has a timetable instead:", end="")
        # -- working space with api_response as day --
        output += f"\n===--  {api_response["date"]} --===\n"
        for lesson in api_response["list"]:
            unit = day_template
            for key in key_list:
                unit = unit.replace(key, lesson[key[1:]])
            output += f"{unit}\n---\n"
        output = output[:-4]

if not output:
    output = "[Nothing here...]"

print(output)
