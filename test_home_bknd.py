from flask import Flask, render_template, session,redirect,request,flash
import pymysql
import random
import bcrypt

app = Flask(__name__)
app.config['SECRET_KEY'] = 'heyhowsitgoing'

def get_db_connection():
    return pymysql.connect(
        host = "localhost",
        user = "root",
        password = "12345",
        database = "club_proj"
    )

@app.route('/signup',methods = ['GET','POST'])
def signup():
    if request.method == 'POST':
        f_name = request.form['f_name']
        m_name = request.form['m_name']
        l_name = request.form['l_name']
        email = request.form['email']
        batch = request.form['batch']
        dob = request.form['dob']
        status = request.form['status']
        age = request.form['age']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash("Passwords do not match. Please try again.", 'error')
            return redirect('/signup')
        
        #hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())


        connection = get_db_connection()
        cursor  = connection.cursor()

        tmp_sid = random.randint(1,100)
        cursor.execute('''
        INSERT INTO student (sid,f_name, m_name, l_name, email, batch, dob, status, age, password)
            VALUES (%s,%s, %s, %s, %s, %s, %s, %s, %s,%s)
        ''', (tmp_sid,f_name, m_name, l_name, email, batch, dob, status, age,password))

        connection.commit()
        flash("You have successfully signed up!", 'success')
        cursor.close()
        connection.close()

        return redirect('/login_tmp')
    return render_template('signup_tmp.html')

@app.route('/home')
def home():
    student_sid = session.get('sid')
    if not student_sid:
        return redirect('/login_tmp')
    
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute('''
                   select c.club_id,c.clubname,st.team_id
                   from clubs c
                   join student_team st on c.club_id = st.club_id
                   where st.student_id = %s
                   ''',(student_sid,))
    

    data = cursor.fetchall()

    club_teams = {}
    if data:
        for da in data:
            club_teams[da[1]] = []
            club_teams[da[1]].append(da[2])

    #so club_teams is gonna look like : {"arc":[team1,team2]}
    cursor.execute('''
                   select f_name,m_name,l_name,email
                   from student 
                   where sid = %s
                   ''',(student_sid,))

    student = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template('home.html', student = student, clubs = data)#also add, team_data = club_teams.

@app.route('/login_tmp',methods = ['GET','POST'])  
def login_tmp():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute('SELECT sid,password FROM student WHERE email = %s', (email,))
        user = cursor.fetchone()

        if user:
            stored_sid, stored_pw = user

            if password == stored_pw:
                session['sid'] = stored_sid
                flash("login successful",'success')
                return redirect('/home')

            else:
                flash("Invalid password. Please try again later",'error')
        else:
            flash("Invalid email",'error')
        
        cursor.close()
        connection.close()

    return render_template('login_tmp.html')
        
if __name__ == "__main__":
    app.run(debug = True)


        





