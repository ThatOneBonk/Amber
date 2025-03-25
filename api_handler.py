from urllib.request import urlopen
from enum import Enum
from datetime import *
import hashlib
import logging
import json
import ssl

from io_handler import *
from states import states

ssl._create_default_https_context = ssl._create_stdlib_context # SSL init

program_states = states()

class InvokeOptions(Enum):
    TODAY = 1
    TOMORROW = 2
    THISWEEK = 3
    NEXTWEEK = 4

def get_api_response(url: str, InvokeOptions) -> [list, bool]:
    """
    Fetch an API response from the given URL using the given invoke option.
    If a single day was requested but the day doesn't have a timetable associated with it, the nearest available timetable is returned and the return boolean is set to False.

    Args:
        url (str): The API URL.
        InvokeOptions (enum): The date or range for which the timetable should be pulled.

    Returns:
        list: The API response (None if a singular day was requested, but it is a day off).
        bool: Whether or not the returnd list belongs to the requested day:
            - True: The return list contains the timetable for the specified day;
            - False: The return list contains the nearest proper timetable instead;
            - None: When a day range has been requested and such logic cannot be applied.
    """

    do_single_day = False

    match InvokeOptions.name:
        case "TODAY":
            # FIXME THIS DOES NOT SET THE TIMEZONE BE CAREFUL FOR THE LOVE OF GOD
            timestamp = int(datetime.now(timezone.utc).replace(hour = 0, minute = 0, second = 0, microsecond = 0).strftime('%s'))
            do_single_day = True
        case "TOMORROW":
            timestamp = int(datetime.now(timezone.utc).replace(hour = 0, minute = 0, second = 0, microsecond = 0).strftime('%s')) + 86400
            do_single_day = True
        case "THISWEEK":
            # oh my god what a f###ing abomination
            timestamp = int((datetime.now(timezone.utc).replace(hour = 0, minute = 0, second = 0, microsecond = 0) - timedelta(days = datetime.now().weekday())).strftime('%s'))
        case "NEXTWEEK":
            # it uh, it does work, i can't complain
            timestamp = int((datetime.now(timezone.utc).replace(hour = 0, minute = 0, second = 0, microsecond = 0) - timedelta(days = datetime.now().weekday())).strftime('%s')) + 604800

    json_file = json.load(urlopen(f"{url.replace("!timestamp", str(timestamp))}"))

    if do_single_day:
        if not json_file:
            return None, False
        # check if result belongs to the timestamp (and account for possible timezone shenanigans when doing this check, too)
        if abs(int(datetime.strptime(json_file[0]["date"], "%Y-%m-%d").timestamp()) - timestamp) <= 43200:
            return json_file[0], True
        else:
            return json_file[0], False
    
    return json_file, None

def get_groups(url: str):
    print(url)
    groups = json.load(urlopen(url))
    output = []
    for group in groups["results"]:
        output.append(group["text"])
    return output