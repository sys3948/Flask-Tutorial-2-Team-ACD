from flask import Flask, render_template, request, redirect, session
from flask.helpers import flash, url_for
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
    return render_template('body_edit.html', body = None)

@app.route('/body_update/<id>', methods=['GET', "POST"])
def body_update(id):
    if not 'id' in session:
        flash('로그인을 해주세요.')
        return redirect('/login')
    conn = pymysql.connect(host='192.168.111.133', port=3306, user=m_info.account_c, passwd=m_info.password_c, database='page')
    cur = conn.cursor()

    if request.method == 'POST':
        cur.execute("update posts set title = '%s', body='%s' where posts_id = %s" %(request.form.get('title'), request.form.get('body'), id))
        conn.commit()
        cur.close()
        conn.close()
        flash('게시글 수정을 했습니다.')
        return redirect('/body/'+id)

    cur.execute("select posts_id, title, body from posts where posts_id = '%s'" %(id))
    body = cur.fetchone()
    cur.close()
    conn.close()
    if session.get('id') != body[0]:
        flash('작성자가 아닙니다.')
        return redirect('/')
    return render_template('body_edit.html', body = body)

@app.route('/body_delete/<id>')
def body_delete(id):
    if not 'id' in session:
        flash('로그인이 되어있지 않습니다. 로그인을 해주세요.')
        return redirect('/login')
    conn = pymysql.connect(host='192.168.111.133', port=3306, user=m_info.account_c, passwd=m_info.password_c, database='page')
    cur = conn.cursor()
    cur.execute("select posts_id, user_id from posts where posts_id = '%s'" %(id))
    posts_info = cur.fetchone()

    if posts_info[1] != session.get('id'):
        cur.close()
        conn.close()
        flash('작성자가 아니여서 글 삭제를 실패하셨습니다.')
        return redirect('/body/' + id)
    
    cur.execute("delete from posts where posts_id = '%s'" %(id)) 
    conn.commit()
    cur.close()
    conn.close()

    flash('글 삭제가 성공했습니다.')
    return redirect('/')

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
        cur.execute("select u.nickname, c.contents, c.stampdate, c.comments_id \
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
    conn.close()
    return redirect('/body/' + id)


@app.route('/comment_update/<id>', methods=['GET', 'POST'])
def comment_update(id):
    if not 'id' in session:
        flash('로그인이 되어있지 않습니다. 로그인을 해주세요.')
        return redirect('/')
    conn = pymysql.connect(host='192.168.111.133', port=3306, user=m_info.account_c, passwd=m_info.password_c, database='page')
    cur = conn.cursor()
    cur.execute("select comments_id, contents, user_id, posts_id from comments where comments_id = '%s'" %(id))
    comment = cur.fetchone()

    if comment[2] != session.get('id'):
        cur.close()
        conn.close()
        flash('댓글 작성자가 아닙니다.')
        return redirect('/body/' + str(comment[3]))

    if request.method == 'POST':
        cur.execute("update comments set contents = '%s' where comments_id = '%s'" %(request.form.get('comment'), id))
        conn.commit()
        cur.close()
        conn.close()
        return redirect('/body/' + str(comment[3]))

    cur.close()
    conn.close()
    return render_template('comment_update.html', comment = comment)


@app.route('/comment_delete/<id>')
def comment_delete(id):
    if not 'id' in session:
        flash('로그인이 되어있지 않습니다. 로그인을 해주세요.')
        return redirect('/')
    conn = pymysql.connect(host='192.168.111.133', port=3306, user=m_info.account_c, passwd=m_info.password_c, database='page')
    cur = conn.cursor()
    cur.execute("select comments_id, contents, user_id, posts_id from comments where comments_id = '%s'" %(id))
    comment = cur.fetchone()

    if comment[2] != session.get('id'):
        cur.close()
        conn.close()
        flash('댓글 작성자가 아닙니다.')
        return redirect('/body/' + str(comment[3]))

    cur.execute("delete from comments where comments_id = '%s'" %(id))
    conn.commit()
    cur.close()
    conn.close()

    return redirect('/body/' + str(comment[3]))


@app.route('/profile')
def profile():
    if not 'id' in session:
        flash('로그인을 해주세요.')
        return redirect('/login')

    conn = pymysql.connect(host='192.168.111.133', port=3306, user=m_info.account_c, passwd=m_info.password_c, database='page')
    cur = conn.cursor()
    cur.execute('select user_id, nickname from users where user_id = "%s"' %(session.get('id')))
    user = cur.fetchone()
    cur.close()
    conn.close()

    return render_template('profile.html', user = user)


@app.route('/change_name', methods=['GET', 'POST'])
def change_name():
    if not 'id' in session:
        flash('로그인을 해주세요.')
        return redirect('/login')

    conn = pymysql.connect(host='192.168.111.133', port=3306, user=m_info.account_c, passwd=m_info.password_c, database='page')
    cur = conn.cursor()
    if request.method == 'POST':
        cur.execute("update users set nickname = '%s' where user_id = '%s'" %(request.form.get('name'), session.get('id')))
        conn.commit()
        cur.close()
        conn.close()
        return redirect('/profile')
    cur.execute('select nickname from users where user_id = "%s"' %(session.get('id')))
    user = cur.fetchone()
    cur.close()
    conn.close()

    return render_template('change_name.html', user = user)


@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if not 'id' in session:
        flash('로그인을 해주세요.')
        return redirect('/login')

    if request.method == 'POST':
        conn = pymysql.connect(host='192.168.111.133', port=3306, user=m_info.account_c, passwd=m_info.password_c, database='page')
        cur = conn.cursor()
        cur.execute('update users set password = "%s" where user_id = "%s"' %(request.form.get('password'), session.get('id')))
        conn.commit()
        cur.close()
        conn.close()
        session.clear()
        return redirect('/login')
    return render_template('change_password.html')


@app.route('/out_user')
def out_user():
    if not 'id' in session:
        flash('로그인을 해주세요.')
        return redirect('/login')

    conn = pymysql.connect(host='192.168.111.133', port=3306, user=m_info.account_c, passwd=m_info.password_c, database='page')
    cur = conn.cursor()
    cur.execute("delete from users where user_id = '%s'" %(session.get('id')))
    conn.commit()
    cur.close()
    conn.close()
    session.clear()

    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)