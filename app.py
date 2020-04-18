from flask import Flask, render_template, request, g, flash, redirect, session, abort, url_for, escape, Markup
import sqlite3
import os

DATABASE = './database.db'

# the function get_db is taken from here:
# https://flask.palletsprojects.com/en/1.1.x/patterns/sqlite3/


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

# the function make_dicts is taken from here:
# https://flask.palletsprojects.com/en/1.1.x/patterns/sqlite3/


def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value)
                for idx, value in enumerate(row))

# the function query_db is taken from here:
# https://flask.palletsprojects.com/en/1.1.x/patterns/sqlite3/


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


app = Flask(__name__)
app.secret_key = os.urandom(12)

# the function close_connection is taken from here:
# https://flask.palletsprojects.com/en/1.1.x/patterns/sqlite3/
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route('/')
def medium():
    if not session.get('logged_in'):
        return render_template('loginUser.html')
    else:
        return redirect(url_for('showHome'))


@app.route('/login', methods=['GET', 'POST'])
def user_login():
    if request.method == "POST":
        return validateUser()
    else:
        return render_template('loginUser.html')


@app.route('/logout')
def user_logout():
    session['logged_in'] = False
    session['student'] = False
    session['instructor'] = False
    return medium()


@app.route('/registerPortal')
def showRegister():
    if not session.get('logged_in'):
        return render_template('registerUser.html')
    return redirect(url_for('showHome'))


@app.route('/registerAction', methods=['POST'])
def registerUser():
    if not session.get('logged_in'):
        userFname = request.form['firstname']
        username = request.form['username']
        password = request.form['password']
        userType = request.form.get('usertype')

        db = get_db()
        db.row_factory = make_dicts

        sUserExist = query_db("SELECT username FROM Student WHERE username = ?", [
                              username], one=True)
        iUserExist = query_db("SELECT username FROM Instructor WHERE username = ?", [
                              username], one=True)

        if (sUserExist is not None) or (iUserExist is not None):
            flash(Markup(
                "User already exists. Are you sure <i>this</i> isn't your account?"))
            return redirect(url_for('showRegister'))
        else:
            if (userFname == '') or (username == '') or (password == '') or (userType == 'Select a user type'):
                flash("You forgot to input first name/username/password/user type")
                return redirect(url_for('showRegister'))
            elif (userType == 'student') and (('instructor' in username) or ('instructor' in password)):
                flash("You shouldn't be logging into this type of user!")
                return redirect(url_for('showRegister'))
            elif (userType == 'instructor') and (('student' in username) or ('student' in password)):
                flash("You shouldn't be logging into this type of user!")
                return redirect(url_for('showRegister'))
            elif userType == 'student':
                query_db("INSERT INTO Student (username, password, fname) VALUES (?, ?, ?)", [
                    username, password, userFname])
                db.commit()
                db.close()

                flash("You've successfully created an account.")
                return redirect(url_for('showRegister'))
            else:
                query_db("INSERT INTO Instructor (username, password, fname) VALUES (?, ?, ?)", [
                    username, password, userFname])
                db.commit()
                db.close()

                flash("You've successfully created an account.")
                return redirect(url_for('showRegister'))
    return redirect(url_for('showHome'))


@app.route('/validateUser', methods=['POST'])
def validateUser():
    username = request.form['username']
    password = request.form['password']

    db = get_db()
    db.row_factory = make_dicts
    studentUser = query_db("SELECT username FROM Student WHERE username = ? AND password = ?", [
        username, password], one=True)
    instructorUser = query_db("SELECT username FROM Instructor WHERE username = ? AND password = ?", [
        username, password], one=True)
    db.close()

    if studentUser is None and instructorUser is None:
        flash('Incorrect information provided, please try a different username/passsword.')
        session['logged_in'] = False
        return redirect(url_for('medium'))
    elif studentUser is not None:
        session['user'] = studentUser['username']
        session['logged_in'] = True
        session['student'] = True
        return redirect(url_for('medium'))
    elif instructorUser is not None:
        session['user'] = instructorUser['username']
        session['logged_in'] = True
        session['instructor'] = True
        return redirect(url_for('medium'))


@app.route('/home')
def showHome():
    if session.get('logged_in') and session.get('student'):
        username = session.get('user')

        db = get_db()
        db.row_factory = make_dicts

        name = query_db("SELECT fname FROM Student WHERE username = ?", [
            username], one=True)

        return render_template('index.html', user=name['fname'])
    elif session.get('logged_in') and session.get('instructor'):
        username = session.get('user')

        db = get_db()
        db.row_factory = make_dicts

        name = query_db("SELECT fname FROM Instructor WHERE username = ?", [
            username], one=True)

        return render_template('index.html', user=name['fname'])
    else:
        return redirect(url_for('medium'))


