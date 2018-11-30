import json
import os

from flask import Flask, flash, render_template, request
from wtforms import Form, StringField, SubmitField, TextAreaField, validators

PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))
PROJECT_ROOT_1LVL = os.path.dirname(PROJECT_ROOT)
LINES_FILE = os.path.join(PROJECT_ROOT_1LVL, 'nhl-twitter-bot', 'localdata', 'lines-override.json')

# Flask Application Config
#DEBUG = True
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

def readLinesFile():
    with open(LINES_FILE) as f:
        lines = json.load(f)
    return lines


def writeLinesFile(lines):
    with open(LINES_FILE, 'w') as f:
        json.dump(lines, f)


@app.route("/", methods=['GET', 'POST'])
def lines_form():
    form = LinesForm(request.form)

    lines = readLinesFile()
    print(f'Lines from File: {lines}')

    if request.method == 'POST':

        confirmed_lines = dict()
        for fieldname, value in form.data.items():
            # Convert fieldname from <POS><LINE> to <LINE><POS>
            line = fieldname[-1]
            position = fieldname[0:-1]
            key = f'{line}{position}'
            # print(fieldname, key, value)
            confirmed_lines[key] = value

        print(f'Confirmed Lines: {confirmed_lines}')
        writeLinesFile(confirmed_lines)

        if form.validate():
            flash('Lineup confirmed!', 'success')
        else:
            flash('All the form fields are required.', 'error')

    return render_template('lines.html', form=form, lines=lines)

if __name__ == "__main__":
    app.run('0.0.0.0')
