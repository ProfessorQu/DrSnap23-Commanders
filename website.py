from flask import Flask, render_template, request, session
from data.commanders import get_commanders
import random
import string

app = Flask(__name__)
app.secret_key = "".join(random.choice(string.ascii_letters + string.digits) for _ in range(50))


@app.route("/", methods=["GET", "POST"])
def index():
    session['show_un'] = request.form.get("show_un")
    session['order'] = request.form.get("order")
    session['asc'] = request.form.get("asc") == "true"

    commanders = get_commanders(session['show_un'], session['order'], session['asc'])
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
        "index.html",
        len=len(current_commanders),
        commanders=current_commanders,
        total_len=total_len,
        page=page,
        show_un=session['show_un'],
        order=session['order'],
        asc=session['asc']
    )

app.run(host="0.0.0.0", port=80)