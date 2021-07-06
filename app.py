from flask import Flask, render_template, request, redirect, session
from flask.helpers import flash
import pymysql
from datetime import datetime
import sys
sys.path.append('d:/uploadGit/account_info')
import mysql_info as m_info

app = Flask(__name__)

app.config['SECRET_KEY'] = 'hard string key'

@app.route('/') # 라우트 데코레이터. - 클라이언트에서 보내온 request를 받는 역활. - url 입력하는 행위. 접속할 때
def index():
    #뷰 함수.
    conn = pymysql.connect(host='192.168.111.133', port=3306, user=m_info.account_c, passwd=m_info.password_c, database='page')
    cur = conn.cursor()
    cur.execute("select title, writer, stampdate from posts")
    info = cur.fetchall()
    cur.close()
    conn.close()
    print(info)
    for i in info:
        print(i[2])
    return render_template('index.html', info = info) # 응답 - 화면 뿌려주는거.

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        print(request.form.get('email'))
        print(request.form.get('password'))
        conn = pymysql.connect(host='192.168.111.133', port=3306, user=m_info.account_c, passwd=m_info.password_c, database='page')
        cur = conn.cursor()
        cur.execute("select id, username from users where email='%s' and password='%s'" %(request.form.get('email'), request.form.get('password')))
        info = cur.fetchone()
        cur.close()
        conn.close()

        if info:
            print(info)
            session['user'] = info[1]
            return redirect('/')

        return redirect('/login')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/regis', methods=['GET', 'POST'])
def regis():
    if request.method == 'POST':
        conn = pymysql.connect(host='192.168.111.133', port=3306, user=m_info.account_c, passwd=m_info.password_c, database='page')
        cur = conn.cursor()
        cur.execute("insert into users (email, password, username) values('%s', '%s', '%s')" %(request.form.get('email'), request.form.get('password'), request.form.get('username')))
        conn.commit()
        cur.close()
        conn.close()
        return redirect('/login')
    return render_template('regis.html')

@app.route('/body_edit', methods=['GET', 'POST'])
def body_edit():
    if not session.get('user'):
        flash('로그인을 해야합니다.')
        return redirect('/')
    if request.method == 'POST':
        conn = pymysql.connect(host='192.168.111.133', port=3306, user=m_info.account_c, passwd=m_info.password_c, database='page')
        cur = conn.cursor()
        cur.execute("insert into posts(title, body, stampdate, writer) values('%s', '%s', '%s', '%s')" %(request.form.get('title'), request.form.get('body'), datetime.now().strftime('%Y-%m-%d %H:%M'), session.get('user')))
        conn.commit()
        cur.close()
        conn.close()
        return redirect('/')
    return render_template('body_edit.html')

@app.route('/body/<title>')
def body(title):
    conn = pymysql.connect(host='192.168.111.133', port=3306, user=m_info.account_c, passwd=m_info.password_c, database='page')
    try:
        cur = conn.cursor()
        cur.execute("select * from posts where title='%s'" %(title))
        contents = cur.fetchone()
        return render_template('body.html', contents = contents)
        cur.close()
        conn.close()
    except Exception as e:
        cur.close()
        conn.close()
        return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)