"""
This module serves as a front-end to the Lines Override function
of the NHL Twitter Bot. Also does validation of player names.
"""

import json
import logging
import os
from datetime import datetime

import requests
from dateutil.parser import parse
from flask import (Flask, flash, jsonify, redirect, render_template, request,
                   url_for)
from wtforms import Form, StringField, SubmitField, TextAreaField, validators

PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))
PROJECT_ROOT_1LVL = os.path.dirname(PROJECT_ROOT)
LINES_FILE = os.path.join(PROJECT_ROOT_1LVL, 'nhl-twitter-bot', 'localdata', 'lines-override.json')

NHL_API_BASE = 'http://statsapi.web.nhl.com/api/v1'
NHL_API_BASEONLY = 'http://statsapi.web.nhl.com'

# Flask Application Config
# DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '6ac69d35549cb232a7946da014f03a68030991afc7a7f29b'

class LinesForm(Form):
    C1 = StringField('C1', [validators.DataRequired()], render_kw={"placeholder": "Center #1"})
    LW1 = StringField('LW1', [validators.DataRequired()], render_kw={"placeholder": "Left Wing #1"})
    RW1 = StringField('1RW', [validators.DataRequired()], render_kw={"placeholder": "Right Wing #1"})
    C2 = StringField('2C', [validators.DataRequired()], render_kw={"placeholder": "Center #2"})
    LW2 = StringField('2LW', [validators.DataRequired()], render_kw={"placeholder": "Left Wing #2"})
    RW2 = StringField('2RW', [validators.DataRequired()], render_kw={"placeholder": "Right Wing #2"})
    C3 = StringField('3C', [validators.DataRequired()], render_kw={"placeholder": "Center #3"})
    LW3 = StringField('3LW', [validators.DataRequired()], render_kw={"placeholder": "Left Wing #3"})
    RW3 = StringField('3RW', [validators.DataRequired()], render_kw={"placeholder": "Right Wing #3"})
    C4 = StringField('4C', [validators.DataRequired()], render_kw={"placeholder": "Center #4"})
    LW4 = StringField('4LW', [validators.DataRequired()], render_kw={"placeholder": "Left Wing #4"})
    RW4 = StringField('4RW', [validators.DataRequired()], render_kw={"placeholder": "Right Wing #4"})
    LD1 = StringField('LD1', [validators.DataRequired()], render_kw={"placeholder": "Left Defense #1"})
    RD1 = StringField('RD1', [validators.DataRequired()], render_kw={"placeholder": "Right Defense #1"})
    LD2 = StringField('LD2', [validators.DataRequired()], render_kw={"placeholder": "Left Defense #2"})
    RD2 = StringField('RD2', [validators.DataRequired()], render_kw={"placeholder": "Right Defense #2"})
    LD3 = StringField('LD3', [validators.DataRequired()], render_kw={"placeholder": "Left Defense #3"})
    RD3 = StringField('RD3', [validators.DataRequired()], render_kw={"placeholder": "Right Defense #3"})


# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# NHL Score & Parsing Methods
# ------------------------------------------------------------------------------

def get_all_teams():
    teams_url = f'{NHL_API_BASE}/teams?expand=team.stats,team.roster'
    try:
        logging.info("Sending All Teams API Request - %s", teams_url)
        all_teams = requests.get(teams_url)
        all_teams_date = parse(all_teams.headers['Date'])
        all_teams_json = all_teams.json()
    except requests.exceptions.RequestException:
        logging.error('Unable to get team information.')

    return (all_teams_json['teams'], all_teams_date)


def generate_roster_team_dict(all_teams):
    roster_dict = dict()
    for team in all_teams:
        team_id = team['id']
        players = team['roster']['roster']
        for player in players:
            player_name = player['person']['fullName'].upper()
            player_id = player['person']['id']
            roster_dict[player_name] = dict()
            roster_dict[player_name]['team'] = team_id
            roster_dict[player_name]['id'] = player_id

    return roster_dict


# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# File System Methods
# ------------------------------------------------------------------------------

