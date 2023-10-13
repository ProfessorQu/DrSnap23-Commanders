import time
import praw
import sqlite3
import re
import json

class Database:
    def open(self):
        self.connection = sqlite3.connect("data/database.db")
        self.connection.row_factory = sqlite3.Row

    def close(self):
        self.connection.close()
    
    def __enter__(self):
        self.open()
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
                author_comment = comment.body
                if len(author_comment) > 500:
                    break

        author_comment = re.sub(r"(?:\*\*)(.*?)(?:\*\*)", r"<b>\1</b>", author_comment)
        author_comment = re.sub(r"(?:\*)(.*?)(?:\*)", r"<i>\1</i>", author_comment)
        author_comment = re.sub(r"(?:\[)(.*?)(?:\]\()(.*?)(?:\))", r"<a href=\2>\1</a>", author_comment)
        author_comment = re.sub(r"\n", r"<br>", author_comment)

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
                print(f"Adding commander #{i}...", end="\r")

            self.add_commander(user, post, cur)
            time.sleep(0.1)
        
        print(f"\n===== Done, got: {i} commanders! ======")

        self.connection.commit()

    def run_query(self, query, params=None):
        if params is None:
            params = []

        self.connection.execute(query, params)
        self.connection.commit()

    def run_select_query(self, query):
        return self.connection.execute(query).fetchall()

    def get_commanders(self, show, order, asc, name, comment, com_type, oracle_text, power, toughness):
        query = "SELECT * FROM commanders WHERE ID > -1 "

        if show != "all":
            query += f"AND is_un = {show == 'un'} "        
        if name:
            query += f"AND name LIKE '%{name}%' "
        if comment:
            for word in comment.split(" "):
                query += f"AND author_comment LIKE '%{word}%' "
        if com_type:
            query += f"AND type LIKE '%{com_type}%' "
        if oracle_text:
            for word in oracle_text.split(" "):
                query += f"AND oracle_text LIKE '%{word}%' "
        if power:
            query += f"AND power = {power} "
        if toughness:
            query += f"AND toughness = {toughness} "

        if order is None:
            query += f"ORDER BY ups {'ASC' if asc else 'DESC'}"
        else:
            query += f"ORDER BY {order} {'ASC' if asc else 'DESC'}"

        return self.run_select_query(query)
    
    def update_commander(self, commander_id, inputs):
        is_un = 'is_un' in inputs

        query = "UPDATE commanders SET name = ?, is_un = ?, mana_cost = ?, type = ?, oracle_text = ?, power = ?, toughness = ? WHERE ID = ?"
        params = [
            inputs['name'], is_un, inputs['mana_cost'], inputs['type'],
            inputs['oracle_text'], inputs['power'], inputs['toughness'],
            commander_id
        ]

        self.run_query(query, params)
    
if __name__ == '__main__' and input("Are you sure? This will delete all data. (yes/no) ").lower() == "yes":
    with Database() as db:
        # db.reset()
        # db.save_commanders(limit=None)

        for commander in db.run_select_query("SELECT * FROM commanders"):
            print(commander['image_url'])
            # com_type = commander['type']
            # if com_type == "" or com_type is None:
            #     db.run_query(f"UPDATE commanders SET type = 'Legendary Creature - ' WHERE ID = {commander['id']}")
            # comment = commander['author_comment']
            # comment = re.sub(r"(?:\[)(.*)(?:\]\()(.*?)(?:\))", r"<a href=\2>\1</a>", comment)

            # db.connection.execute(
            #     "UPDATE commanders SET author_comment = ? WHERE ID = ?",
            #     [comment, commander['id']]
            # )

        # db.connection.commit()
