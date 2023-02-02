import json
from datetime import datetime
import praw

reddit = praw.Reddit(client_id='******',
                     client_secret='******',
                     user_agent='******',
                     username='******',
                     password='******')
                     

subreddit = reddit.subreddit("overlord")
activation_codes = {}

with open("answers.json", "r") as QandA_File:
    activation_codes.clear()
    QandA = json.load(QandA_File)
    for k in QandA["questions_answers"]:
        activation_codes.update({k["question"]: k["answer"]})


class ContinueComments(Exception):
    pass


def stream_the_comments():
    checkedFile = open("checkedIds.json", "r+")
    checkeds = json.loads(checkedFile.read())
    for comment in subreddit.stream.comments():
        '''This code checks if this comment is already checked'''
        try:
            for commentid in checkeds["checkedComments"]:
                if commentid['comment_id'] == comment.id:
                    raise ContinueComments
        except ContinueComments:
            continue

        '''This code stores the comment so activation codes won't be sought again'''

        def append_json(new_data):
            checkeds["checkedComments"].append(new_data)
            checkedFile.seek(0)
            json.dump(checkeds, checkedFile, indent=4)

        element = {
            "comment_id": comment.id,
            "date": str(datetime.fromtimestamp(comment.created_utc)),
        }
        append_json(element)

        '''This code searches for activation codes and if there is one, it answers to the post'''
        answer = ""
        summoned_answers = set()
        for x in activation_codes.items():
            if x[0] in comment.body.lower():
                activation_code_text = ((x[0].replace("{", "")).replace("}", "")).title()
                summoned_answers.add("### Keyword: " + activation_code_text + "\n\n" + x[1])
            else:
                continue

        if len(summoned_answers) > 0:
            sa_index = 1
            for a in summoned_answers:
                answer += a
                if not len(summoned_answers) == sa_index:
                    answer += "\n\n---\n\n"
                sa_index += 1
            summoned_answers.clear()
            # parent = comment.submission
            parent = reddit.comment(comment.parent_id)
            author = comment.author
            final_reply = answer + "\n\n^If ^you ^have ^any ^questions ^or ^problems ^about ^the ^bot, ^please " \
                                   "^contact ^[u/******](https://www.reddit.com/user/******). ^Thank ^you ^for " \
                                   "^summoning ^me, ^[u/" + author.name + "](https://www.reddit.com/user/" + author.name + ")"
            parent.reply(final_reply)


stream_the_comments()
