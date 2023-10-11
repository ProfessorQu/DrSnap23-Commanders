import time
import praw
import sqlite3
import re

class Database:
    def __init__(self):
        self.connection = sqlite3.connect("data/database.db")
        self.connection.row_factory = sqlite3.Row
    
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.connection.close()

    def create_db(self):
        with open("data/schema.sql") as file:
            self.connection.executescript(file.read())
        
        self.connection.commit()

    def get_user(self):
        reddit = praw.Reddit(
            client_id="9aTF-d-qd0g_Vu5Cixig1Q",
            client_secret="FR0EjUMB_54wCyHPK1S8rL2t26j3dA",
            user_agent="DrSnap23-Commanders"
        )

        return reddit.redditor("DrSnap23")

    def get_submissions(self, user, limit):
        return user.submissions.top(limit=limit, time_filter="all")

    def add_commander(self, user, submission, cur):
        title = submission.title

        if "Daily Commander" not in title:
            return 

        search = re.search(r"/ (.*) \(D", title)

        name = search[0][2:-3] if search is not None else "__UNKWOWN__"
        image_url = submission.url
        post_url = submission.shortlink
        is_un = "un-" in title.lower()
        ups = submission.ups

        author_comment = ""

        all_comments = submission.comments
        all_comments.replace_more()
        all_comments = all_comments.list()

        for comment in all_comments:
            if comment.author == user:
                author_comment = comment.body_html
                if len(author_comment) > 500:
                    break

        cur.execute(
            "INSERT INTO commanders (name, image_url, post_url, ups, is_un, author_comment) VALUES (?, ?, ?, ?, ?, ?)",
            (name, image_url, post_url, ups, is_un, author_comment)
        )

    def save_commanders(self, limit=100):
        cur = self.connection.cursor()

        user = self.get_user()

        for i, submission in enumerate(self.get_submissions(user, limit)):
            if i % 100 == 0:
                print(f"Adding commander #{i}...")

            self.add_commander(user, submission, cur)
        
        print(f"===== Done, got: {i} commanders! ======")

        self.connection.commit()

    def run_query(self, query):
        return self.connection.execute(query).fetchall()

    def get_commanders(self, show_un, order, asc):
        query = "SELECT * FROM commanders "

        if show_un != "all":
            query += f"WHERE is_un = {show_un == 'un'} "

        if order is None:
            query += f"ORDER BY ups {'ASC' if asc else 'DESC'}"
        else:
            query += f"ORDER BY {order} {'ASC' if asc else 'DESC'}"

        return self.run_query(query)
    
    def close(self):
        self.connection.close()
    
if __name__ == '__main__' and input("Are you sure? This will delete all data. (yes/no) ").lower() == "yes":
    with Database() as db:
        db.run_query("ALTER TABLE commanders RENAME COLUMN comments_text to author_comment")
        # db.run_query("SELECT * FROM commanders")
        # db.save_commanders(limit=2000)
