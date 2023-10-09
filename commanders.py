import praw

class Commander:
    def __init__(self, name, img_url, post_url, is_un) -> None:
        self.name = name
        self.img_url = img_url
        self.post_url = post_url
        self.is_un = is_un

def get_user():
    reddit = praw.Reddit(
        client_id="9aTF-d-qd0g_Vu5Cixig1Q",
        client_secret="FR0EjUMB_54wCyHPK1S8rL2t26j3dA",
        user_agent="DrSnap23-Commanders"
    )

    return reddit.redditor("DrSnap23")

def get_commanders(user, limit=100):
    submissions = []

    for submission in user.submissions.top(limit=limit, time_filter="all"):
        title = submission.title

        if "Daily Commander" not in title:
            continue

        name = title[title.rfind("/")+2:title.find("(")-1]

        commander = Commander(name, submission.url, submission.shortlink, "un-" in title.lower())
        submissions.append(commander)
    
    return submissions

if __name__ == '__main__':
    user = get_user()
    commanders = get_commanders(user, limit=10)
