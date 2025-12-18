#!/usr/bin/python3

"""
This program displays a list of recent earthquakes.
Parses GeoJSON API Endpoint from https://earthquake.usgs.gov
and displays the result as optional color coded list in the terminal.
Color requires a terminal that supports 256 colors.

The PAGER status colors are taken from https://earthquake.usgs.gov/data/pager/background.php
The suggested levels of response are:
no response needed -> green,
local/regional     -> yellow,
national           -> orange,
international      -> red
"""

import argparse
from dataclasses import dataclass
import errno
import os
import shlex
import subprocess
import sys
import time
from datetime import datetime, timezone
import requests
from tabulate import tabulate

# small performance optimization
tabulate.WIDE_CHARS_MODE = False

# constants
VERSION = "1.0.1"
DESCRIPTION = """
Monitor recent earthquakes reported by USGS at https://earthquake.usgs.gov.
If no arguments are specified, the significant earthquakes for the day (--day)
is output by default.

USGS has developed PAGER: an automated system for rapidly estimating impact,
exposure, fatalities, and losses. Color-coded alerting determines the
suggested levels of response: no response needed (green), local/regional (yellow),
national (orange), or international (red).

+-------------------------+----------------------+---------------------------+
| Alert Level and Color   | Estimated Fatalities | Estimated Losses (USD)    |
+-------------------------+----------------------+---------------------------+
| Red                     | 1,000+               | $1 billion+               |
| Orange                  | 100 - 999            | $100 million - $1 billion |
| Yellow                  | 1 - 99               | $1 million - $100 million |
| Green                   | 0                    | < $1 million              |
+-------------------------+----------------------+---------------------------+
"""
QUAKECOLORS = {
    # pager
    "green": "\033[38;5;046m",
    "orange": "\033[38;5;208m",
    "red": "\033[38;5;009m",
    "reset": "\033[0m",
    "yellow": "\033[38;5;011m",
    # magnitude
    "mag8": "\033[38;5;201m",
    "mag7": "\033[38;5;001m",
    "mag6": "\033[38;5;196m",
    "mag5": "\033[38;5;202m",
    "mag4": "\033[38;5;226m",
    "mag3": "\033[38;5;216m",
    "mag2": "\033[38;5;033m",
    "mag1": "\033[38;5;006m",
}
PAGERS = ("red", "orange", "yellow", "green")
UNITS = ("hour", "day", "week", "month")
MAGS = (45, 25, 10)
DEFAULT_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"


# classes
@dataclass
# this is a basic script, we can tolerate a few too many attributes
# pylint: disable=too-many-instance-attributes
class QwState:
    """use class to store global states"""

    alarm: list
    pageralerts: list
    progname: str
    alerted: bool = False
    acceptwarn: bool = False
    enablecolor: bool = True
    geolink: bool = False
    magalert: float = 666.666
    localtime: bool = True
    refresh: int = 300
    runonce: bool = False
    timeout: int = 10
    timeformat: str = DEFAULT_TIME_FORMAT


# functions
def confirmation_prompt(prompt):
    """confirm yes/no prompt"""
    try:
        response = input(f"{prompt} (y/n): ").lower().strip()
    except KeyboardInterrupt:
        print()
        return False
    return response in ["y", "yes"]


def convert_magnitude(magnitude, magstr):
    """convert magnitude into desired printable strings"""
    if magnitude >= 8.5:
        result = f'{get_color("mag8")}{magstr}{get_color("reset")}'
    elif magnitude >= 7.5:
        result = f'{get_color("mag7")}{magstr}{get_color("reset")}'
    elif magnitude >= 6.5:
        result = f'{get_color("mag6")}{magstr}{get_color("reset")}'
    elif magnitude >= 5.5:
        result = f'{get_color("mag5")}{magstr}{get_color("reset")}'
    elif magnitude >= 4.5:
        result = f'{get_color("mag4")}{magstr}{get_color("reset")}'
    elif magnitude >= 3.5:
        result = f'{get_color("mag3")}{magstr}{get_color("reset")}'
    elif magnitude >= 2.5:
        result = f'{get_color("mag2")}{magstr}{get_color("reset")}'
    elif magnitude >= 1.5:
        result = f'{get_color("mag1")}{magstr}{get_color("reset")}'
    else:
        result = magstr
    return result


def convert_seconds_to_hr(seconds):
    """convert seconds to human readable output"""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    parts = []
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if secs > 0 or len(parts) == 0:
        parts.append(f"{secs}s")

    return " ".join(parts)


def get_color(color):
    """conditionally returns an earthquake color"""
    if QwState.enablecolor:
        return QUAKECOLORS[color]
    return ""


