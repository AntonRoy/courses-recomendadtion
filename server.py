from flask import Flask, render_template, request, redirect
import os
import sqlite3
from flask_bootstrap import Bootstrap
import numpy as np

app = Flask(__name__)
boostrap = Bootstrap(app)

UPLOAD_FOLDER = '/home/anton/Documents/CursRec/static'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

languages = ['Python', 'Scala', 'PHP', 'Java', 'Haskell',
                     'Rust', 'C++', 'C#', 'C', 'HTML', 'CSS',
                     'Javascript', 'Ruby', 'GO', 'TypeScript',
                     'Swift', 'Objective C', 'Bash']

spheres = ['Web программист', 'Mobile-разработчик', 'Разработчик игр', 'Дизайнер интерфейсов']

sphere2tags = {}

def courses_of_sphere(sphere, n_courses):
    global sphere2tags
    cnn = sqlite3.connect("data")
    cur = cnn.cursor()
    tags = sphere2tags[sphere]
    courses = cur.execute("SELECT * FROM COURSES").fetchall()
    best_courses = [[0, ()] for i in range(n_courses)]
    for course in courses:
        cnt = 0
        if course[3] == '-':
            continue
        best_courses.sort()
        for tag in tags:
            if tag in (course[0] + course[1]).lower():
                cnt += 1
        if cnt >= best_courses[0][0]:
            best_courses[0] = [cnt, course]
    best_courses.sort(key=lambda x: -x[0])
    return list(map(lambda x: x[1], best_courses))


@app.route("/")
def start():
    return redirect('/questions')


@app.route('/questions', methods=['GET', 'POST'])
def recomendation():
    global languages
    global spheres
    if request.method == 'POST':
        languages = [el[0] if el[1][0] == 'on' else "" for el in list(dict(request.form).items())]
        languages.sort()
        languages = languages[languages.count("") + 1:]
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        courses = courses_of_sphere(spheres, 10)
        return render_template("recomendation.html", courses=courses)
    elif request.method == "GET":
        return render_template("questions.html", languages=languages, spheres=spheres)


app.secret_key = os.urandom(24)


if __name__ == '__main__':
    app.run(debug=True)