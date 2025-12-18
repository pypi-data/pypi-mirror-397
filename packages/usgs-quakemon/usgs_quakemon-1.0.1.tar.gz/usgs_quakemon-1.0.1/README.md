# usgs-quakemon
Monitor **[USGS](https://earthquake.usgs.gov/)** **[GeoJSON](https://earthquake.usgs.gov/earthquakes/feed/v1.0/geojson.php)** earthquake feeds with *Python 3* from a <ins>CLI terminal</ins>. Optional audible alarm terminal bell or custom command is supported. Many options are available to customize output but [python-tabulate](https://github.com/astanin/python-tabulate) formatting is used by default.

## Requirements
* Python3 >= 3.10
* Both [python-tabulate](https://github.com/astanin/python-tabulate) and [Requests](https://github.com/psf/requests)
* **256 color** terminal capability for color output
* Network access to https://earthquake.usgs.gov

## Installation & Update
[pipx](https://github.com/pypa/pipx) install from the [PyPi package](https://pypi.org/project/usgs-quakemon) is recommended; pipx uses a virtual environment and optionally adds `usgs-quakemon` to the user's path.

```shell
# Recommended PyPi pipx installation #
pipx install usgs-quakemon
pipx ensurepath
source ~/.bashrc
usgs-quakemon --help

# Recommended PyPi pipx update
pipx upgrade usgs-quakemon


# Remote GitHub + pipx installation #
pipx install 'git+https://github.com/ryan-steed-usa/usgs-quakemon'
pipx ensurepath
source ~/.bashrc
usgs-quakemon --help

# Remote GitHub + pipx update
pipx upgrade usgs-quakemon
```

<details>
<summary>
Additional installation options
</summary>

```shell
# PyPi uvx installation
uvx usgs-quakemon

# PyPi uvx update
uvx usgs-quakemon@latest


# Clone repository + pipx installation #
git clone https://github.com/ryan-steed-usa/usgs-quakemon
pipx install ./usgs-quakemon
pipx ensurepath
source ~/.bashrc
usgs-quakemon --help

# Clone repository + pipx update
cd ./usgs-quakemon
git pull
pipx upgrade usgs-quakemon


# Clone + direct execution
git clone https://github.com/ryan-steed-usa/usgs-quakemon
cd usgs-quakemon
python3 -m pip install -r requirements.txt
python3 usgs-quakemon --help
```

</details>

## Usage
```
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
```
<details>
<summary>
Full usage
</summary>

```
usage: usgs-quakemon [-h] [-a ALARM] [-p PAGER [PAGER ...]] [-m MAGNITUDE] [-f] [-g] [-l] [-r REFRESH] [-ro] [-t TIMEOUT] [--time-format TIME_FORMAT] [--color | --no-color] [--version] [--accept-warning] [-h45 | -h25 | -h10 | -hs | -ha |
                     -d45 | -d25 | -d10 | -ds | -da | -w45 | -w25 | -w10 | -ws | -wa | -m45 | -m25 | -m10 | -ms | -ma]

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

options:
  -h, --help            show this help message and exit
  -a, --alarm ALARM     set a custom alarm command, this disables the terminal bell alarm, for example using the sox utility: "play -q ~/Audio/quake-alarm.wav"
  -p, --pager PAGER [PAGER ...]
                        enable audible alarm (defaults to terminal bell) for desired pager, valid pagers are ('red', 'orange', 'yellow', 'green')
  -m, --magnitude MAGNITUDE
                        enable audible alarm (defaults to terminal bell) for specified magnitude threshold, value >= mag will trigger the alarm
  -f, --follow          enable follow mode like tail, (default: False)
  -g, --geo-link        enable geo:// link column, (default: False)
  -l, --localtime       display timestamps in local timezone, (default: True)
  -r, --refresh REFRESH
                        set the API request refresh rate in optional time unit, omitted unit presumes "s" (seconds); minimum 60s, maximum 24h (default: 60s)
  -ro, --run-once       disable watch and run a single loop (default: False)
  -t, --timeout TIMEOUT
                        set the API request timeout value in seconds, minimum 10 (default: 10)
  --time-format TIME_FORMAT
                        set an strptime compatible string to customize the time format (default: %Y-%m-%d %H:%M:%S)
  --color, --no-color   control color output (default: True)
  --version             show program's version number and exit
  --accept-warning      accept/suppress all warning prompts (default: False)
  -h45, --hour45        show earthquakes >= M4.5 of the last hour
  -h25, --hour25        show earthquakes >= M2.5 of the last hour
  -h10, --hour10        show earthquakes >= M1.0 of the last hour
  -hs, --hour           show significant earthquakes of the hour
  -ha, --hour-all       show all earthquakes of the last hour
  -d45, --day45         show earthquakes >= M4.5 of the last day
  -d25, --day25         show earthquakes >= M2.5 of the last day
  -d10, --day10         show earthquakes >= M1.0 of the last day
  -ds, --day            show significant earthquakes of the day
  -da, --day-all        show all earthquakes of the last day
  -w45, --week45        show earthquakes >= M4.5 of the last week
  -w25, --week25        show earthquakes >= M2.5 of the last week
  -w10, --week10        show earthquakes >= M1.0 of the last week
  -ws, --week           show significant earthquakes of the week
  -wa, --week-all       show all earthquakes of the last week
  -m45, --month45       show earthquakes >= M4.5 of the last month
  -m25, --month25       show earthquakes >= M2.5 of the last month
  -m10, --month10       show earthquakes >= M1.0 of the last month
  -ms, --month          show significant earthquakes of the month
  -ma, --month-all      show all earthquakes of the last month
```

</details>

### Example
This command monitors for significant earthquakes occurring within the past week using a customized local timezone format. It will refresh every 4 hours automatically, and execute `play -q ~/Audio/quake-alarm.wav` if any alerts above *green* are detected. Non-default [Geo URIs](https://en.wikipedia.org/wiki/Geo_URI_scheme) are also output.
```shell
usgs-quakemon -ws -p 'red' 'orange' 'yellow' --time-format '%a %m-%d-%Y %I:%M:%S %p' -a "play -q ~/Audio/quake-alarm.wav" -r 4h -g -l
```
Example output:
<img width="1657" height="158" alt="image" src="https://github.com/user-attachments/assets/841b93c4-31b8-43eb-9311-1522df81399f" />

## Privacy
**No data is collected nor stored by the author.** Some information including origin IP address and HTTP request headers are required to be transmitted to the USGS API endpoint (https://earthquake.usgs.gov/) in order to poll for earthquake updates. The author cannot be held liable for the data collection policy instituted by the server administrators of the USGS services. **Privacy and security are highly valued and important to the author. This program will always remain transparent and open-source.**

---

### Credits
This project is based upon (and was originally forked from) **[quakewatch](https://github.com/baraclese/quakewatch)** by *[baraclese](https://github.com/baraclese)*. Thanks!

### Notes
_Generative "AI" is/was not used to "Vibe code" this project but (local) open-source and open-weight LLMs are employed for knowledge and summarization, mostly for commit_ logs.