@app.route('/lectures')
def showLectures():
    if session.get('logged_in') and session.get('student'):
        username = session.get('user')

        db = get_db()
        db.row_factory = make_dicts

        name = query_db("SELECT fname FROM Student WHERE username = ?", [
            username], one=True)

        return render_template('lectures.html', user=name['fname'])
    elif session.get('logged_in') and session.get('instructor'):
        username = session.get('user')

        db = get_db()
        db.row_factory = make_dicts

        name = query_db("SELECT fname FROM Instructor WHERE username = ?", [
            username], one=True)

        return render_template('lectures.html', user=name['fname'])
    else:
        return redirect(url_for('medium'))


@app.route('/assignments')
def showAssignments():
    if session.get('logged_in') and session.get('student'):
        username = session.get('user')

        db = get_db()
        db.row_factory = make_dicts

        name = query_db("SELECT fname FROM Student WHERE username = ?", [
            username], one=True)

        return render_template('Assignments.html', user=name['fname'])
    elif session.get('logged_in') and session.get('instructor'):
        username = session.get('user')

        db = get_db()
        db.row_factory = make_dicts

        name = query_db("SELECT fname FROM Instructor WHERE username = ?", [
            username], one=True)

        return render_template('Assignments.html', user=name['fname'])
    else:
        return redirect(url_for('medium'))


@app.route('/resources')
def showResources():
    if session.get('logged_in') and session.get('student'):
        username = session.get('user')

        db = get_db()
        db.row_factory = make_dicts

        name = query_db("SELECT fname FROM Student WHERE username = ?", [
            username], one=True)

        return render_template('resources.html', user=name['fname'])
    elif session.get('logged_in') and session.get('instructor'):
        username = session.get('user')

        db = get_db()
        db.row_factory = make_dicts

        name = query_db("SELECT fname FROM Instructor WHERE username = ?", [
            username], one=True)

        return render_template('resources.html', user=name['fname'])
    else:
        return redirect(url_for('medium'))


@app.route('/labs')
def showLabs():
    if session.get('logged_in') and session.get('student'):
        username = session.get('user')

        db = get_db()
        db.row_factory = make_dicts

        name = query_db("SELECT fname FROM Student WHERE username = ?", [
            username], one=True)

        return render_template('labs.html', user=name['fname'])
    elif session.get('logged_in') and session.get('instructor'):
        username = session.get('user')

        db = get_db()
        db.row_factory = make_dicts

        name = query_db("SELECT fname FROM Instructor WHERE username = ?", [
            username], one=True)

        return render_template('labs.html', user=name['fname'])
    else:
        return redirect(url_for('medium'))


@app.route('/tests')
def showTests():
    if session.get('logged_in') and session.get('student'):
        username = session.get('user')

        db = get_db()
        db.row_factory = make_dicts

        name = query_db("SELECT fname FROM Student WHERE username = ?", [
            username], one=True)
        db.close()

        return render_template('Tests.html', user=name['fname'])
    elif session.get('logged_in') and session.get('instructor'):
        username = session.get('user')

        db = get_db()
        db.row_factory = make_dicts

        name = query_db("SELECT fname FROM Instructor WHERE username = ?", [
            username], one=True)
        db.close()

        return render_template('Tests.html', user=name['fname'])
    else:
        return redirect(url_for('medium'))


@app.route('/grades')
def getGrades():
    if session.get('logged_in'):
        username = session.get('user')
        sBoolean = session.get('student')
        iBoolean = session.get('instructor')

        db = get_db()
        db.row_factory = make_dicts

        if sBoolean:
            Sid = query_db("SELECT Sid FROM Student WHERE username = ?", [
                username], one=True)
            sGrades = query_db(
                "SELECT mark, eval FROM Marks WHERE Sid = ?", [Sid['Sid']], one=False)
            name = query_db("SELECT fname FROM Student WHERE username = ?", [
                username], one=True)
            evaluations = query_db("SELECT DISTINCT eval FROM Marks")
            db.close()
            if sGrades is None:
                render_template('grades.html')
            return render_template('grades.html', sGrades=sGrades, user=name['fname'], evaluation=evaluations)
        elif iBoolean:
            Iid = query_db("SELECT Iid FROM Instructor WHERE username = ?", [
                username], one=True)
            name = query_db("SELECT fname FROM Instructor WHERE username = ?", [
                username], one=True)
            evaluations = query_db("SELECT eval, Sid, mark FROM Marks")
            remarks = query_db("SELECT Sid, eval, reason FROM Remark")
            db.close()
            if evaluations is None:
                return render_template('grades.html')
            return render_template('grades.html', user=name['fname'], evaluation=evaluations, remarks=remarks)
    else:
        return redirect(url_for('medium'))


