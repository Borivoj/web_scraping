from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

import undetected_chromedriver as uc

import json

import time
from datetime import datetime
import calendar

import re

import pandas as pd
from bs4 import BeautifulSoup


class twitter_utils:
    def parse_custom_date(date_str):
        current_year = datetime.now().year
        # Split the input date string into parts
        parts = date_str.split()
        day = parts[1]
        day = day.strip(',')
        day = int(day)
        month_name = parts[0]
        month_name = month_name.strip(',')
        
        year = current_year if len(parts) < 3 else int(parts[2])
        month_number = list(calendar.month_abbr).index(month_name.capitalize())
        return datetime(year, month_number, day)

class cnb_sel:
    def __init__(self, chrome_driver = "/usr/local/bin/chromedriver", chrome_binary='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'):
        chromedriver = chrome_driver
        options = Options()
        options.binary_location = chrome_binary
        #self.driver = uc.Chrome(options=options)
        self.driver = webdriver.Chrome(options=options)
        self.page_loading_b = 5
        self.twitter_logged_in = False
        self.text_regex_pattern = re.compile(r'((more)|([0-9]+)) replies') 
        
    def xp_sel(self, X_PATH):
        return(self.driver.find_elements(By.XPATH,X_PATH))
    
    def css_sel(self, CSS_CLASS):
        return(self.driver.find_elements(By.CSS_SELECTOR,CSS_CLASS))
    
    def tag_sel(self,tag_name):
        return(self.driver.find_elements(By.TAG_NAME, tag_name))
    
    def page_source_as(self):
        time.sleep(self.page_loading_b)
        html = self.driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
        return(html)
    
    def twitter_login(self, user_name = 'a.m.rulez@proton.me', twitter_password='MOIS89jxji99j', twitter_user = '@bankingguru666'):    
        self.driver.get('https://twitter.com/login')
        time.sleep(self.page_loading_b*5)
        input_element = self.driver.find_element(By.XPATH,"//input[@autocomplete='username']")
        input_element.send_keys(user_name)
        self.driver.find_elements(By.XPATH, '//*[contains(text(), "Next")]')[
                -1
            ].click()
        time.sleep(self.page_loading_b)
        try:
            #element_del = self.el_xp("//*[contains(text(), 'Phone number or username')]")
            input_element = self.driver.find_element(By.XPATH,"//input[@autocomplete='on']")
            input_element.send_keys(twitter_user)
            self.driver.find_elements(By.XPATH, '//*[contains(text(), "Next")]')[
                    -1
                ].click()
        except:
            pass
        time.sleep(self.page_loading_b)
        
        try:
            input_element = self.driver.find_element(By.XPATH,"//input[@autocomplete='current-password']")
            input_element.send_keys(twitter_password)
            self.driver.find_elements(By.XPATH, '//*[contains(text(), "Log in")]')[
                    -1
                ].click()
            self.twitter_logged_in = True
        except:
            self.twitter_logged_in = False
            print("Failed to login.")
        
    def quit(self):
        self.driver.quit()
        
    def twitter_limit_exceeded(self):
        text_err1 = 'Rate limit exceeded'
        el1 = self.xp_sel(f"//*[contains(text(), '{text_err1}')]")
        
        text_err2 = 'Cannot retrieve Tweets at this time'
        el2 = self.xp_sel(f"//*[contains(text(), '{text_err2}')]")
        text_err3 = 'Something went wrong. Try reloading.'
        el3 = self.xp_sel(f"//*[contains(text(), '{text_err3}')]")
        
        if el1 is not None or el2 is not None or el3 is not None:
            return(True)
        else:
            return(False)
        
    def tw_go_to_post(self, post_id, twitter_user):
        if self.twitter_logged_in == False:
            self.twitter_login()
            time.sleep(self.page_loading_b)
        
        self.driver.get('https://twitter.com/'+twitter_user+'/status/'+post_id)
        
        if self.twitter_limit_exceeded():
            RuntimeError('Twitter rate limit exceede for today')
        
        
        
    def get_post_links(self):
        post_links = []
        a_elements = self.driver.find_elements(By.TAG_NAME, "a")
        for element in a_elements:
            link_full = element.get_attribute("href")
            status_match = re.search(pattern='https:\/\/twitter.com\/([a-z]|[A-Z]|[0-9]|_)+\/status\/[0-9]*$',string=link_full)
            if status_match is not None:
                post_links.append(status_match.group())
        return(list(set(post_links)))
    
    def get_tweet_texts(self):
        tweet_text_elements = self.driver.find_elements(By.XPATH,f"//div[@data-testid='tweetText']")
        tweet_texts = []
        for element in tweet_text_elements:
            tweet_texts.append(element.text)
        return(list(set(tweet_texts)))
    
    def get_post_replies(self, post_id, twitter_user):
        self.tw_go_to_post(post_id=post_id, twitter_user=twitter_user)
        if self.twitter_logged_in == False:
            raise Exception("Must be logged in to get tweet replies.")
        
        time.sleep(self.page_loading_b)
        dtTWEETS = self.replies_on_post_page()
        
        if dtTWEETS.shape[0]>0:
            dtTWEETS = dtTWEETS[dtTWEETS['TWEET_ID'] != post_id]
            dtTWEETS['IN_REPLY_TO_ID'] = post_id
            return(dtTWEETS)
        else:
            print("No replies")
            return(pd.DataFrame())
    
    def replies_on_post_page(self):        
        tweet_text_elements = self.driver.find_elements(By.XPATH,f"//article[@data-testid='tweet']")
        dtTWEETS = pd.DataFrame()
        for tweet_text_element in tweet_text_elements:
            # As of now can proces only replies... Which is a good thing maybe
            string_parts = tweet_text_element.text.split('\n')
            try:
                date_time = twitter_utils.parse_custom_date(string_parts[3])
                #text_raw = string_parts[4]
            except:
                continue
            
            # Process tweet on page
            dtTWEET = pd.DataFrame()
            outer_html = tweet_text_element.get_attribute('outerHTML')
            soup = BeautifulSoup(outer_html, 'lxml')
            a_tags = soup.find_all('a')
            span_tags = soup.find_all('span')
            
            
            for a_tag in a_tags:
                href = a_tag.get('href')
                if href is not None:
                    if twitter_link.is_twitter_post_link(href):
                        lnk = twitter_link(href)
            
            raw_content = tweet_text_element.text
            
            if span_tags[5].text in tweet_text_element.text:
                raw_content = span_tags[5].text
            else:    
                for span_tag in span_tags:
                    if span_tag.text in tweet_text_element.text:
                        raw_content = span_tag.text
                        break
            
            raw_content = raw_content.replace('\n',' ')    
            
            dtTWEET = pd.DataFrame({'DATE_TIME':  [date_time],
                                    'TWEET_ID': [lnk.post_id],
                                    'RAW_CONTENT': [raw_content],
                                    'USERNAME': [lnk.twitter_user]})
            
            dtTWEETS = pd.concat([dtTWEETS, dtTWEET], ignore_index=True)
        return(dtTWEETS)
    
    def get_jsons(self):
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
        page_source = self.driver.page_source
        json_matches = get_json_part(page_source)
        json_data_list = []
        for json_str in json_matches:
            try:
                parsed_json = json.loads(json_str)
                json_data_list.append(parsed_json)
            except json.JSONDecodeError:
                continue
        return(json_data_list)
    
    def allow_cookies(self, cookie_text_button = 'Allow all cookies'):
        self.driver.find_elements(By.XPATH, '//*[contains(text(), "'+cookie_text_button+'")]')[
            -1
        ].click()
    
    def ignore_fb_login(self):
        ign_cross_els = self.xp_sel("//*[@Aria-label='Close' and @role='button']")
        try:
            for ign_cross_el in ign_cross_els:
                try:
                    ign_cross_el.click()
                except:
                    pass
        except:
            pass
    
    def scroll_full_page_down(self):
        scroll_position = 0

        # Define the scroll step size (adjust as needed)
        scroll_step = 500  # Scroll down by 500 pixels each time

        # Loop to scroll down the full page
        while True:
            # Scroll down by the scroll_step
            self.driver.execute_script(f"window.scrollTo(0, {scroll_position});")
            
            # Update the scroll_position
            scroll_position += scroll_step
            
            # Wait briefly to allow content to load (you can adjust the sleep duration)
            time.sleep(1)
            
            # Check if we have reached the bottom of the page
            # You can adjust this condition based on your specific use case
            if scroll_position >= self.driver.execute_script("return Math.max( document.body.scrollHeight, document.body.offsetHeight, document.documentElement.clientHeight, document.documentElement.scrollHeight, document.documentElement.offsetHeight );"):
                break
    
    def try_clicking(self,element):
        try:
            element.click()
        except:
            print('Failed to click this:')
            print(element.get_attribute("outerHTML"))
    
    def expand_replies(self):
        # Tato funkce nejak nefunguje :(
        self.scroll_full_page_down()
        # Open replies
        repl_els  = self.xp_sel("//*[contains(text(), 'replies')]")
        for repl_el in repl_els:
            if self.text_regex_pattern.search(repl_el.text):
                self.try_clicking(repl_el)
                self.try_clicking(repl_el.find_element(By.XPATH,'../..'))
                self.try_clicking(repl_el.find_element(By.XPATH,'..'))
                self.try_clicking(repl_el.find_element(By.XPATH,'../../..'))

    def get_fcb_post_comments(self, post_id):
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
        
        dtCOMMENTS = pd.DataFrame()
        url_fb = 'https://www.facebook.com/'+post_id
        self.driver.get(url_fb)
        try:
            self.allow_cookies()
        except:
            pass
        
        self.ignore_fb_login()
        #self.expand_replies()
        self.scroll_full_page_down()
        
        json_data_list = self.get_jsons()

        for json_data in json_data_list:
            if is_facebook_comment(json_data):
                try:
                    dtNEW_COMMENTS = json_comment_to_pd(json_data)
                    dtNEW_COMMENTS['POST_ID'] = post_id
                    dtCOMMENTS = pd.concat([dtNEW_COMMENTS, dtCOMMENTS], ignore_index = True)
                except:
                    #print(json_data)
                    pass
        return(dtCOMMENTS)
    

class twitter_link:
    def __init__(self, link_text):
        if not twitter_link.is_twitter_post_link(link_text):
            raise ValueError('Not a twitter post link')
        self.text = link_text
        self.post_id = twitter_link.get_post_id_from_link(link_text)
        self.twitter_user = twitter_link.get_user_from_link(link_text)
    
    def is_twitter_post_link(some_text):
        status_match = re.search(pattern='((^https:\/\/twitter.com)|^)\/([a-z]|[A-Z]|[0-9]|_)+\/status\/[0-9]*$',string=some_text)
        if status_match is not None:
            return(True)
        else:
            return(False)
    
    def get_user_from_link(link_text):
        user_match = re.search(pattern='((^https:\/\/twitter.com)|^)\/(.*?)\/status\/[0-9]*$', string=link_text)
        if user_match is not None:
            return(user_match.group(3))
        else:
            return(None)

    def get_post_id_from_link(link_text):
        post_id_match = re.search(pattern='\/([0-9]*?)$', string=link_text)
        if post_id_match is not None:
            return(post_id_match.group(1))
        else:
            return(None)
