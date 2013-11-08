import sys, os, urllib2, urlparse, re
import argparse
from bs4 import BeautifulSoup
from urlparse import urlparse

class Klassikaraadio:
	
	@staticmethod
	def supports(url):
		return urlparse(url).hostname == 'klassikaraadio.err.ee'
		
	def __init__(self, url, pretend):
		print 'Fetching from Klassikaraadio'
		self.hostname = urlparse(url).hostname
		self.pretend = pretend

		response = urllib2.urlopen(url)
		html = response.read().decode('utf-8', 'ignore')
		
		parsed_html = BeautifulSoup(html)
		self.title = parsed_html.body.find('h1').text
		
		if not os.path.exists(self.title):
			os.makedirs(self.title)
		
		container = parsed_html.body.find('div', attrs={'class': 'sisu_content'})
		
		episode_urls = []
		for link in container.find_all('a'):
			target = link.get('href')
			if '/helid?' in target:
				episode_urls.append(target)
		
		total = len(episode_urls)
		i = 1
		for episode in episode_urls:
			self.fetchEpisode(episode, i, total)
			i += 1
		
	def fetchEpisode(self, episode_url, nr, total):
		url = 'http://' + self.hostname + episode_url
		
		response = urllib2.urlopen(url)
		html = response.read().decode('utf-8', 'ignore')
		
		parsed_html = BeautifulSoup(html)
		episode = parsed_html.body.find('h3').text
		date = parsed_html.body.find('h5').text
		file_name = date + ' - ' + episode
		
		if self.pretend:
			print file_name
		else:
			sound_clip_id = re.search('(\d+)', episode_url).group(0)
			url = 'http://heli.er.ee/helid/klassika/' + sound_clip_id + '.mp3'
			download(url, self.title + '/' + file_name + '.mp3', file_name, nr, total)
	
class Raadio2:

	@staticmethod
	def supports(url):
		return urlparse(url).hostname == 'r2.err.ee'
		
	def __init__(self, url, pretend):
		print 'Fetching from r2'
		
		response = urllib2.urlopen(url)
		html = response.read().decode('utf-8', 'ignore')
		
		parsed_html = BeautifulSoup(html)
		page_title = parsed_html.head.find('title').text
		self.title = page_title.split('.')[1].strip()
		
		if not os.path.exists(self.title):
			os.makedirs(self.title)
		
		episodes = []
		container = parsed_html.body.find('div', attrs={'id': 'centercolumn'})
		for paragraph in container.find_all('p'):
			url = paragraph.find_all('a')[1].get('href')
			title = paragraph.contents[0].strip('(').strip()
			if title.startswith(self.title):
				title = title[len(self.title):].strip()
			
			if len(title) > 0:
				episodes.append({'url': url, 'title': title})
		
		total = len(episodes)
		i = 1
		for episode in episodes:
			if pretend:
				print episode['title']
			else:
				download(episode['url'], self.title + '/' + episode['title'] + '.mp3', episode['title'], i, total)
				i += 1
	


def download(url, file_path, title, nr, total):

	req = urllib2.Request(url)
	total_size = 0
	
	if os.path.exists(file_path):
		f = open(file_path, 'ab')
		size = os.path.getsize(file_path)
		req.headers['Range'] = 'bytes=%s-' % (size)
		total_size += size
	else:
		f = open(file_path, 'wb')
	
	try:
		u = urllib2.urlopen(req)
	except urllib2.HTTPError as e:
		if e.code == 416:
			f.close()
			return

	meta = u.info()
	
	file_size_dl = total_size
	
	file_size = int(meta.getheaders("Content-Length")[0])
	total_size += file_size
	size_in_mb = total_size / (1024*1024)
	
	block_sz = 8192
	while True:
	    buffer = u.read(block_sz)
	    if not buffer:
	        break
	
	    file_size_dl += len(buffer)
	    f.write(buffer)
	    status = "[%3.2f%% of %d MB]" % (file_size_dl * 100. / total_size, size_in_mb)
	    sys.stdout.write("\r(%d/%d) %s %s" % (nr, total, title, status))
	    sys.stdout.flush()
	
	f.close()
	print ''

parser = argparse.ArgumentParser(description='Fetches episodes from Klassikaraadio')
parser.add_argument('url', metavar='URL', help='URL of the Klassikaraadio episode list')
                   
parser.add_argument('--pretend', dest='pretend', action='store_true',
                   help='Does not download any files')

args = parser.parse_args()
print 'URL: ' + args.url

classes = [Klassikaraadio, Raadio2]
for c in classes:
	if c.supports(args.url):
		c(args.url, args.pretend)
		break