@app.route('/remarkRequest', methods=['POST'])
def remarkRequest():
    if session.get('logged_in') and session.get('student'):
        username = session.get('user')
        assignment = request.form.get('aName')
        reason = request.form.get('reason')

        if (assignment == 'Select an evaluation') or (reason == ''):
            flash('Please select a valid evaluation/enter a valid reason.')
            return redirect(url_for('getGrades'))
        else:
            db = get_db()
            db.row_factory = make_dicts

            Sid = query_db("SELECT Sid FROM Student WHERE username = ?", [
                username], one=True)
            # insert into db
            query_db("INSERT INTO Remark (Sid, reason, eval) VALUES (?, ?, ?)", [
                Sid['Sid'], reason, assignment])
            db.commit()
            db.close()

            flash("Anonymous feedback sent.")
            return redirect("/grades")
    elif session.get('logged_in') and session.get('instructor'):
        username = session.get('user')
        db = get_db()
        db.row_factory = make_dicts
        name = query_db("SELECT fname FROM Instructor WHERE username = ?", [
            username], one=True)
        db.close()
        return redirect("/grades")
    else:
        return redirect(url_for('medium'))


@app.route('/enterGrades', methods=['POST'])
def enterGrades():
    if session.get('logged_in') and session.get('instructor'):
        username = session.get('user')
        stNum = request.form.get('sNum')
        assignment = request.form.get('aName')
        grade = request.form.get('pGrade')

        if (assignment == '') or (stNum == '') or (grade == ''):
            flash('Please ensure all fields have been completed.')
            return redirect(url_for('getGrades'))
        else:
            db = get_db()
            db.row_factory = make_dicts

            Iid = query_db("SELECT Iid FROM Instructor WHERE username = ?", [
                username], one=True)
            name = query_db("SELECT fname FROM Instructor WHERE username = ?", [
                username], one=True)

            # insert into db
            query_db("INSERT INTO Marks (Sid, mark, eval, Iid) VALUES (?, ?, ?, ?)", [
                     int(stNum), float(grade), assignment, Iid['Iid']])
            db.commit()
            db.close()

            flash('Grade added.')
            return redirect("/grades")
    else:
        return redirect(url_for('medium'))


@app.route('/feedbacks')
def showFeedbacks():
    if session.get('logged_in'):
        if session.get('student'):
            username = session.get('user')

            db = get_db()
            db.row_factory = make_dicts
            name = query_db("SELECT fname FROM Student WHERE username = ?", [
                username], one=True)
            iName = query_db("SELECT fname FROM Instructor", one=False)

            return render_template('feedbacks.html', user=name['fname'], iName=iName)
        elif session.get('instructor'):
            username = session.get('user')

            db = get_db()
            db.row_factory = make_dicts
            name = query_db("SELECT fname FROM Instructor WHERE username = ?", [
                username], one=True)
            iFeedback = query_db(
                "SELECT feedback FROM Feedbacks WHERE instructor = ?", [name['fname']], one=False)
            db.close()

            return render_template('feedbacks.html', feedbacks=iFeedback, user=name['fname'])
    else:
        return redirect(url_for('medium'))


@app.route('/feedbackForm', methods=['POST'])
def createFeedbacks():
    if session.get('logged_in'):
        if session.get('student'):
            feedback = request.form['feedback']
            iName = request.form.get('instructorname')

            if (feedback == '') or (iName == 'Select an instructor'):
                flash("Please input a valid feedback/pick a valid instructor.")
                return redirect(url_for("showFeedbacks"))
            else:
                db = get_db()
                db.row_factory = make_dicts

                query_db("INSERT INTO Feedbacks (feedback, instructor) VALUES (?, ?)", [
                    feedback, iName])
                db.commit()
                db.close()

                flash('Anonymous feedback submitted!')
                return redirect(url_for('showFeedbacks'))
    return redirect(url_for('showHome'))


@app.route('/<page>')
def linkPages(page):  # allows you to access other ages on the site
    if session.get('logged_in') and '.html' in page:
        return 'You got caught sneaking around the site. Go back to a valid route (starting with "/")'
    elif not session.get('logged_in') and '.html' in page:
        return 'You got caught sneaking around the site. Please log in and go to a valid route (starting with "/")'


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
