from flask import Flask, render_template, request, session, redirect, url_for
from data.commanders import Database
import random
import string

app = Flask(__name__)
app.secret_key = "".join(random.choice(string.ascii_letters + string.digits) for _ in range(50))

with Database() as db:
    all_commanders_len = len(db.run_query("SELECT * FROM commanders"))

@app.route("/", methods=["GET", "POST"])
@app.route("/index", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        session['show_un'] = request.form.get("show_un")
        session['order'] = request.form.get("order")
        session['asc'] = request.form.get("asc") == "true"
        session['name'] = request.form.get("name")
        session['comment'] = request.form.get("comment")
    else:
        session['show_un'] = "all"
        session['order'] = "ups"
        session['asc'] = False
        session['name'] = ""
        session['comment'] = ""

    with Database() as db:
        commanders = db.get_commanders(session['show_un'], session['order'], session['asc'], session['name'], session['comment'])

    total_len = len(commanders)

    if 'cur_page' not in session:
        session['cur_page'] = 0

    if request.form.get("back"):
        if session['cur_page'] >= 100:
            session['cur_page'] -= 100
    elif request.form.get("next"):
        if session['cur_page'] <= total_len - 100:
            session['cur_page'] += 100
    elif request.form.get("first"):
        session['cur_page'] = 0
    elif request.form.get("last"):
        session['cur_page'] = (total_len // 100) * 100

    if total_len <= session['cur_page']:
        session['cur_page'] = 0

    page = session['cur_page']

    current_commanders = commanders[page:page+100]

    return render_template(
        "search.html",
        page="search",
        len=len(current_commanders),
        commanders=current_commanders,
        total_len=total_len,
        result_page=page,
        session=session,
    )

@app.route("/random")
def random_commander():
    commander_id = random.randint(0, all_commanders_len-1)
    return redirect(url_for("commander", id=commander_id))

@app.route("/about")
def about():
    return render_template("about.html", page="about")

@app.route("/commander/<id>")
def commander(id):
    with Database() as db:
        commander = db.run_query(f"SELECT * FROM commanders WHERE ID = {id}")

    if len(commander) >= 1:
        return render_template(
            "commander.html",
            commander=commander[0],
        )
    
    return "FAILED"

app.run(host="0.0.0.0", port=80)
