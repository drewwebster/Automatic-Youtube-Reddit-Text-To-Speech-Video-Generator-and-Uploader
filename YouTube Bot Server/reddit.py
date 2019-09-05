import praw
import datetime
from datetime import timezone
import database

reddit = praw.Reddit(client_id='XXXXX',
                     client_secret='XXXXX', password='XXXXX',
                     user_agent='XXXXX', username='XXXXX')

class Submission():
    def __init__(self, subredditid, submission_id, subreddit, permalink, link, title, author, upvotes, downvotes, amountcomments, comments, timecreated, timegathered, visited, alreadyIn):
        self.subredditid = subredditid
        self.subreddit = subreddit
        self.permalink = permalink
        self.submission_id = submission_id
        self.link = link
        self.title = title
        self.author = author
        self.upvotes = upvotes
        self.downvotes = downvotes
        self.amountcomments = amountcomments
        self.comments = comments
        self.timecreated = timecreated
        self.timegathered = timegathered
        self.visited = visited
        self.update = alreadyIn
        pass

class CommentWrapper():
    def __init__(self, author, text, upvotes, subcomments = None):
        self.author = author
        self.text = text
        self.upvotes = upvotes
        self.subcomments = subcomments

def getInfo(subredditname, amount):
    all_scripts = database.getScriptIds()
    subs = []
    subreddit = reddit.subreddit(subredditname)
    hot_subreddit = subreddit.hot(limit=amount)
    for x, submission in enumerate(hot_subreddit):
        alreadyIn = False
        print("%s/%s"%(x + 1, amount))
        if submission.num_comments < 1000:
            print("Too little comments (%s)" % submission.num_comments)
            continue
        if submission.id in [scriptid[1] for scriptid in all_scripts]:
            index = [scriptid[1] for scriptid in all_scripts].index(submission.id)
            if [scriptstatus[2] for scriptstatus in all_scripts][index] == "RAW":
                print("Script already in database, updating old script")
                alreadyIn = True
            else:
                print("Script already complete, skipping")
                continue
        comments = []
        amountReplies = 4
        try:
            for commentThread in range(0, 30, 1):
                try:
                    threadcomments = ()
                    thread = submission.comments[commentThread]
                    text = thread.body
                    author = thread.author.name
                    ups = thread.ups
                    if author is None:
                        author = "deleted"
                    threadcomments = threadcomments + ((author, text, ups),)
                    prevreply = thread
                    for i in range(0, amountReplies, 1):
                        try:
                            reply = list(prevreply.replies)[0]
                            try:
                                text = reply.body
                                author = reply.author.name
                                ups = reply.ups
                                threadcomments = threadcomments + ((author, text, ups),)
                            except AttributeError:
                                continue
                            prevreply = reply
                        except IndexError:
                            continue
                    comments.append(threadcomments)
                except (IndexError, AttributeError):
                    pass
        except Exception:
            print("Error parsing script, skipping")
            continue

        if not alreadyIn:
            print("Submission good to add")
        now = datetime.datetime.now()
        author = str(submission.author)
        time_created = (datetime.datetime.fromtimestamp(submission.created_utc).replace(tzinfo=timezone.utc).strftime("%Y-%m-%d %H:%M:%S"))
        time_gathered = now.strftime('%Y-%m-%d %H:%M:%S')
        newSub = Submission(submission.subreddit_id, submission.id, subredditname, submission.permalink, submission.url, submission.title, author,
                            submission.ups, submission.downs, submission.num_comments, comments, time_created, time_gathered,
                            submission.visited, alreadyIn)
        subs.append(newSub)
    return subs
