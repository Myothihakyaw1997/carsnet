import json
import time
import requests
import datetime
import argparse
from decouple import config
from crawler import Crawler

start_time = time.time()                          ### Crawler Starts Time

parser = argparse.ArgumentParser(description="-d For scroll times and -k for waiting time after each scroll")

parser.add_argument("-d", "--depth", type=int, default=2, metavar="", help="Numbers of scroll")

parser.add_argument("-k", "--keep", type=int, default=5, metavar="", help="Seconds you want to delay after scroll")

args = parser.parse_args()

###### CRAWLER DASHBOARD ######

if __name__ == '__main__':

    #####  GET pages APi 

    headers = {
                'Content-Type': "application/json",
                'Accept': "*/*",
                'Cache-Control': "no-cache",
                'Host': 'crawler-dev.digi-zaay.com.mm',
                'Accept-Encoding': "gzip, deflate",
                'Content-Length': "100",
                'Connection': "keep-alive",
                'cache-control': "no-cache",
                'Authorization':config('TOKEN')
            }
    all_pages_url = config('ALL_PAGES_URL')
    get_page = requests.get(all_pages_url, headers = headers )
    page_data = get_page.json()                            ### Formatted to Python data type (e.g None)
    # print(page_data)
    # print(json.dumps(page_data, indent=2))               ### Formatted to JSON data type   (e.g null)
    
### Extract,Check  Page ids and Schedule ids From page Data  and Insert to Page and Schedule Tables ###

    weekday = datetime.datetime.today().weekday()
    if weekday== 6:                   ## Sunday is 6 in python
        weekday = 0
    else:
        weekday = weekday + 1

    timestamp = time.strftime('%H:%M:%S')
    print(time)
    ts = time.gmtime()
    crawl_day = time.strftime("%Y-%m-%d %H:%M:%S", ts)
    today_schedules = []

    print('\n----------------------------Active Page Urls--------------------------------')

    for page in page_data:
        # print(page['schedules'])    
        # print(page["url"])

        if page['is_active'] == 1 and len(page['schedules']) > 0:
            for item in page['schedules']:
                print(f'{page["url"]:80} on Weekday :{item["day"]} and Start Time :{item["time"]}')
                
                ### Check WeekDay Here , If matches, append it to today_schedules
                if item['day'] == weekday or item['day'] == 7:
                    item['url']  = page['url']
                    today_schedules.append(item)

    today_schedules= sorted(today_schedules, key = lambda i: int(i['time'].replace(':','')))
    print('\n')
    print('------------------This Schedules Will Be Crawled Today-------------------')
    print(today_schedules)
    

    ### Program Will Start Every 1 Hour Interval ###
    current_time = time.strftime('%H:%M:%S')
    current_hour, current_min, current_sec = current_time.split(':')

    start_hour = int(current_hour)
    # start_min  = int(current_min)
    start_min = 0

    end_hour = start_hour + 1
    end_min = 60

    
    #### Crawl page or groups according to Urls if the start time falls between each 1 hour interval ##
    for page_schedule in today_schedules:
        print("Starting Browser For A Page")
        p = Crawler(args.depth, args.keep)
        crawl_hour, crawl_min, crawl_sec = page_schedule['time'].split(':')
        # print(page_schedule ['time'])


        # if (start_hour <= int(crawl_hour)  <= end_hour) and  (start_min <= int(crawl_min) <= end_min):

        if True:
            page_start = {}
            page_end = {}
            ### Login into Facebook Account
            p.login(config('EMAIL'), config('PASSWORD'))
            crawl_page_url =  page_schedule['url']
            page_id = page_schedule['crawl_page_id']
            
        ## Sends Api Response                                                
            page_start['crawl_page_id'] = page_id
            page_start['start_at']      = current_time

            start_crawl_url = config('HISTORY_URL')
            start_crawl_data = json.dumps(page_start)

            print('\nSending Post_Start_Crawling Api\n')
            start_crawl_post = requests.post(start_crawl_url, data=start_crawl_data, headers=headers)
            print('Response From POST start crawl api')

        ### Insert to History Table Every Time This Api is Called ###
            history_data  = json.loads(start_crawl_post.text)
            history_id = history_data['id']
            print(json.dumps(history_data, indent=2))  
        ## End of Start Crawl Api


        ### Starts to Crawl Page From Url ###
            
            print(f'\nThis URL will be crawled Starting on {current_hour} hours and {current_min} mins ')

            # Call crawl Function and  sends data to Server ##
                              
            p.collect_url(crawl_page_url, history_id, page_id)

        ### End of call Function            ###

            end_time = time.strftime('%H:%M:%S')
            page_end['end_at']        = end_time
            end_crawl_data = json.dumps(page_end)
            print('\nSending Put_End_Crawling Api\n')

            end_crawl_url = config('HISTORY_URL')+'/'+str(history_id)
            end_crawl_put = requests.put(end_crawl_url, data= end_crawl_data, headers = headers)
            
            print("Response From Put end crawl Api")
            print(end_crawl_put.text)
    
        p.close_browser()
        print("Sleep 10 Secs After Closing Browser For a Page\n\n")
        time.sleep(10)

days = 0
total_secs = int(time.time() - start_time)
if total_secs >= 86400:
    days = int(total_secs / 86400)
    secs = total_secs % 86400
else:
    seconds = total_secs

hrs, mins, secs = str(datetime.timedelta(seconds = seconds)).split(':')
print("\n-------------------------------------------------------------------")
print(f'Finished in {days} day, {hrs} hours , {mins} minutes and {secs}  seconds')