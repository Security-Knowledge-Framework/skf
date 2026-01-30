from flask import Flask, render_template, abort
from flask_cors import CORS
import json, os
from itertools import groupby

app = Flask(__name__, static_folder='static')
CORS(app)  # This will allow all domains (Access-Control-Allow-Origin: *)

@app.route('/')
def courses():
    return render_template('courses.html')


@app.route('/requirements')
def home():
    with open('converter/ASVS-4.0.3.json', 'r') as f:
        data = json.load(f)
    
    data.sort(key=lambda x: x['chapter_name'])
    grouped_data_by_chapter = {k: list(v) for k, v in groupby(data, key=lambda x: x['chapter_name'])}
    
    data.sort(key=lambda x: x['section_name'])
    grouped_data_by_section = {k: list(v) for k, v in groupby(data, key=lambda x: x['section_name'])}
    
    return render_template('checklist.html', data_chapter=grouped_data_by_chapter, data_section=grouped_data_by_section)

@app.route('/course/<name>')
def course(name):
    filepath = os.path.join('data', 'courses', f'{name}.json')
    if not os.path.isfile(filepath):
        filepath_upper = os.path.join('data', 'courses', f'{name.upper()}.json')
        if not os.path.isfile(filepath_upper):
            abort(404)
        filepath = filepath_upper  # fallback to uppercase version

    with open(filepath, 'r') as f:
        course_data = json.load(f)
    return render_template('course.html', course=course_data)



@app.route('/labs')
def labs():
    return render_template('labs.html')


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
