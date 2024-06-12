import pandas as pd
from cnb_sel import cnb_sel
from cnb_sel import twitter_link
from cnb_sel import twitter_utils
from selenium.webdriver.common.by import By
import sqlite3
import scraping_utilities


sqlite_db_file = './db.sqlite'
conn = sqlite3.connect(sqlite_db_file)
xdriver = cnb_sel()

# Get posts for which i want comments
dtPOSTS = pd.read_sql('SELECT DISTINCT TWEET_ID, USERNAME  FROM GATHERED_TWEETS gt JOIN SUBJECT_PROFILE sp ON LOWER(gt.USERNAME) = LOWER(sp.TWITTER_PROFILE) WHERE gt.TWEET_ID NOT IN (SELECT ptp.POST_ID FROM PROCESSED_TW_POSTS ptp) AND gt.IN_REPLY_TO_ID IS NULL AND gt.TWEET_ID NOT IN (SELECT gt2.IN_REPLY_TO_ID FROM GATHERED_TWEETS gt2 WHERE gt2.IN_REPLY_TO_ID IS NOT NULL) AND gt.TWEET_ID NOT IN (SELECT ptp2.POST_ID FROM PROCESSED_TW_POSTS ptp2 WHERE ptp2.POST_ID IS NOT NULL) ORDER BY gt.DATE_TIME DESC LIMIT 30', conn)

while dtPOSTS.shape[0]>0:
    
    dtREPL_all = pd.DataFrame()

    for index, POST in dtPOSTS.iterrows():
        dtREPL = xdriver.get_post_replies(POST['TWEET_ID'], POST['USERNAME'])
        print(f"Fetched {dtREPL.shape[0]} comments.")
        dtREPL_all = pd.concat([dtREPL_all, dtREPL], ignore_index=True)

    if dtREPL_all.shape[0]>0:
        scraping_utilities.append_tweets_to_db(conn, dtREPL_all)
        dtPR = pd.DataFrame({'POST_ID': dtPOSTS['TWEET_ID'].values})
        dtPR['P_DESC'] = 'processed for comments'
        dtPR.to_sql('PROCESSED_TW_POSTS', con=conn, if_exists='append', index=False)
    else:
        print('No comments. Is evertyhing fine or what?')
        break
    print('Written to dob.')
    dtPOSTS = pd.read_sql('SELECT DISTINCT TWEET_ID, USERNAME  FROM GATHERED_TWEETS gt JOIN SUBJECT_PROFILE sp ON LOWER(gt.USERNAME) = LOWER(sp.TWITTER_PROFILE) WHERE gt.TWEET_ID NOT IN (SELECT ptp.POST_ID FROM PROCESSED_TW_POSTS ptp) AND gt.IN_REPLY_TO_ID IS NULL AND gt.TWEET_ID NOT IN (SELECT gt2.IN_REPLY_TO_ID FROM GATHERED_TWEETS gt2 WHERE gt2.IN_REPLY_TO_ID IS NOT NULL) AND gt.TWEET_ID NOT IN (SELECT ptp2.POST_ID FROM PROCESSED_TW_POSTS ptp2 WHERE ptp2.POST_ID IS NOT NULL) ORDER BY gt.DATE_TIME DESC LIMIT 30', conn)




