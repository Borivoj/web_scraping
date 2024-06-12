import pandas

def append_fb_posts_to_db(conn, dtPOSTS):
    existing_ids = pandas.read_sql_query("SELECT POST_ID FROM FACEBOOK_POST", conn)
    dtPOSTS_n = dtPOSTS[~dtPOSTS['POST_ID'].isin(existing_ids['POST_ID'])]
    dtPOSTS_n.to_sql('FACEBOOK_POST', conn, if_exists='append', index=False)
    conn.commit()

def append_fb_comments_to_db(conn, dtCOMMENTS):
    existing_ids = pandas.read_sql_query("SELECT COMMENT_ID FROM FACEBOOK_COMMENT", conn)
    dtCOMMENTS_n = dtCOMMENTS[~dtCOMMENTS['COMMENT_ID'].isin(existing_ids['COMMENT_ID'])]
    n_to_add = len(dtCOMMENTS)
    n_to_added = len(dtCOMMENTS_n)
    print(f"Data frame contains {n_to_add} comments of which {n_to_added} are new ones beeing added to db.")
    dtCOMMENTS_n.to_sql('FACEBOOK_COMMENT', conn, if_exists='append', index=False)
    conn.commit()

def append_tweets_to_db(conn, dtTWEETS):
    existing_ids = pandas.read_sql_query("SELECT TWEET_ID FROM GATHERED_TWEETS", conn)
    dtTWEETS_n = dtTWEETS[~dtTWEETS['TWEET_ID'].isin(existing_ids['TWEET_ID'])]
    dtTWEETS_n.to_sql('GATHERED_TWEETS', conn, if_exists='append', index=False)
    conn.commit()