def readLinesFile():
    try:
        with open(LINES_FILE) as f:
            lines = json.load(f)
    except FileNotFoundError:
        # 'Touch' the File
        with open(LINES_FILE, 'a'):
            os.utime(LINES_FILE, None)

        # Return an empty dictionary
        lines = {'1C': '', '1LW': '', '1RW': '',
                 '2C': '', '2LW': '', '2RW': '',
                 '3C': '', '3LW': '', '3RW': '',
                 '4C': '', '4LW': '', '4RW': '',
                 '1LD': '', '1RD': '',
                 '2LD': '', '2RD': '',
                 '3LD': '', '3RD': ''}

    filetime = os.path.getmtime(LINES_FILE)

    return (lines, filetime)


def writeLinesFile(lines):
    with open(LINES_FILE, 'w') as f:
        json.dump(lines, f)


# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# Flask Routes
# ------------------------------------------------------------------------------

@app.route("/", methods=['GET'])
def lines_form():
    form = LinesForm(request.form)

    # API Driven Development
    lines_dict = get_lines().get_json()
    lines = lines_dict['lines']

    confirmed = dict(lines_dict)
    confirmed.pop('lines')

    print(lines)
    print(confirmed)

    return render_template('lines.html', form=form, lines=lines, confirmed=confirmed)


@app.route("/updatelines", methods=['POST'])
def update_lines():
    player_error = False
    form = LinesForm(request.form)

    if request.method == 'POST':
        confirmed_lines = dict()
        for fieldname, value in form.data.items():
            # Convert fieldname from <POS><LINE> to <LINE><POS>
            line = fieldname[-1]
            position = fieldname[0:-1]
            key = f'{line}{position}'
            # print(fieldname, key, value)
            confirmed_lines[key] = value

        # Check if a player exists and if all players are on the same team
        for position, player in confirmed_lines.items():
            try:
                player_id = roster_dict[player.upper()]['id']
                player_team = roster_dict[player.upper()]['team']
            except KeyError:
                # Sometimes a player is an AHL call-up & not on NHL Roster Page
                logging.info('%s is not on the master roster - check live feed for verification.', player)
                lookup_position = '1C' if position != '1C' else '2C'
                lookup_player = confirmed_lines[lookup_position]
                lookup_team = roster_dict[lookup_player.upper()]['team']

                schedule = f'https://statsapi.web.nhl.com/api/v1/schedule?teamId={lookup_team}'
                logging.info('Getting Schedule via API - %s', schedule)
                schedule_json = requests.get(schedule).json()
                live_feed = schedule_json['dates'][0]['games'][0]['link']
                live_feed_url = f'{NHL_API_BASEONLY}{live_feed}'
                logging.info('Getting Live Feed via API - %s', live_feed_url)
                live_feed_resp = requests.get(live_feed_url).text
                if player not in live_feed_resp:
                    flash(f'{player} is in invalid NHL player.', 'error')
                    return redirect(url_for('lines_form'))

        print(f'Confirmed Lines: {confirmed_lines}')
        writeLinesFile(confirmed_lines)

        if form.validate():
            flash('Lineup confirmed!', 'success')
        else:
            flash('All the form fields are required.', 'error')

    return redirect(url_for('lines_form'))


@app.route("/getlines", methods=['GET'])
def get_lines():
    lines, filetime = readLinesFile()

    confirmed_datetime = datetime.fromtimestamp(filetime)
    confirmed_today = bool(confirmed_datetime.date() == datetime.today().date())
    confirmed_str = confirmed_datetime.strftime('%Y-%m-%d %H:%M%p')

    return_dict = dict()
    return_dict['confirmed'] = confirmed_today
    return_dict['confirmed_datetime'] = confirmed_str
    return_dict['lines'] = lines

    return jsonify(return_dict)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S',
                        format='%(asctime)s - %(module)s.%(funcName)s (%(lineno)d) - %(levelname)s - %(message)s')

    # Generate Roster Dictionary (for player name validation)
    all_teams, all_teams_date = get_all_teams()
    roster_dict = generate_roster_team_dict(all_teams)
    app.run('0.0.0.0')
