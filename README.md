# NHL Twitter Game Bot - Lines Override

This script is used in conjunction with the [
NHL Twitter Bot](https://github.com/mattdonders/nhl-twitter-bot) to override lines when they are not externally set during pre-game checks. If you are not running that bot, this script serves no other purpose.

When a lineup is confirmed, the script will perform validation against the NHL API to be sure the players specified exist and are spelled correctly.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites and Installation

To run this bot, download the most current release, setup your virtual environment and install the requirements via pip.

```
git clone git@github.com:mattdonders/nhl-lines-override.git
cd nhl-lines-override
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

### Execution

I execute the script and send it to the background so it constantly runs.
```
nohup python lines.py &
```

The script modifies a file that is used by the Twitter Bot to override lines, but can also be hit via API directly (as per the examples below). The API provides more context to the **confirmation** of the lines (ie - if the lines were confirmed today).
```
$ cat ../nhl-twitter-bot/localdata/lines-override.json
{"1C": "Nico Hischier", "1LW": "Taylor Hall", "1RW": "Jesper Bratt",
"2C": "Travis Zajac", "2LW": "Marcus Johansson", "2RW": "Kyle Palmieri",
"3C": "Brett Seney", "3LW": "Miles Wood", "3RW": "Blake Coleman",
"4C": "Brett Seney", "4LW": "Brian Boyle", "4RW": "Stefan Noesen",
"1LD": "Andy Greene", "1RD": "Damon Severson",
"2LD": "Egor Yakovlev", "2RD": "Sami Vatanen",
"3LD": "Will Butcher", "3RD": "Ben Lovejoy"}

$ curl 172.0.0.1:5000/getlines
{"confirmed":true,"confirmed_datetime":"2018-11-30 15:29PM",
"lines":{
"1C":"Nico Hischier","1LD":"Andy Greene","1LW":"Taylor Hall","1RD":"Damon Severson","1RW":"Jesper Bratt",
"2C":"Travis Zajac","2LD":"Egor Yakovlev","2LW":"Marcus Johansson","2RD":"Sami Vatanen","2RW":"Kyle Palmieri",
"3C":"Brett Seney","3LD":"Will Butcher","3LW":"Miles Wood","3RD":"Ben Lovejoy","3RW":"Blake Coleman",
"4C":"Brett Seney","4LW":"Brian Boyle","4RW":"Stefan Noesen"}}
```


## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/mattdonders/nhl-lines-override/tags).

## Authors

* **Matt Donders** - https://mattdonders.com
