import sqlite3
from flask import Flask, render_template, request, redirect, session
app = Flask(__name__)

app.secret_key = "sunabaco"

@app.route("/")
def helloworld():
    return "Hello World!"

# @app.route("/<name>")
# def greet(name):
#     return name + "さん こんばんは！"

@app.route("/template")
def template():
    user_name = "Onochang"
    age = 27
    address = "北海道江別市"
    print(user_name)
    return render_template("index.html", name = user_name, age = age, address = address)

@app.route("/weather")
def weather():
    weather = "晴れ"
    return render_template("weather.html", weather = weather)

@app.route("/dbtest")
def dbtest():
    # flasktest.dbに接続
    conn = sqlite3.connect("flasktest.db")
    # データベースの中身を確認する
    c = conn.cursor()
    # SQLを実行する
    c.execute("select name, age, address from users where id = 1")
    # 変数にセレクトしたレコードのデータを格納
    user_info = c.fetchone()
    print(user_info)
    # データベースの接続を終了する
    c.close()
    return render_template("dbtest.html", user_info = user_info)

# タスクの入力ページを取得するためのルーティング
@app.route("/add", methods=["GET"])
def add_get():
    if "user_id" in session:
        return render_template("add.html")
    else:
        return redirect("/login")

# 入力したタスクをデータベースに追加するためのルーティング
@app.route("/add", methods=["POST"])
def add_post():
    if "user_id" in session:
        user_id = session["user_id"][0]
        # 入力フォームから値を取得する。
        task = request.form.get("task")
        print(task)
        # データベースに接続
        conn = sqlite3.connect("flasktest.db")
        # データベースを操作できるようにする
        c = conn.cursor()
        # SQLを実行してCREATEする
        c.execute("insert into task values (null, ?, ?)", (task, user_id))
        # データベースの変更を保存する
        conn.commit()
        # データベースの接続を終了する。
        c.close()
        return redirect("/list")
    else:
        return redirect("/login")

@app.route("/list")
def task_list():
    if "user_id" in session:
        # セッションからユーザー情報を取得
        user_id = session["user_id"][0]
        conn = sqlite3.connect("flasktest.db")
        c = conn.cursor()
        # ログインユーザーの名前を取得
        c.execute("select name from user where id = ?", (user_id,))
        user_name = c.fetchone()[0]
        # タスク一覧をREADする
        c.execute("select id, task from task where user_id = ?", (user_id,))
        task_list = []
        # for 変数 in 配列
        for row in c.fetchall():
            print("----------")
            print(row)
            print("----------")
            task_list.append({"id": row[0], "task": row[1]})
        c.close()
        print(task_list)
        return render_template("task_list.html", task_list = task_list, user_name = user_name)
    else:
        return redirect("/login")

@app.route("/edit/<int:id>")
def edit(id):
    if "user_id" in session:
        conn = sqlite3.connect("flasktest.db")
        c = conn.cursor()
        c.execute("select task from task where id = ?", (id,))
        task = c.fetchone()
        c.close()
        # もしタスクがあれば
        if task is not None: 
            print(task)
            task = task[0]
        # もしタスクがなければ
        else:
            return "タスクがありません"

        item = {"id": id, "task": task}
        return render_template("edit.html", task = item)
    else:
        return redirect("/login")

@app.route("/edit", methods=["POST"])
def update_task():
    if "user_id" in session:
        # 編集対象のidを取得
        item_id = request.form.get("task_id")
        item_id = int(item_id)
        # 編集された内容
        task = request.form.get("task")

        conn = sqlite3.connect("flasktest.db")
        c = conn.cursor()
        c.execute("update task set task = ? where id = ?", (task, item_id))
        conn.commit()
        c.close()
        return redirect("/list")
    else:
        return redirect("/login")

@app.route("/del/<int:id>")
def del_task(id):
    if "user_id" in session:
        conn = sqlite3.connect("flasktest.db")
        c = conn.cursor()
        c.execute("delete from task where id = ?", (id,))
        conn.commit()
        c.close()
        return redirect("/list")
    else:
        return redirect("/login")

@app.route("/regist", methods=["GET"])
def regist_get():
    if "user_id" in session:
        return redirect("/list")
    else:
        return render_template("regist.html")

@app.route("/regist", methods=["POST"])
def regist_post():
    name = request.form.get("name")
    password = request.form.get("password")

    conn = sqlite3.connect("flasktest.db")
    c = conn.cursor()
    c.execute("insert into user values(null, ?, ?)", (name, password))
    conn.commit()
    c.close()
    return redirect("/login")

@app.route("/login", methods=["GET"])
def login_get():
    if "user_id" in session:
        return redirect("/list")
    else:
        return render_template("login.html")

@app.route("/login", methods=["POST"])
def login_post():
    name = request.form.get("name")
    password = request.form.get("password")

    conn = sqlite3.connect("flasktest.db")
    c = conn.cursor()
    c.execute("select id from user where name = ? and password = ?", (name, password))
    user_id = c.fetchone()
    c.close()

    if user_id is None:
        return render_template("login.html")
    else:
        # ログインが成功した時にセッションを発行する。
        session["user_id"] = user_id
        return redirect("/list")

@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect("/login")


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

if __name__ == "__main__":
    app.run(debug=True)