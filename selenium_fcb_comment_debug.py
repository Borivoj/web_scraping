import json
import pandas as pd
import sqlite3


from cnb_sel import cnb_sel
from cnb_sel import twitter_link
from cnb_sel import twitter_utils


print('Connecting to db...')
sqlite_db_file = '../bank_indentity/db_bi2.sqlite'
conn = sqlite3.connect(sqlite_db_file)

print('Starting Chrome...')
driver = cnb_sel()

driver.get_fcb_post_comments('639273908225681')

file_path = "output.txt"

# Open the file in write mode ('w')
# If the file does not exist, it will be created. If it exists, its contents will be overwritten.
with open(file_path, 'w') as file:
    # Write the string to the file
    file.write(driver.get_jsons())

jsons = driver.get_jsons()
for json_data in jsons:
    if all(json_element in json_data for json_element in ['text']):
        if 'milá' in json_data['text']:
            #print(json_data)
            a= json_data
            print(json_data['__typename'])
    #if all(json_element in json_data for json_element in ['id', 'body', '__typename', 'author']):
    #    print(json_data['body']['text'])
json_comment_to_pd(a)
is_facebook_comment(a)
driver.xp_sel("//button[@role='button' and descendant::text()[contains(., 'replies')]]")
//*[@id="mount_0_0_U6"]/div/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div/div/div/div/div/div/div/div/div/div/div/div/div[2]/div/div/div[4]/div/div/div[2]/ul/li[4]/div[2]/div/div[2]/div/div[2]
repl_els  = driver.xp_sel("//*[contains(text(), 'replies')]")

repl_els[1].get_attribute("outerHTML")
f=repl_els[1].find_element(By.XPATH,'../..')
f.get_attribute("outerHTML")
f.click()

for repl_el in repl_els:
    if driver.text_regex_pattern.search(repl_el.text):
        try:
            f=repl_el.find_element(By.XPATH,'../..')
            f.click()
            #repl_el.click()
        except:
            try:
                repl_el.click()
            except:
                pass
        
driver.ignore_fb_login()

driver.xp_sel("//*[@data-visualcompletion='ignore']")
a = driver.xp_sel("//*[@Aria-label='Close' and @role='button']")
a[0].click()

import re
text_regex_pattern = re.compile(r'((more)|([0-9]+)) replies') 

button = driver.xp_sel(f"//button[matches(text(), '{button_text_pattern.pattern}')]")

repl_els  = driver.xp_sel("//*[contains(text(), 'replies')]")

for repl_el in repl_els:
    if text_regex_pattern.search(repl_el.text):
        repl_el.click()
        #repl_el.click()
c = a.find_element(By.XPATH, '../..')
c.click()
repl_btn = driver.xp_sel(f"//*[matches(text(), '{text_regex_pattern.pattern}')]")
from selenium.webdriver.common.by import By

a = repl_btn[0].find_element(By.XPATH,"..")

a.click()
#driver = uc.Chrome(options=options)
driver.css_sel()

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