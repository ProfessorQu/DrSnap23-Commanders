from flask import Flask, render_template, request
from data.commanders import run_select_query
import random

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    show_un = request.form.get("show_un") != None

    commanders = run_select_query(
        f"""
        SELECT * FROM commanders
        WHERE is_un = {show_un}
        ORDER BY ups DESC
        """
    )

    length = min(100, len(commanders))
    current_commanders = commanders[:length]

    return render_template(
        "index.html", len=len(current_commanders),
        commanders=current_commanders,
        show_un=show_un
    )

app.run(host="0.0.0.0", port=80)