def get_earthquake(feature):
    """returns a list of properties for one earthquake"""
    properties = feature["properties"]
    geometry = feature["geometry"]

    # time is given in milliseconds since epoch
    utctime = datetime.fromtimestamp(properties["time"] / 1000, timezone.utc)
    localtime = utctime.astimezone()
    timestamp = localtime if QwState.localtime else utctime

    # colorize magnitude
    magnitude = properties["mag"]
    magstr = f"{magnitude:0.2f}"

    # send alarm based on magnitude
    if magnitude >= QwState.magalert and QwState.alerted is False:
        if len(QwState.alarm) >= 1:
            run_custom_alarm()
        else:
            print("\a", end="")
        QwState.alerted = True  # page only once per refresh

    magnitudestr = convert_magnitude(magnitude, magstr)

    # alert property is the PAGER status
    alertprop = properties["alert"]
    if isinstance(alertprop, str) and alertprop.lower() in PAGERS:
        alert = f'{get_color(alertprop)}{alertprop.upper()}{get_color("reset")}'
        if (
            alertprop.lower() in QwState.pageralerts
            and QwState.alerted is False
        ):
            if len(QwState.alarm) >= 1:
                run_custom_alarm()
            else:
                print("\a", end="")
            QwState.alerted = True
    else:
        alert = "-"

    results = [
        timestamp.strftime(QwState.timeformat),
        magnitudestr,
        properties["place"],
        alert,
        properties["url"],
    ]

    if QwState.geolink:
        coordinates = geometry["coordinates"]
        results.append(
            f"geo:{coordinates[1]},{coordinates[0]},{coordinates[2]}"
        )

    return results


def get_sites():
    # available API endpoints
    """generate site URLs"""
    # URLs
    url = {}
    for unit in UNITS:
        for mag in MAGS:
            url[f"{unit}{mag}"] = (
                f"https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/{mag/10}_{unit}.geojson"
            )
        url[f"all_{unit}"] = (
            f"https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_{unit}.geojson"
        )
        url[f"significant_{unit}"] = (
            f"https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/significant_{unit}.geojson"
        )
    return url


def init_args(parser):
    """initialize arguments"""
    parser.add_argument(
        "-a",
        "--alarm",
        help='set a custom alarm command, this disables\
            the terminal bell alarm, for example using the sox utility: "play -q\
            ~/Audio/quake-alarm.wav"',
        type=str,
    )
    parser.add_argument(
        "-p",
        "--pager",
        help=f"enable audible alarm (defaults to terminal bell)\
            for desired pager, valid pagers are {PAGERS}",
        type=str,
        nargs="+",
    )
    parser.add_argument(
        "-m",
        "--magnitude",
        help="enable audible alarm (defaults to terminal bell)\
            for specified magnitude threshold, value >= mag will trigger the alarm",
        type=float,
    )
    parser.add_argument(
        "-f",
        "--follow",
        help="enable follow mode like tail, (default: False)",
        action="store_true",
    )
    parser.add_argument(
        "-g",
        "--geo-link",
        help="enable geo:// link column, (default: False)",
        action="store_true",
    )
    parser.add_argument(
        "-l",
        "--localtime",
        help=f"display timestamps in local timezone, (default:\
            {QwState.localtime})",
        action="store_true",
    )
    parser.add_argument(
        "-r",
        "--refresh",
        help='set the API request refresh rate in optional time\
            unit, omitted unit presumes "s" (seconds); minimum 60s, maximum 24h (default:\
            5m)',
        type=str,
    )
    parser.add_argument(
        "-ro",
        "--run-once",
        help="disable watch and run a single loop (default:\
            False)",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "-t",
        "--timeout",
        help=f"set the API request timeout value in seconds,\
            minimum 10 (default: {QwState.timeout})",
        type=int,
        nargs=1,
    )
    parser.add_argument(
        "--time-format",
        help=f'set an strptime compatible string to customize\
            the time format (default: {DEFAULT_TIME_FORMAT.replace("%", "%%")})',
        type=str,
    )
    parser.add_argument(
        "--color",
        help="control color output (default: True)",
        type=bool,
        action=argparse.BooleanOptionalAction,
        default=True,
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {VERSION}"
    )
    parser.add_argument(
        "--accept-warning",
        help="accept/suppress all warning prompts (default:\
            False)",
        action="store_true",
        default=False,
    )

    group = parser.add_mutually_exclusive_group()
    for unit in UNITS:
        for mag in MAGS:
            group.add_argument(
                f"-{unit[0]}{mag}",
                f"--{unit}{mag}",
                help=f"show earthquakes >=\
                    M{mag / 10:.1f} of the last {unit}",
                action="store_true",
            )
        group.add_argument(
            f"-{unit[0]}s",
            f"--{unit}",
            help=f"show significant earthquakes of \
                the {unit}",
            action="store_true",
        )
        group.add_argument(
            f"-{unit[0]}a",
            f"--{unit}-all",
            help=f"show all earthquakes of the \
                last {unit}",
            action="store_true",
        )
    return parser.parse_args()


