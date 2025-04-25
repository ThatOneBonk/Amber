# Amber
(Not the Pyro archer)
## What is Amber?
Amber is a Python utility that fetches and formats a timetable from a REST API into a clean, readable message. This bypasses the need to go to a site or other middlemen that could be slow or, frankly, poorly implemented.\
Amber was designed with a specific REST API in mind (specifying which would be a privacy breach).\
The project started as a Telegram bot, but the current implementation of Amber doesn't communicate with Telegram yet. It's also great as a CLI utility, as it turns out.\
## Configuration
A default configuration file is created in the `file/` directory if it is not already present.
- `url_timetable` is the URL of the REST API that Amber will use.
  - `!group` will be replaced with the group name picked;
  - `!timestamp` will be replaced with a UNIX timestamp:
    - In Headless mode, `!timestamp` is generated based on the date selected in the TUI. The time is 12AM (GMT+3), for the specified day or the specified week's Monday depending on user input.
- `logging_level` sets the logging level. It is overridden if the `--logging_level` CLI argument is passed.
Additionally, a `file/timetable_template.md` file is required. This file defines how a single class' entry in a timetable looks like. `!tags` will be replaced with relevant information at runtime: the tag's name is taken and Amber looks for a corresponding key in the API's response JSON.
## How to run
First off,
```bash
git clone https://github.com/ThatOneBonk/Amber.git; cd Amber
```
You can then run:
```bash
python amber.py
```
Amber takes CLI arguments:
- `--mode` or `-m` specifies the mode to run Amber in - Headless (as a CLI utility) or Faceless (as a Telegram bot). Defaults to Headless;
- `--logging_level` or `-l` specifies the logging level to run Amber with, overriding the value set in the configuration file;
- `--certificate` or `-c` specifies the path to a `.pem` certificate file to be used during SSL context setup. Due to a specific REST API's invalid certificates, this is an option...
- `--group` or `-g` specifies your group. If not passed, you will be asked by the TUI.
