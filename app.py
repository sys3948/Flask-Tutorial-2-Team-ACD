from flask import Flask, render_template, request, redirect
import pymysql
import sys
sys.path.append('d:/uploadGit/account_info')
import mysql_info as m_info

app = Flask(__name__)

@app.route('/') # 라우트 데코레이터. - 클라이언트에서 보내온 request를 받는 역활. - url 입력하는 행위. 접속할 때
def index():
    #뷰 함수.
    return '''index page''' # 응답 - 화면 뿌려주는거.

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
            return redirect('/')

        return redirect('/login')
    return render_template('login.html')

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


if __name__ == '__main__':
    app.run(debug=True)