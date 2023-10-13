from flask import Flask, render_template, request, session, redirect, url_for
from data.commanders import Database
import random
import secrets
import logging

app = Flask(__name__)
app.secret_key = secrets.token_hex()

logger = logging.getLogger("werkzeug")
logger.setLevel(logging.ERROR)

COMMANDERS_PER_PAGE = 30

with Database() as db:
    all_commanders_len = len(db.run_select_query("SELECT * FROM commanders"))

@app.route("/", methods=["GET", "POST"])
@app.route("/index", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        session['show'] = request.form.get("show")
        session['order'] = request.form.get("order")
        session['asc'] = request.form.get("asc") == "true"
        session['name'] = request.form.get("name")
        session['comment'] = request.form.get("comment")
        session['type'] = request.form.get("type")
        session['oracle_text'] = request.form.get("oracle_text")
        session['power'] = request.form.get("power")
        session['toughness'] = request.form.get("toughness")
    else:
        session['show'] = "all"
        session['order'] = "ups"
        session['asc'] = False
        session['name'] = ""
        session['comment'] = ""
        session['type'] = ""
        session['oracle_text'] = ""
        session['power'] = ""
        session['toughness'] = ""

    with Database() as db:
        commanders = db.get_commanders(
            session['show'], session['order'], session['asc'],
            session['name'], session['comment'], session['type'],
            session['oracle_text'],
            session['power'], session['toughness']
        )

    total_len = len(commanders)

    if 'cur_page' not in session:
        session['cur_page'] = 0

    if request.form.get("back"):
        if session['cur_page'] >= COMMANDERS_PER_PAGE:
            session['cur_page'] -= COMMANDERS_PER_PAGE
    elif request.form.get("next"):
        if session['cur_page'] <= total_len - COMMANDERS_PER_PAGE:
            session['cur_page'] += COMMANDERS_PER_PAGE
    elif request.form.get("first"):
        session['cur_page'] = 0
    elif request.form.get("last"):
        session['cur_page'] = (total_len // COMMANDERS_PER_PAGE) * COMMANDERS_PER_PAGE

    if total_len <= session['cur_page']:
        session['cur_page'] = 0

    page = session['cur_page']

    current_commanders = commanders[page:page+COMMANDERS_PER_PAGE]

    return render_template(
        "search.html",
        page="search",
        len=len(current_commanders),
        commanders=current_commanders,
        total_len=total_len,
        result_page=page,
        session=session,
        commanders_per_page=COMMANDERS_PER_PAGE
    )

@app.route("/random")
def random_commander():
    commander_id = random.randint(0, all_commanders_len-1)
    return redirect(url_for("commander", commander_id=commander_id))

@app.route("/about")
def about():
    return render_template("about.html", page="about")

@app.route("/commander/<commander_id>", methods=["GET", "POST"])
def commander(commander_id):
    with Database() as db:
        if request.method == "POST":
            db.update_commander(commander_id, request.form.to_dict())

        commanders = db.run_select_query(f"SELECT * FROM commanders WHERE ID = {commander_id}")

    if len(commanders) >= 1:
        commander = dict(commanders[0])
        for key in commander:
            if commander[key] is None:
                commander[key] = ""

        return render_template(
            "commander.html",
            commander=commander,
        )

    return "FAILED"

app.run(host="0.0.0.0", port=4321)
