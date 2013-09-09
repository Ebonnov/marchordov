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
  # TODO: sanity check int-ity

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

if __name__ == '__main__':
  app.run()
