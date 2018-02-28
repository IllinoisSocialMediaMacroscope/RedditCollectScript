# In[1]:

import praw
import csv
import writeToS3 as s3
from os import listdir, remove
from os.path import isfile, join
import pandas as pd

reddit = praw.Reddit(user_agent='collect all data in the subreddit',
                     client_id='your client id', client_secret='your client secret')
subreddits = ['Parenting', 'Mommit', 'kiddiekitchen']

for sub in subreddits:
    files = [f for f in listdir(sub) if isfile(join(sub, f))]

    for f in files:
        df = pd.read_csv(join(sub,f))
        ids = df['id'].dropna().astype('str').tolist()
        folder_id = f[:-4]

        for id in ids:
            submission = reddit.submission(id=id)
            submission.comments.replace_more(limit=None)
            comment_queue = submission.comments[:]  # Seed with top-level
            comments_no_order = [['author','body','created_utc','id','link_id',
                            'parent_id', 'score', 'subreddit_display_name','subreddit_name_prefixed','subreddit_id']]

            while comment_queue:
                comment = comment_queue.pop(0)
                comments_no_order.append([str(comment.author),
                                        comment.body, comment.created_utc, comment.id, comment.link_id,
                                        comment.parent_id, comment.score, comment.subreddit.display_name,
                                        comment.subreddit_name_prefixed, comment.subreddit_id])
                comment_queue.extend(comment.replies)

            # if folder doesnt exist create it

            # save to csv
            with open(id + '.csv', 'w', newline="", encoding='utf-8') as f:
                writer = csv.writer(f, delimiter=',')
                writer.writerows(comments_no_order)

            # push to s3 bucket
            s3.upload('', 'Comment/' + sub + '/' + folder_id + '/', id+'.csv')

            # delete local file
            remove(id + '.csv')
