import random
from flask import abort, Flask, jsonify, request, render_template
app = Flask(__name__)

@app.route('/')
def index():
  return 'it worked!'

if __name__ == '__main__':
  app.run()
