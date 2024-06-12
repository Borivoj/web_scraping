import json
import pandas as pd
import sqlite3

from cnb_sel import cnb_sel
from scraping_utilities import append_fb_comments_to_db

POSTS_SEL = "SELECT *  FROM BANK_POSTS WHERE SOCIAL_NETWORK ='fb' and C_DATE >= '2022-06-01' and C_DATE <='2023-05-31'"


print('Starting Chrome...')
driver = cnb_sel()

print('Connecting to db...')
sqlite_db_file = '../bank_indentity/db_bi2.sqlite'
conn = sqlite3.connect(sqlite_db_file)

dtPOSTS = pd.read_sql(POSTS_SEL, con=conn)

for index, row in dtPOSTS.iterrows():
    if index < 204:
        continue
    dtCOMMS = driver.get_fcb_post_comments(row['ID'])
    print(dtCOMMS)
    try:
        append_fb_comments_to_db(conn, dtCOMMENTS=dtCOMMS)
    except:
        pass
    print(index)

conn.close()