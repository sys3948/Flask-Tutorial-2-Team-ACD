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
    cur.execute("select p.posts_id, p.title, p.stampdate, u.nickname \
                 from posts p join users u \
                 on p.user_id = u.user_id")
    info = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('index.html', info = info) # 응답 - 화면 뿌려주는거.

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        conn = pymysql.connect(host='192.168.111.133', port=3306, user=m_info.account_c, passwd=m_info.password_c, database='page')
        cur = conn.cursor()
        cur.execute("select user_id from users where email='%s' and password='%s'" %(request.form.get('email'), request.form.get('password')))
        info = cur.fetchone()
        cur.close()
        conn.close()

        if info:
            print(info)
            session['id'] = info[0]
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
        cur.execute("insert into users (email, password, nickname) values('%s', '%s', '%s')" %(request.form.get('email'), request.form.get('password'), request.form.get('username')))
        conn.commit()
        cur.close()
        conn.close()
        return redirect('/login')
    return render_template('regis.html')

@app.route('/body_edit', methods=['GET', 'POST'])
def body_edit():
    if not session.get('id'):
        flash('로그인을 해야합니다.')
        return redirect('/')
    if request.method == 'POST':
        conn = pymysql.connect(host='192.168.111.133', port=3306, user=m_info.account_c, passwd=m_info.password_c, database='page')
        cur = conn.cursor()
        cur.execute("insert into posts(title, body, stampdate, user_id) values('%s', '%s', '%s', '%s')" %(request.form.get('title'), request.form.get('body'), datetime.now().strftime('%Y-%m-%d %H:%M'), session.get('id')))
        conn.commit()
        cur.close()
        conn.close()
        return redirect('/')
    return render_template('body_edit.html')

@app.route('/body/<id>')
def body(id):
    conn = pymysql.connect(host='192.168.111.133', port=3306, user=m_info.account_c, passwd=m_info.password_c, database='page')
    cur = conn.cursor()
    try:
        cur.execute("select p.title, p.body, p.stampdate, u.nickname \
                     from posts p join users u \
                     on p.user_id = u.user_id \
                     where p.posts_id = '%s'" %(id))
        contents = cur.fetchone()
        cur.execute("select u.nickname, c.contents, c.stampdate \
                     from comments c join users u \
                     on c.user_id = u.user_id \
                     where c.posts_id = '%s'" %(id))
        comments = cur.fetchall()
        cur.close()
        conn.close()
        return render_template('body.html', contents = contents, comments = comments, id = id)
    except Exception as e:
        print(e)
        cur.close()
        conn.close()
        return redirect('/')

@app.route('/comment/<id>', methods=['POST'])
def comment(id):
    if not session.get('id'):
        return redirect('/body/' + id)
    conn = pymysql.connect(host='192.168.111.133', port=3306, user=m_info.account_c, passwd=m_info.password_c, database='page')
    cur = conn.cursor()
    cur.execute("insert into comments(contents, stampdate, user_id, posts_id) values('%s', '%s', '%s', '%s')" %(request.form.get('comment'), datetime.now().strftime('%Y-%m-%d %H:%M'), session.get('id'), id))
    conn.commit()
    cur.close()
    conn.commit()
    return redirect('/body/' + id)


if __name__ == '__main__':
    app.run(debug=True)