def print_table(url, follow):
    """prints the table of all earthquakes"""
    try:
        req = requests.get(url, timeout=QwState.timeout)
    # broad except is the intention here
    # pylint: disable=broad-exception-caught
    except Exception as e:
        print(f"{QwState.progname}: error: {e}", file=sys.stderr)
        sys.exit(1)
    earthquakes = req.json()
    currenttime = (
        datetime.now() if QwState.localtime else datetime.now(timezone.utc)
    )
    quakelist = list(map(get_earthquake, earthquakes["features"]))
    tz_name = (
        str(time.localtime().tm_zone)
        if QwState.localtime
        else str(currenttime.tzinfo)
    )
    quakeheaders = [
        f"Time ({tz_name})",
        "Mag",
        "Location",
        "PAGER",
        "More info",
    ]
    if QwState.geolink:
        quakeheaders.append("Geo link")
    events_found = len(quakelist)

    if events_found >= 50 and not QwState.acceptwarn:
        if confirmation_prompt(
            f"""Warning, {events_found} is greater than 50.

The --accept-warning argument can be used to bypass this prompt.
Choosing yes here will suppress subsequent warnings.

Continue?"""
        ):
            QwState.acceptwarn = True
            print("Continuing...")
        else:
            print("Aborting...")
            sys.exit(1)

    if not follow:
        os.system("clear")

    refreshstr = ""
    if not QwState.runonce:
        refreshstr = (
            f", refreshing every {convert_seconds_to_hr(QwState.refresh)}"
        )

    print(f'{earthquakes["metadata"]["title"]}{refreshstr}')
    print(
        f"Current Time ({tz_name}): {currenttime.strftime(QwState.timeformat)}"
    )
    print(f"Events found: {events_found}")

    if not follow:
        print(tabulate(quakelist, headers=quakeheaders, floatfmt=".1f"))
    else:
        print(" | ".join(quakeheaders))
        for x in quakelist:
            print(" | ".join(x))


def parse_arg_to_seconds(arg):
    """parse argument time string to seconds"""

    if len(arg) < 2:
        raise ValueError(
            "invalid argument, {number} or {number}{unit} required"
        )

    # extract
    unit = "s"
    if not arg[-1].isdigit():
        unit = arg[-1]
        value = float(arg[:-1])
    else:
        value = float(arg)

    # convert
    if unit == "s":
        result = int(value)
    elif unit == "m":
        result = int(value * 60)
    elif unit == "h":
        result = int(value * 3600)
    else:
        raise ValueError(
            'invalid argument unit, use "s" for seconds, "m" for\
 minutes, or "h" for hours'
        )

    # ensure minimum
    if result < QwState.refresh:
        raise ValueError(
            f'requires minimum value "{QwState.refresh}(s)" not:\
 "{arg}"'
        )

    # ensure maximum
    if result > 86400:
        raise ValueError("invalid duration, greater than 24 hours")

    return result


def process_args(args):
    # we only process args once...
    # pylint: disable=too-many-branches
    """process arguments"""
    if isinstance(args.alarm, str):
        if args.alarm != "":
            try:
                QwState.alarm = shlex.split(args.alarm)
            except ValueError as e:
                print(
                    f"{QwState.progname}: error parsing argument -a/--alarm command:\
                        {e}",
                    file=sys.stderr,
                )
                sys.exit(1)
        else:
            print(
                f"{QwState.progname}: error: argument -a/--alarm requires an input string",
                file=sys.stderr,
            )
            sys.exit(1)
    if isinstance(args.pager, list):
        for pager in args.pager:
            if not pager in PAGERS:
                print(
                    f'{QwState.progname}: error: argument -p/--pager: requires input of {PAGERS}\
 not: "{pager}"',
                    file=sys.stderr,
                )
                sys.exit(1)
        QwState.pageralerts = args.pager
    if args.refresh:
        if args.run_once:
            print(
                f"{QwState.progname}: error: arguments -r/--refresh and -ro/--run-once cannot be\
 used simultaneously",
                file=sys.stderr,
            )
            sys.exit(1)
        try:
            refresh = parse_arg_to_seconds(args.refresh)
            QwState.refresh = refresh
        except ValueError as e:
            print(
                f"{QwState.progname}: error: argument -r/--refresh: {e}",
                file=sys.stderr,
            )
            sys.exit(1)
    if args.timeout:
        if args.timeout[0] > QwState.timeout:
            QwState.timeout = args.timeout[0]
        elif not args.timeout[0] == QwState.timeout:
            print(
                f'{QwState.progname}: error: argument -t/--timeout: requires minimum value\
 "{QwState.timeout}" not: "{args.timeout[0]}"',
                file=sys.stderr,
            )
            sys.exit(1)
    if args.time_format:
        if validate_time_format(args.time_format):
            QwState.timeformat = args.time_format
        else:
            print(
                f'{QwState.progname}: error: argument --time-format: requires strftime format\
 like "{DEFAULT_TIME_FORMAT}" not: "{args.time_format}"',
                file=sys.stderr,
            )
            sys.exit(1)


