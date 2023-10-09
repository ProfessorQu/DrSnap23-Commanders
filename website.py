from flask import Flask, render_template, request
from commanders import get_commanders
import random

app = Flask(__name__)

if __name__ == '__main__':
    commanders = get_commanders()
    commanders.sort(key=lambda com: com['ups'], reverse=True)

@app.route("/", methods=["GET", "POST"])
def index():
    show_un = request.form.get("show_un") != None

    legal_commanders = [commander for commander in commanders if commander['is_un'] == show_un]

    length = min(100, len(legal_commanders))
    random_commanders = legal_commanders[:length]
    # random_commanders = random.sample(legal_commanders, length)

    return render_template(
        "index.html", len=len(random_commanders),
        commanders=random_commanders,
        show_un=show_un
    )

app.run(host="0.0.0.0", port=80)