# Selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ChromeOptions

# Utils
from decouple import config
import time
import datetime
import calendar
import argparse
import uuid
import re
import requests
from entity_extraction import retrieve_entity
import json
import requests

class Crawler:
    def __init__(self, depth, keep):

        # self.ids = None
        self.depth = depth
        self.delay = keep
        print(f'Scroll Times: {self.depth}')
        print(f'Waiting Time: {self.delay}  secs')
        self.browser = webdriver.Chrome(executable_path=config('CHROMEDRIVER'))
        
    def collect_url(self, url, history_id,page_id):
        self.history_id = history_id
        self.page_id     = page_id
        print(f"Crawling This Url =====> {url} .... with following ids,  ")
        print(f"History Id: {history_id}, Page Id: {page_id} ")


        self.browser.get(url)

        for scroll in range(self.depth):
            self.click_esc_key()
            time.sleep(self.delay) 
            self.click_esc_key()
            time.sleep(self.delay)
            #### Scrolling 
            self.browser.execute_script("window.scrollBy(0, document.body.scrollHeight)")
        self.collect_crawl_posts(self.history_id,self.page_id)

    def collect_crawl_posts(self,history_id,page_id):
        print("\n In collecting crawl Post")
        print(f"With History Id = {history_id} and Page Id={page_id} ")
        posts = self.browser.find_elements_by_class_name("userContentWrapper")

        headers = {
            'Content-Type': "application/json",
            'Accept': "*/*",
            'Cache-Control': "no-cache",
            'Host': config('DIGIZAAY_HOST'),
            'Accept-Encoding': "gzip, deflate",
            'Content-Length': "200",
            'Connection': "keep-alive",
            'cache-control': "no-cache",
            'Authorization':config('TOKEN')
        }

        all_content = []
        for num, post in enumerate(posts):
            date = ''
            timestamp = ''
            print(f'\n--------------------------------IN POST NUMBER {num+1}-------------------------------')
            print('----------------------------------------------------------------------------------------')           
            
            ### Get TimeStamp (to skip the last crawled post in case of some failures during crawling )
            timestamp = ''
            try:
                date_obj = post.find_element_by_css_selector('._5ptz')
                date =  date_obj.get_attribute("title")

                timestamp = date_obj.get_attribute("data-utime")
                timestamp = int(timestamp)
            except Exception as e:
                print("Error retrieving date " + str(e))

            # Check timestamp if the page is already scanned before            
            # if(timestamp < 1576813657):

            ### Comments Included ...So After Expanding comments and clicking See More in Post Text and Comments , Everything will be extracted ###
            if(True):
                # Author Name
                all_content  = []
                entities     = []
                author_name  = ''
                post_text    = ''
                like_count   = 0
                comment_count= 0
                share_count  = 0
               
                # IMAGE URLS
                images =  self.extract_all_images(post)                 ### Before expanding (to avoid scroll up)

                ### Expand More Comments by Clicking View More Comments ###
                self.click_view_more_button(post)

                ### Expand Post Text and Comment Text by Clicking See More ###
                self.click_see_more_button(post)

                # POST TEXT
                try: 
                    post_text = post.find_element_by_class_name('userContent').text
                    post_text = self.remove_emoji(post_text)
                    entities = retrieve_entity(post_text)
                except Exception as e:
                    print('Issue with retrieving content: ' + str(e))

                # AUTHOR
                try:
                    author_name = post.find_element_by_css_selector('.fwb.fcg a').text         
                except Exception as e:
                    print("Error retrieving author name" + str(e))

                # LIKE , COMMENT ,SHARE
                try:
                    like_count = post.find_element_by_class_name("_81hb").text
                    like_count = int(re.search(r'\d+', like_count).group())
                except:
                    like_count = 0
                try:
                    comment_count = post.find_element_by_class_name("_1whp").text
                    comment_count = int(re.search(r'\d+', comment_count).group())
                except:
                    comment_count = 0
                try:
                    share_count = post.find_element_by_class_name("_355t").text
                    share_count = int(re.search(r'\d+', share_count).group())
                except:
                    share_count = 0                           

                # ALL COMMNTS
                # comments = self.extract_all_comments(post)

                print(f"Author Name: {author_name} , Post Date: {date}")
                print(f"Like :{like_count} , Comment :{comment_count} , Share :{share_count} \n")
                # print(f"\nImage Urls..........\n{images}")

                
                dataObj = {
                        'post_detail': post_text,
                        'page_id': page_id,
                        'history_id':history_id,
                        'published_at' : timestamp,
                        'author_name' : author_name,
                        'post_images' : images,                
                        'segmentation' : entities,                
                        'comments_count' : comment_count,
                        'likes_count' : like_count,
                        'shares_count' : share_count
                        # 'post_comments' :comments
                    }

                if post_text is not '':
                    all_content.append(dataObj)
                    data = json.dumps({'crawl_posts': all_content})
                    print(data)
                    # self.sent_to_digi_zaay(data,headers)
                # print(all_content)
    
        try:
            print("End of processing Last Post")
        except Exception as e:
            print("Issue in sending content to digizaay server" + str(e))
    
    def sent_to_digi_zaay(self, data,headers):
        url = config('DIGIZAAY_URL')
        print(f"Send to This Url ===> {url}" )
        print("with following post data\n", data)
        post_car = requests.post(url, data=data, headers=headers)
        print(post_car)                 # 200 => data successfully insert

    def click_esc_key(self):
        return webdriver.ActionChains(self.browser).send_keys(Keys.ESCAPE).perform()

    def click_view_more_button(self, post):
        view_more_counts = 0
        while True:
            try:
                view = post.find_element_by_partial_link_text("View")
                view.send_keys(Keys.RETURN)
                WebDriverWait(self.browser, 3).until(EC.presence_of_element_located((By.CLASS_NAME,"_72vr")))
                view_more_counts +=1
            except:
                break
        print(f"Clicked View More {view_more_counts} time")

    def click_see_more_button(self,post):
        try:
            see_mores = post.find_elements_by_link_text("See more")
            for seemore in see_mores:
                seemore.send_keys(Keys.ENTER)
                time.sleep(1)
        except:
            pass

    def extract_all_images(self,post):
        images = []
        try:                
            # Try clicking on the images
            image_holder = post.find_element_by_class_name('mtm').find_element_by_css_selector('a[rel="theater"]')
            image_holder.click()
            WebDriverWait(self.browser, 2).until(EC.presence_of_element_located((By.CLASS_NAME, "spotlight")))
            
            count = 0
            while(count < 15):  
                     
                try:          
                    spotlight = self.browser.find_element_by_class_name(
                        'spotlight')

                    # print('---------------------------------')                    
                    image_url = spotlight.get_attribute("src")
                    # print(image_url)
                    if image_url in images:
                        pass
                        # print('same image already')
                        # hasMore = False
                    else:
                        images.append(image_url)                                     
                    next_btn = self.browser.find_element_by_css_selector(
                        '.snowliftPager.prev')
                    next_btn.click()
                    count += 1
                except Exception as ex:
                    print("Issue retrieving image"+str(ex))
                    count += 1
                    time.sleep(1)
            self.click_esc_key()
            
                
        except Exception as e:
            # No image holder or images here
            print('Issue retrieving the images: ' + str(e))
            pass
        
        return images

    def extract_all_comments(self,post):
        all_comments = []
        names  = []
        cmts = []
        try:
            comments = post.find_elements_by_class_name("_72vr")
            author = post.find_elements_by_css_selector('a[class = "_6qw4"')
            for no, cmt in enumerate(comments):
                comment = cmt.text
                cmt = re.sub(author[no].text,"",comment,count=1)
                if cmt == "":
                    continue
                try:
                    # print(f'{no:04} : {author[no].text} : {cmt}')
                    names.append(author[no].text)
                    cmts.append(cmt)
                except:
                    pass

            all_comments = list(zip(names, cmts))
        except:
            print("This post has no Comments")

        return all_comments

    def remove_emoji(self, string):
        emoji_pattern = re.compile("["
                                   u"\U0001F600-\U0001F64F"  # emoticons
                                   u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                   u"\U0001F680-\U0001F6FF"  # transport & map symbols
                                   u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                                   u"\U00002702-\U000027B0"
                                   u"\U000024C2-\U0001F251"
                                   "]+", flags=re.UNICODE)
        return emoji_pattern.sub(r'', string)

    def login(self, email, password):
        self.browser.get("https://www.facebook.com")

        emailbox = self.browser.find_element_by_name("email")
        emailbox.clear()
        emailbox.send_keys(email)

        emailbox = self.browser.find_element_by_name("pass")
        emailbox.clear()
        emailbox.send_keys(password)
        
        emailbox.send_keys(Keys.ENTER)

    def close_browser(self):
        return self.browser.close()



