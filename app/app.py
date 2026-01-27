from flask import Flask, render_template, abort
from flask_cors import CORS
import json, os
from itertools import groupby

app = Flask(__name__)
CORS(app)  # This will allow all domains (Access-Control-Allow-Origin: *)



def load_json(file_json):
    with open(file_json, "r", encoding="utf-8") as f:
        return json.load(f)

def search_courses(query, max_results=100):
    query = query.lower()
    keywords = query.split()
    file_json = "data/roles/linuxfoundation_courses.json"
    courses = load_json(file_json)
    results = []

    for course in courses:
        score = 0
        title = course.get("title", "").lower()
        description = course.get("description", "").lower()
        category = course.get("category", "").lower()
        difficulty = course.get("difficulty", "").lower()

        for kw in keywords:
            if kw in title:
                score += 3
            if kw in description:
                score += 2
            if kw in category:
                score += 10
            if kw in difficulty:
                score += 1

        if score > 0:
            results.append((score, course))

    results.sort(reverse=True, key=lambda x: x[0])
    return [r[1] for r in results[:max_results]]

@app.route('/')
def courses():
    return render_template('courses.html')

@app.route('/roles')
def roles():
    return render_template("roles.html")

@app.route('/role/<name>')
def role(name):
    # Load course catalog and map by ID
    course_data = load_json("data/roles/linuxfoundation_courses.json")
    course_map = {course["id"]: course for course in course_data}

    # Load learning path per role
    if "linux" in name.lower():
        role_path = load_json("data/roles/role_learning_paths_kernel.json")
    elif "security" in name.lower():
        role_path = load_json("data/roles/role_learning_paths_cybersecurity.json")
    elif "kubernetes" in name.lower():
        role_path = load_json("data/roles/role_learning_paths_kubernetes.json")
    elif "genai" in name.lower():
        role_path = load_json("data/roles/role_learning_paths_ai.json")
    else:
        role_path = load_json("data/roles/role_learning_paths_kernel.json")


    # Enrich role_path with full course info
    for level in role_path:
        enriched = []
        for entry in role_path[level]["courses"]:
            course_id = entry.get("id")
            if course_id in course_map:
                enriched.append(course_map[course_id])
        role_path[level]["courses"] = enriched
    return render_template("role.html", role_tracks=role_path, job_name=name)

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
        abort(404)
    with open(filepath, 'r') as f:
        course_data = json.load(f)
    return render_template('course.html', course=course_data)


@app.route('/labs')
def labs():
    return render_template('labs.html')


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