def select_site(args):
    """parse args to select a site"""
    urls = get_sites()
    site = urls["significant_day"]
    for unit in UNITS:
        for mag in MAGS:
            if getattr(args, f"{unit}{mag}", True):
                if (
                    (unit == "day" and mag == 10)
                    or unit in ("week", "month")
                    and not QwState.acceptwarn
                ):
                    # warn about results
                    if confirmation_prompt(
                        f"""Warning, magnitude >= {mag} results for the\
 {unit} can number in the hundreds.

The --accept-warning argument can be used to bypass this prompt.
Choosing yes here will suppress subsequent warnings.

Continue?"""
                    ):
                        QwState.acceptwarn = True
                        print("Continuing...")
                    else:
                        print("Aborting...")
                        sys.exit(1)
                site = urls[f"{unit}{mag}"]
        if getattr(args, f"{unit}", True):
            site = urls[f"significant_{unit}"]
        if getattr(args, f"{unit}_all", True):
            if unit in ("day", "week", "month") and not QwState.acceptwarn:
                # warn about results
                if confirmation_prompt(
                    f"""Warning, all results for the {unit} can number in\
 the hundreds.

The --accept-warning argument can be used to bypass this prompt.
Choosing yes here will suppress subsequent warnings.

Continue?"""
                ):
                    QwState.acceptwarn = True
                    print("Continuing...")
                else:
                    print("Aborting...")
                    sys.exit(1)
            site = urls[f"all_{unit}"]
    return site


def run_custom_alarm():
    """execute custom subprocess triggered by alerts"""
    try:
        # we want this to be non-blocking
        # pylint: disable=consider-using-with
        subprocess.Popen(QwState.alarm)
    except subprocess.TimeoutExpired:
        print(
            f"{QwState.progname}: alarm error: command timed out",
            file=sys.stderr,
        )
        sys.exit(1)
    except FileNotFoundError:
        print(
            f"{QwState.progname}: alarm error: command not found: {QwState.alarm[0]}",
            file=sys.stderr,
        )
        sys.exit(1)
    # broad except is the intention here
    # pylint: disable=broad-exception-caught
    except Exception as e:
        print(
            f"{QwState.progname}: alarm error: command unexpected error: {e}",
            file=sys.stderr,
        )
        sys.exit(1)
    QwState.alerted = True


def validate_time_format(timefmt):
    """test a strptime string format"""
    try:
        timestr = datetime.now().strftime(timefmt)
        datetime.strptime(timestr, timefmt)
        return True
    except ValueError:
        return False


def main():
    """main function to parse arguments and watch for earthquakes"""

    parser = argparse.ArgumentParser(
        description=DESCRIPTION,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    QwState.progname = parser.prog
    QwState.pageralerts = []
    QwState.alarm = []
    args = init_args(parser)
    QwState.acceptwarn = args.accept_warning
    site = select_site(args)
    process_args(args)

    QwState.enablecolor = args.color
    QwState.geolink = args.geo_link
    QwState.localtime = args.localtime
    QwState.runonce = args.run_once
    if isinstance(args.magnitude, float):
        QwState.magalert = args.magnitude

    while True:
        try:
            print_table(site, args.follow)
            if args.follow and not args.run_once:
                print()
            sys.stdout.flush()  # flush for pipe compatibility
            QwState.alerted = False
            if args.run_once:
                break
            time.sleep(QwState.refresh)
        except KeyboardInterrupt:
            print(flush=True)  # this puts the prompt on the next line
            break
        except BrokenPipeError:
            sys.stderr.close()  # handle broken pipe gracefully
            raise


if __name__ == "__main__":
    try:
        main()
    except IOError as e:
        if e.errno == errno.EPIPE:
            # ignore pipe error trace
            pass
