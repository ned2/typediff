from flask import Flask, render_template, url_for, redirect

# Flask setup
app = Flask(__name__)



@app.route('/')
def index():
    return render_template('index.html', title='Typediff')
