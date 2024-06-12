from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc
import json
import pandas as pd
import sqlite3


print('Connecting to db...')
sqlite_db_file = '../bank_indentity/db.sqlite'
conn = sqlite3.connect(sqlite_db_file)

print('Starting Chrome...')
chromedriver = "/usr/local/bin/chromedriver"
options = Options()
options.binary_location = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'

driver = uc.Chrome(options=options)


def get_json_part(text, root_call = True):
    bracket_counter = 0
    first_ite = True
    out_text_list = []
    out_text = ""
    for char in text:
        if char =='}':
            bracket_counter = bracket_counter - 1
        
        if bracket_counter > 0:
            out_text = out_text + char
        
        if bracket_counter == 0 and first_ite == False:
            out_text_list = out_text_list + get_json_part(out_text, root_call=False)
            out_text = ""
            first_ite = True
        
        if char == '{':
            bracket_counter = bracket_counter + 1
            first_ite = False
    
    if first_ite == True and root_call == False:
        out_text = text
    
    out_text_list = out_text_list + ['{' + out_text + '}']
    
    return(out_text_list)
        
def is_facebook_comment(json_data):
    if all(json_element in json_data for json_element in ['id', 'body', '__typename', 'author']):
        if json_data['__typename'] == 'Comment':
            return(True)
    else:
        return(False)

def json_comment_to_pd(json_comment):
    #dtCOMMENT=pd.DataFrame({'COMMENT_ID': [json_comment['id']], 'TEXT_RAW': [json_comment['body']['text']], 'AUTHOR': [json_comment['author']['name']]})
    dtCOMMENT=pd.DataFrame({'COMMENT_ID': [json_comment['id']], 'TEXT_RAW': [json_comment['body']['text']], 'AUTHOR': [json_comment['author']['name']], 'IS_A_ORIGINAL_POSTER': [json_comment['is_author_original_poster']]})
    
    return(dtCOMMENT)

def allow_cookies(driver):
    driver.find_elements(By.XPATH, '//*[contains(text(), "Allow all cookies")]')[
        -1
    ].click()

dtPOSTS = pd.read_sql("SELECT * FROM FACEBOOK_POST  WHERE POST_ID NOT IN (SELECT POST_ID FROM FACEBOOK_COMMENT UNION ALL SELECT POST_ID FROM PROCESSED_FCB_POSTS) ORDER BY POST_DATE DESC LIMIT 10", con=conn)

while len(dtPOSTS)>0:
    dtCOMMENTS = pd.DataFrame()

    for index, ROW in dtPOSTS.iterrows():
        url_fb = 'https://www.facebook.com/'+ROW['POST_ID']
        driver.get(url_fb)
        try:
            allow_cookies(driver)
        except:
            pass
        page_source = driver.page_source
        json_matches = get_json_part(page_source)
        json_data_list = []
        for json_str in json_matches:
            try:
                parsed_json = json.loads(json_str)
                json_data_list.append(parsed_json)
            except json.JSONDecodeError:
                continue

        for json_data in json_data_list:
            if is_facebook_comment(json_data):
                try:
                    dtNEW_COMMENTS = json_comment_to_pd(json_data)
                    dtNEW_COMMENTS['POST_ID'] = ROW['POST_ID']
                    dtCOMMENTS = pd.concat([dtNEW_COMMENTS, dtCOMMENTS], ignore_index = True)
                except:
                    print(json_data)
                    pass
    
    dtCOMMENTS.to_sql('FACEBOOK_COMMENT',conn, if_exists='append', index=False)
    dtPOSTS[['POST_ID']].to_sql('PROCESSED_FCB_POSTS',conn, if_exists='append', index=False)

    dtPOSTS = pd.read_sql("SELECT * FROM FACEBOOK_POST  WHERE POST_ID NOT IN (SELECT POST_ID FROM FACEBOOK_COMMENT UNION ALL SELECT POST_ID FROM PROCESSED_FCB_POSTS) ORDER BY POST_DATE DESC LIMIT 10", con=conn)

print(dtCOMMENTS[['TEXT_RAW']])

driver.quit()