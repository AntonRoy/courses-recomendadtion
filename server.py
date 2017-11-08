from flask import Flask, render_template, request, redirect, make_response
import os
import sqlite3
from flask_bootstrap import Bootstrap
import numpy as np
import uuid

app = Flask(__name__)
boostrap = Bootstrap(app)

languages = ['Python', 'Scala', 'PHP', 'Java', 'Haskell',
             'Rust', 'C++', 'C#', 'C', 'HTML', 'CSS',
             'Javascript', 'Ruby', 'GO', 'TypeScript',
             'Swift', 'Objective C', 'Bash']

spheres = ['Web программист', 'Mobile-разработчик', 'Разработчик игр',
           'Дизайнер интерфейсов', 'Анализ данных']

sphere2tags = {
    'Web программист': ['data science', 'css', 'html', 'javascript', 'php', 'sql',
                        'yii2', 'ruby', 'ruby on rails', 'reactjs', 'django', 'flask', 'tornado'],
    'Mobile-разработчик': ['java', 'swift', 'android', 'ios', 'objective-c'],
    'Разработчик игр': ['c#', 'unity', 'ооп', '.net'],
    'Дизайнер интерфейсов': ['photoshop', 'UX', 'UI', 'sketch'],
    'Анализ данных': ['reinforcement learning',
    'semi-supervised learning',
    'unsupervised learning',
    'advanced machine learning',
    'supervised learning',
    'statistical learning',
    'machine learning',
    'artificial intelligence',
    'feature extraction',
    'fuzzy clustering',
     'SVD', 'NMF', 'DSSM'],
    'Программист распределенных систем': ['hadoop', 'spark', 'haskel', 'rust', 'exonum', 'python', 'R']
}

users = {}

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


@app.route("/rec_sys/")
def start():
    return redirect('/rec_sys/questions')


@app.route("/rec_sys/recomendation", methods=['GET', 'POST'])
def recomendate():
    if request.method == 'POST':
        cnn = sqlite3.connect('dataset')
        cur = cnn.cursor()
        actual_courses = [el[0] for el in list(dict(request.form).items())]
        id_ = request.cookies.get('user_id')
        data = users[id_]
        for i in range(len(data[0])):
            course = data[0][i]
            if i in actual_courses:
                cur.execute("INSERT INTO USERS_COURSES (ID, NAME, LAST_NAME, COURSE_TEXT, COURSE_LINK, LANGUAGES) VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}')"
                            .format(id_, data[1], data[2], course[0] + ". " + course[1], course[3], ", ".join(data[3])))
                cnn.commit()
            #print((id_, data[1], data[2], course[0] + ". " + course[1], course[3]))
        return render_template('thanks_for_data.html')
    elif request.method == 'GET' and request.cookies.get('user_id'):
        id_ = request.cookies.get('user_id')
        courses = users[str(id_)][0]
        courses = list(map(lambda x: [x[0], ". ".join(x[1].split(". ")[:4]) + ". ", x[2], x[3]], courses))
        return render_template('recomendation.html', courses=courses, length=len(courses))
    else:
        return redirect('/rec_sys/questions')


@app.route('/rec_sys/questions', methods=['GET', 'POST'])
def recomendation():
    global languages, spheres, courses
    if request.method == 'POST':
        id_ = str(uuid.uuid4().int)
        lang = [el[0] if el[1][0] == 'on' else "" for el in list(dict(request.form).items())]
        lang.sort()
        languages1 = lang[lang.count("") + 1:]
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        sphere = request.form['sphere']
        response = make_response(redirect('/rec_sys/recomendation'))
        response.set_cookie('user_id', id_)
        users[id_] = [courses_of_sphere(sphere, 10), first_name, last_name, lang]
        return response
    elif request.method == "GET":
        return render_template("questions.html", languages=languages, spheres=spheres)


app.secret_key = os.urandom(24)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)