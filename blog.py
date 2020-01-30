# -*- coding: utf-8 -*-
import time
from time import gmtime
import datetime
from datetime import timedelta
import os
import requests
import random
import sys
import signal
import argparse
from bs4 import BeautifulSoup
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.blocking import BlockingScheduler

my_headers = [
    "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:30.0) Gecko/20100101 Firefox/30.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/537.75.14",
    "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Win64; x64; Trident/6.0)",
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11',
    'Opera/9.25 (Windows NT 5.1; U; en)',
    'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',
    'Mozilla/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.5 (like Gecko) (Kubuntu)',
    'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.0.12) Gecko/20070731 Ubuntu/dapper-security Firefox/1.5.0.12',
    'Lynx/2.8.5rel.1 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/1.2.9',
    "Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.7 (KHTML, like Gecko) Ubuntu/11.04 Chromium/16.0.912.77 Chrome/16.0.912.77 Safari/535.7",
    "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:10.0) Gecko/20100101 Firefox/10.0 "
]


def download_img(url, filename, dest_path):
    if url.startswith("http://dcimg"):
    	s = requests.session()
    	headers = {
			"User-Agent": random.choice(my_headers),
			"Host": "dcimg.awalker.jp",
			"Upgrade-Insecure-Requests": "1"
		}
    	response = s.get(url, headers=headers)
    	pic_url = url.replace("jp/v/", "jp/i/")
    	pic_res = s.get(pic_url, headers=headers)
    	print(filename)
    	output_path = "{}{}{}".format(dest_path, os.sep, filename)
    	if not os.path.exists(output_path):
            if not os.path.isdir(dest_path):
                os.makedirs(dest_path)
            with open(output_path, "wb") as f:
                f.write(pic_res.content)
    	else:
            print('{}: File exist'.format(filename))
    else:
    	download_file(url, filename, dest_path)

def download_file(url, filename, dest_path):
    req = requests.get(url, stream=True, headers={'User-Agent': random.choice(my_headers)})
    if req.status_code == 200:
        total_length = req.headers.get('content-length')
        dl_progress = 0
        if not os.path.isdir(dest_path):
        	os.makedirs(dest_path)
        output_path = "{}{}{}".format(dest_path, os.sep, filename)
        if not os.path.exists(output_path):
            with open(output_path, 'wb') as o_file:
                for chunk in req.iter_content(1024):
                    dl_progress += len(chunk)
                    o_file.write(chunk)
                    # Download progress report
                    percent = dl_progress / int(total_length)
                    sys.stdout.write("\r{}: {:.2%}".format(filename, percent))
                    sys.stdout.flush()

            print('')
        else:
            print('{}: File exist'.format(filename))
    else:
        print('Visit website fail')

def get_blog_img_json(start_time):
    pic_dict = {}
    date_format = "%Y%m%d"
    start_date = datetime.datetime.strptime("%d" % start_time, date_format)
    end_date = datetime.datetime.now()
    while True:
        if start_date > end_date:
            return pic_dict
        start_time = int(start_date.strftime("%Y%m%d"))
        url = "http://blog.nogizaka46.com/?d=%d" % start_time
        req = requests.get(url, stream=True, headers={'User-Agent': random.choice(my_headers)})
        soup = BeautifulSoup(req.text, 'html.parser')

        page = 1
        paginates = soup.select("div.paginate")
        if paginates:
            a = paginates[0].find_all("a")
            href = a[-2].get("href")
            page = int(href[3])
        
        for p in range(page):
            print(start_date)
            if p > 0:
                url = "http://blog.nogizaka46.com/?p=%d&d=%d" % (p + 1, start_time)
                req = requests.get(url, stream=True, headers={'User-Agent': random.choice(my_headers)})
                soup = BeautifulSoup(req.text, 'html.parser')
            titles = soup.select('h1.clearfix')
            entrybodys = soup.select("div.entrybody")

            for index, title in enumerate(titles):
                yearmonth = title.find("span", class_="yearmonth")
                daydate = title.find("span", class_="dd1")
                author = title.find("span", class_="author")
                file_name = yearmonth.text[2:].replace("/", "")
                file_name += daydate.text

                author_name = author.text
                if author_name == u"４期生":
                    entrytitle = title.find("span", class_="entrytitle").find("a")
                    author_name = entrytitle.text.split(" ")[-1]
                    if len(author_name) > 5:
                        author_name = author_name[-5:]
                    if author_name == u"遥香":
                        author_name = u"賀喜 遥香"
                file_name += "_" + author_name.replace("*", "").replace(")", "").replace("/", "").replace("？", "").replace("！", "").replace("　", "")
                
                entrybody = entrybodys[index]
                links = [link for link in entrybody.find_all("img") if link and link.get("src")]
                for link in links:
                    src = link.get("src")
                    if link.parent and link.parent.name == "a":
                        src = link.parent.get("href")
                    if not pic_dict.get(file_name):
                        pic_dict[file_name] = []
                    pic_dict[file_name].append(src)
        start_date += timedelta(days=1)
    return ""

def job(start_time):
    img_json = get_blog_img_json(start_time)
    for key, urls in img_json.items():
        for index, url in enumerate(urls):
            print(url)
            ext = url.split(".")[-1]
            if url.startswith("http://dcimg.awalker.jp/v/"):
                ext = "jpeg"
            file_name = "%s%d.%s" % (key, index, ext)
            if not url.startswith("http"):
                continue
            try:
                download_img(url, file_name, "C:\\Users\\Kappa\\Downloads\\blog1")
            except:
                print(url)
    print("Download complete")

def signal_handler(sig, frame):
    sys.exit(0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Download blog photos.')
    parser.add_argument('hour', type=str, nargs='?', help='hour')
    parser.add_argument('minute', type=str, nargs='?', help='minute')
    parser.add_argument('second', type=str, nargs='?', help='second')
    parser.add_argument('time', type=int, nargs='?', help='Blog Time')
    signal.signal(signal.SIGINT, signal_handler)
    args = parser.parse_args()
    job(args.time)
    # scheduler = BlockingScheduler()
    # scheduler.add_job(job, 'cron', hour = args.hour, minute = args.minute, second = args.second, args = [args.time])
    # try:
        # print("Wait until %s:%s:%s to download blog pictures" % (args.hour, args.minute, args.second))
        # scheduler.start()
    # except (KeyboardInterrupt, SystemExit):
        # scheduler.shutdown(wait=False)
