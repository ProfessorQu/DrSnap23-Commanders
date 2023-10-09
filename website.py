from flask import Flask, render_template
from commanders import get_commanders, get_user
import random

app = Flask(__name__)

if __name__ == '__main__':
    user = get_user()
    commanders = get_commanders(user, limit=2000)

    print("Got all commanders")

@app.route("/")
def index():
    random_commanders = random.sample(commanders, 100)
    return render_template("index.html", len=len(random_commanders), commanders=random_commanders)

app.run(host="0.0.0.0", port=80)