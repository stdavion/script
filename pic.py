import feedparser
from bs4 import BeautifulSoup
import argparse
import requests
import os
import sys
import random
import re
import datetime
from multiprocessing import Pool

desktop = "C:\\Users\\Kappa\\Desktop"

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

def download_site():
	url = "http://blog.livedoor.jp/fumichen2/tag/乃木坂46"
	for p in range(68):
		nurl = '%s?p=%d' % (url, p + 1)
		print(nurl)
		text = requests.get(nurl, stream=True, headers={'User-Agent': random.choice(my_headers)}).text
		dest_path = "%s\\%s" % (desktop, "fumichen2")
		file_path = "%s\\\\%d.html" % (dest_path, p + 1)
		if not os.path.isdir(dest_path):
			os.makedirs(dest_path)
		with open(file_path, "wb+") as f:
			f.write(text.encode())

def getSoup(url):
    text = requests.get(url, stream=True, headers={'User-Agent': random.choice(my_headers)}).text
    soup = BeautifulSoup(text, 'html.parser')
    if "dwango" in url:
    	getDwangoUrls(soup)
    elif "mdpr" in url:
    	getMdprUrls(soup)
    elif "tokyopopline" in url:
    	getTPLPics(soup)
    elif "edgeline" in url:
    	getEdgeline(soup)
    elif "nhk" in url:
    	getNHKPics(soup, url)
    else:
    	getPics(soup)

def getTime(soup):
	time = soup.find("time")
	strtime = time.string[2:].split(" ")[0].replace(".", "").replace("/", "")
	return strtime

def filecount(dir):
	count = 0
	for x in os.listdir(os.path.dirname(dir)):
		if os.path.isfile(x) and not x.endswith("html") and not x.endswith("txt"):
			count+=1
	return count

def download(url, dest_path, header):
    html = requests.get(url, headers = header)
    file_name = url.split(r'/')[-1]
    if not os.path.isdir(dest_path):
    	os.makedirs(dest_path)
    output_path = "{}{}{}".format(dest_path, os.sep, file_name)
    f = open(output_path, 'wb')
    f.write(html.content)
    f.close()

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

def download_img(url, filename, dest_path):
	if url.startswith("http://dcimg"):
		s = requests.session()
		headers = {
			"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36",
			"Host": "dcimg.awalker.jp",
			"Upgrade-Insecure-Requests": "1"
		}
		pic_url = url.replace("jp/view/", "jp/i/")
		pic_res = s.get(pic_url, headers=headers)
		print(filename)
		output_path = "{}{}{}".format(dest_path, os.sep, filename)
		if not os.path.isdir(dest_path):
			os.makedirs(dest_path)
		with open(output_path, "wb") as f:
			f.write(pic_res.content)
	else:
		download_file(url, filename, dest_path)

def getNHKPics(soup, url):
    div = soup.find("div", id="center")
    urlsplit = url.split("/")
    strtime = "%s%s%s" % (urlsplit[-4][2:], urlsplit[-3], urlsplit[-2])
    for img in div.find_all("img"):
    	link = "https://www.nhk.or.jp%s" % img.get("src")
    	download_file(link, link.split("/")[-1], "%s\\%s radirer" % (desktop, strtime))

def getDwangoUrls(soup):
	time = soup.find("span", class_="date")
	strtime = time.string[6:].replace("/", "")
	links = []
	for a in soup.find("div", class_="sec-item").findAll('img'):
		href = a.get('src')
		if href and href.startswith("http") and ("news-img" in href or "news-dwango" in href):
			link = href.replace("/lg_", "/").replace("/sm_", "/")
			if link not in links:
				download_file(link, link.split("/")[-1], "%s\\%s dwango" % (desktop, strtime))
				links.append(link)

def getMdprUrls(soup):
	strtime = getTime(soup)
	for img in [item for item in soup.find_all("img", class_="outputthumb") if len(item["class"]) == 1]:
		src = img.get("src")
		if src and src.startswith("http"):
			last = src.split("?")[-1]
			link = src[0 : src.index(last) - 1]
			download_file(link, link.split("/")[-1], "%s\\%s mdpr" % (desktop, strtime))

def getTPLPics(soup):
    strtime = getTime(soup)
    div = soup.find("div", id="gallery-1")
    for a in div.find_all("a"):
    	link = a.get("href")
    	download_file(link, link.split("/")[-1], "%s\\%s TPL" % (desktop, strtime))    	

def getEdgeline(soup):
    time = soup.find("time")
    strtime = time.get("datetime")[2:10].replace("-", "")
    div = soup.find("div", id="the-content")
    for a in div.find_all("a"):
    	link = a.get("href")
    	if "edgeline" in link:
    		download_file(link, link.split("/")[-1], "%s\\%s edgeline" % (desktop, strtime))  

def getNonnoPics(url):
	text = requests.get(url, stream=True, headers={'User-Agent': random.choice(my_headers)}).text
	soup = BeautifulSoup(text, 'html.parser')
	filename = url.split("/")[-1]
	for img in soup.findAll("img", attrs={"upimage":"org"}):
		link = img.get("src")
		download_file(link, link.split("/")[-1], "%s\\%s" % (desktop, filename))

def getPics(soup):
	strtime = getTime(soup)
	for a in soup.findAll('a'):
		href = "%s.jpg" % a.get('href')
		download_file(href, href.split("/")[-1], "%s\\%s" % (desktop, strtime))

def getNaviPics(url, count):
	a = url.replace("https://news.mynavi.jp/article/", "")
	time = a[2:8]
	for idx in range(count):
		header = {'User-Agent': random.choice(my_headers), "Referer":"https://news.mynavi.jp"}
		link = "%simages/%03dl.jpg" % (url, idx + 1)
		print(link)
		download(link, "%s\\%s" % (desktop, time), header)

def getCrankPic(url, count):
	filename = url.split("/")[-1]
	fileurl = url[:url.index(filename)]
	index = int(filename[:-9])	
	while(index < count):
		index += 1
		url = "%s%d_1200.jpg" % (fileurl, index)
		download_file(url, url.split("/")[-1], "%s\\crank" % desktop)

if __name__ == "__main__":
	# download_site()
	parser = argparse.ArgumentParser(description='Download dwango navi mdpr nonno photos.')
	parser.add_argument('url', type=str, nargs='?', help='Target Url')
	parser.add_argument('count', type=int, nargs='?', help='Image count')
	args = parser.parse_args()
	if args.url:
		if "nonno" in args.url:
			getNonnoPics(args.url)
		elif "mynavi" in args.url:
			if args.count:
				getNaviPics(args.url, args.count)
			else:
				parser.print_help()
		elif "crank" in args.url:
			if args.count:
				getCrankPic(args.url, args.count)
			else:
				parser.print_help()
		else:
			getSoup(args.url)
	else:
		parser.print_help()