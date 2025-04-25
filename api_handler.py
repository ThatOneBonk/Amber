from datetime import datetime, timezone, timedelta
from urllib.request import urlopen
from urllib.error import URLError
from typing import Optional
from enum import Enum
import logging
import json
import ssl

from certifi import where
from states import States

program_states = States()

class InvokeOptions(Enum):
    """
    Arbitrary invoke options that the get_api_response() function expects.
    """
    TODAY = 1
    TOMORROW = 2
    THIS_WEEK = 3
    NEXT_WEEK = 4

def get_api_response(url: str, invoke_options: InvokeOptions, cert: str = None) -> [Optional[list], Optional[bool]]:
    """
    Fetch an API response from the given URL using the given invoke option.
    If a single day was requested but the day doesn't have a timetable associated with it, the nearest available timetable is returned and the return boolean is set to False.

    Args:
        url (str): The API URL.
        invoke_options (InvokeOptions): The date or range for which the timetable should be pulled.
        cert (Optional[str]): Path to a certificate that needs to be used during the SSL context setup.

    Returns:
        Optional[list]: The API response (None if a singular day was requested, but the API didn't return anything).
        Optional[bool]: Whether or not the returnd list belongs to the requested day:
            - True: The return list contains the timetable for the specified day;
            - False: The return list contains the nearest proper timetable instead;
            - None: A day range has been requested and this logic is not applicable.
    """

    do_single_day = False

    match invoke_options.name:
        case "TODAY":
            # FIXME THIS DOES NOT SET THE TIMEZONE BE CAREFUL FOR THE LOVE OF GOD
            timestamp = int(datetime.now(timezone.utc).replace(hour = 0, minute = 0, second = 0, microsecond = 0).strftime('%s'))
            do_single_day = True
        case "TOMORROW":
            timestamp = int(datetime.now(timezone.utc).replace(hour = 0, minute = 0, second = 0, microsecond = 0).strftime('%s')) + 86400
            do_single_day = True
        case "THIS_WEEK":
            # oh my god what a f###ing abomination
            timestamp = int((datetime.now(timezone.utc).replace(hour = 0, minute = 0, second = 0, microsecond = 0) - timedelta(days = datetime.now().weekday())).strftime('%s'))
        case "NEXT_WEEK":
            # it uh, it does work, i can't complain
            timestamp = int((datetime.now(timezone.utc).replace(hour = 0, minute = 0, second = 0, microsecond = 0) - timedelta(days = datetime.now().weekday())).strftime('%s')) + 604800
        case _:
            logging.error("[get_api_response] Unknown InvokeOptions member!")

    if cert:
        ssl_context = ssl.create_default_context(cafile=cert)
        logging.debug("[get_api_response] Certificate path is %s", cert)
    else:
        ssl_context = ssl.create_default_context(cafile=where())

    try:
        json_file = json.load(urlopen(f"{url.replace("!timestamp", str(timestamp))}", context=ssl_context))
    except URLError as exc:
        raise SystemExit("[get_api_response] Failed to open the URL, are the certificated alright? (Pass `--certificate`)") from exc

    if do_single_day:
        if not json_file:
            return None, False
        # check if result belongs to the timestamp (and account for possible timezone shenanigans when doing this check, too)
        if abs(int(datetime.strptime(json_file[0]["date"], "%Y-%m-%d").timestamp()) - timestamp) <= 43200:
            return json_file[0], True
        else:
            return json_file[0], False
    
    return json_file, None