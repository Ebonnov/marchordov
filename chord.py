import logging
import random
from flask import abort, Flask, jsonify, request, render_template, session
app = Flask(__name__)

if not app.debug:
  file_handler = logging.FileHandler('dummy_log')
  file_handler.setLevel(logging.WARNING)
  app.logger.addHandler(file_handler)

app.config.from_object('config.DefaultConfig')

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/_randomsandbox')
def random_sandbox():
  base = 48 + random.randint(0, 11)
  ority = random.randint(0, 1)
  result = [base, base + 3 + ority, base + 7]
  return jsonify(result=result)

@app.route('/_generatefirstquestion')
def first_question():
  # 0: minor, 1: major, 2: dimished
  answer = random.randint(0, 14) / 6
  base = 48 + random.randint(0, 11)
  if answer == 2:
    chord = [base, base + 3, base + 6]
  else:
    chord = [base, base + 3 + answer, base + 7]
  choice = ['minor', 'major', 'diminished']
  session['expected'] = answer
  return jsonify(chord=chord, choice=choice, endpoint='_answerfirstquestion')

@app.route('/_answerfirstquestion')
def answer_first_question():
  if not 'expected' in session:
    return jsonify(error='problem or session cookie corrupted')
  expected = session['expected']
  answer = request.args.get('answer', None)
  if answer is None:
    return jsonify(error='expected answer')

  session.pop('expected', None)
  tooltip = ['minor', 'major', 'diminished']
  try:
    answer = int(answer)
    expected = int(expected)
    answer_tooltip = tooltip[answer]
    expected_tooltip = tooltip[expected]
  except (ValueError, IndexError) as e:
    return jsonify(error='Something went wrong: %s' % e)
  if answer == expected:
    return jsonify(result='Yes!')
  else:
    return jsonify(result='No. You answered %s, %s was generated instead' %
        (answer_tooltip, expected_tooltip)
        )

def create_dummy_session():
  # This is trivial.
  return jsonify(endpoint='_generatefirstquestion')

def create_inkey_session():
  key = random.randint(0, 11)
  major = random.randint(0, 1)
  session['key'] = key
  # Bad naming
  session['majorness'] = major
  # major: 0 2 4 5 7 9 11
  # 0 4 7, 2 5 9, 4 7 11, 5 9 12, 7 11 14, 9 12 16, 11 14 17
  # minor: 0 2 3 5 7 8 11?
  # i.e. 0 3 7, 2 5 8, 3 7 10, 5 8 12, 7 11 14, 8 12 15, 11 14 18
  # Need to 'print' a I or i here
  base = [45 + key, 48 + key + major, 52 + key, 57 + key]
  return jsonify(baseprint=base, endpoint='_generateinkeyquestion')

inkey_chords = [
  [
    ([0, 3, 7], 'i'),
    ([2, 5, 8], 'ii-'),
    ([3, 7, 10], 'III'),
    ([5, 8, 12], 'iv'),
    ([7, 11, 14], 'V'),
    ([8, 12, 15], 'VI'),
    ([11, 14, 17], 'vii-'),
  ],[
    ([0, 4, 7], 'I'),
    ([2, 5, 9], 'ii'),
    ([4, 7, 11], 'iii'),
    ([5, 9, 12], 'IV'),
    ([7, 11, 14], 'V'),
    ([9, 12, 16], 'vi'),
    ([11, 14, 17], 'vii-'),
  ]
]

@app.route('/_generateinkeyquestion')
def generate_inkey_question():
  if 'session' not in session or session['session'] != 'inkey':
    return jsonify(error='wrong session')
  if 'key' not in session or 'majorness' not in session:
    return jsonify(error='session corrupted')
  chord_set = inkey_chords[session['majorness']]
  # randint and I hate each other
  expected = random.randint(0, len(chord_set) - 1)
  chord = [x + 45 + session['key'] for x in chord_set[expected][0]]
  session['expected'] = expected
  return jsonify(chord=chord, choice=[c[1] for c in chord_set],
    endpoint='_answerinkeyquestion')

@app.route('/_answerinkeyquestion')
def answer_inkey_question():
  if not 'expected' in session:
    return jsonify(error='problem or session cookie corrupted')
  expected = session['expected']
  answer = request.args.get('answer', None)
  if answer is None:
    return jsonify(error='expected answer')

  session.pop('expected', None)
  tooltip = [c[1] for c in inkey_chords[session['majorness']]]
  try:
    answer = int(answer)
    expected = int(expected)
    answer_tooltip = tooltip[answer]
    expected_tooltip = tooltip[expected]
  except (ValueError, IndexError) as e:
    return jsonify(error='Something went wrong: %s' % e)
  if answer == expected:
    return jsonify(result='Yes!')
  else:
    return jsonify(result='No. You answered %s, %s was generated instead' %
        (answer_tooltip, expected_tooltip)
        )

#   <---      what session you're in, what session available
#   --->      start session
#             roll dice for the session
#   <---      key to show, set state
#   --->      start first problem
# Am I reinventing a wheel?

@app.route('/_create_session')
def create_session():
  if 'session' in session:
    return jsonify(
      error='Another session is ongoing. Click "end current session" to end.')
  session_name_supported = {
    'dummy': create_dummy_session,
    'inkey': create_inkey_session,
  }
  name = request.args.get('session_name', None)
  if name not in session_name_supported:
    return jsonify(error='session name {} is not supported'.format(name))
  session['session'] = name
  return session_name_supported[name]()

@app.route('/_query_session')
def query_session():
  if 'session' in session:
    return jsonify(has_session='yes', session=session['session'])
  else:
    # probably just use if data.session to tell anyway
    return jsonify(has_session='no')

@app.route('/_clear_session')
def clear_session():
  if 'session' in session:
    del session['session']
  return jsonify()

if __name__ == '__main__':
  app.run()
