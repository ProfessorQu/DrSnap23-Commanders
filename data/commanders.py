import time
import praw
import sqlite3
import re

def get_connection():
    connection = sqlite3.connect("data/database.db")
    connection.row_factory = sqlite3.Row
    return connection

def create_db():
    connection = get_connection()

    with open("data/schema.sql") as file:
        connection.executescript(file.read())
    
    connection.commit()
    connection.close()

def get_user():
    reddit = praw.Reddit(
        client_id="9aTF-d-qd0g_Vu5Cixig1Q",
        client_secret="FR0EjUMB_54wCyHPK1S8rL2t26j3dA",
        user_agent="DrSnap23-Commanders"
    )

    return reddit.redditor("DrSnap23")

def get_submissions(user, limit):
    return user.submissions.top(limit=limit, time_filter="all")

def add_commander(user, submission, cur):
    title = submission.title

    if "Daily Commander" not in title:
       return 

    search = re.search(r"/ (.*) \(D", title)

    name = search[0][2:-3] if search is not None else "__UNKWOWN__"
    image_url = submission.url
    post_url = submission.shortlink
    is_un = "un-" in title.lower()
    ups = submission.ups

    comments_text = ""

    all_comments = submission.comments
    all_comments.replace_more()
    all_comments = all_comments.list()

    for comment in all_comments:
        if comment.author == user:
            comments_text = comment.body_html
            if len(comments_text) > 500:
                break

    cur.execute(
        "INSERT INTO commanders (name, image_url, post_url, ups, is_un, comments_text) VALUES (?, ?, ?, ?, ?, ?)",
        (name, image_url, post_url, ups, is_un, comments_text)
    )

def save_commanders(limit=100):
    connection = get_connection()
    cur = connection.cursor()

    user = get_user()

    for i, submission in enumerate(get_submissions(user, limit)):
        if i % 100 == 0:
            print(f"Adding commander #{i}...")

        add_commander(user, submission, cur)

        time.sleep(0.01)
    
    print(f"===== Done, got: {i} commanders! ======")

    connection.commit()
    connection.close()

def run_select_query(query):
    connection = get_connection() 
    commanders = connection.execute(query).fetchall()
    connection.close()

    return commanders

def get_commanders(show_un, order, asc):
    query = "SELECT * FROM commanders "

    if show_un != "all":
        query += f"WHERE is_un = {show_un == 'un'} "

    if order is None:
        query += f"ORDER BY ups {'ASC' if asc else 'DESC'}"
    else:
        query += f"ORDER BY {order} {'ASC' if asc else 'DESC'}"

    return run_select_query(query)
    
if __name__ == '__main__' and input("Are you sure? This will delete all data. (yes/no) ").lower() == "yes":
    create_db()

    save_commanders(limit=2000)