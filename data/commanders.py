import time
import praw
import sqlite3
import re
import json

class Database:
    def __init__(self):
        self.connection = sqlite3.connect("data/database.db")
        self.connection.row_factory = sqlite3.Row
    
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.connection.close()

    def reset(self):
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

    def get_posts(self, user, limit):
        return user.submissions.top(limit=limit, time_filter="all")

    def add_commander(self, user, post, cur):
        title = post.title

        if "Daily Commander" not in title:
            return 

        search = re.search(r"/ (.*) \(D", title)

        name = search[0][2:-3] if search is not None else "__UNKWOWN__"

        post_url = post.shortlink
        is_un = "un-" in title.lower()
        ups = post.ups

        author_comment = ""

        all_comments = post.comments
        all_comments.replace_more()
        all_comments = all_comments.list()

        for comment in all_comments:
            if comment.author == user:
                author_comment = comment.body_html
                if len(author_comment) > 500:
                    break


        image_url = post.url
        if "gallery" in image_url:
            for image in post.media_metadata.items():
                image_url = image[1]["p"][3]["u"]

                cur.execute(
                    "INSERT INTO commanders (name, image_url, post_url, ups, is_un, author_comment) VALUES (?, ?, ?, ?, ?, ?)",
                    (name, image_url, post_url, ups, is_un, author_comment)
                )
        else:
            cur.execute(
                "INSERT INTO commanders (name, image_url, post_url, ups, is_un, author_comment) VALUES (?, ?, ?, ?, ?, ?)",
                (name, image_url, post_url, ups, is_un, author_comment)
            )


    def save_commanders(self, limit=100):
        cur = self.connection.cursor()

        user = self.get_user()

        for i, post in enumerate(self.get_posts(user, limit)):
            if i % 10 == 0:
                print(f"Adding commander #{i}...")

            self.add_commander(user, post, cur)
        
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
        db.reset()
        db.save_commanders(limit=2000)
