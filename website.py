from flask import Flask, render_template, request
from data.commanders import get_commanders
import random

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    show_un = request.form.get("show_un")
    order = request.form.get("order")
    asc = request.form.get("asc") == "true"

    commanders = get_commanders(show_un, order, asc)

    length = min(100, len(commanders))
    current_commanders = commanders[:length]

    return render_template(
        "index.html", len=len(current_commanders),
        commanders=current_commanders,
        show_un=show_un,
        order=order,
        asc=asc
    )

app.run(host="0.0.0.0", port=80)