import sys, os, urllib2, urlparse, re
import argparse
from bs4 import BeautifulSoup

def fetchIndex(url, pretend):
	hostname = urlparse.urlparse(url).hostname
	print 'URL: ' + url

	response = urllib2.urlopen(url)
	html = response.read().decode('utf-8', 'ignore')
	
	parsed_html = BeautifulSoup(html)
	title = parsed_html.body.find('h1').text
	
	if not os.path.exists(title):
		os.makedirs(title)
	
	container = parsed_html.body.find('div', attrs={'class': 'sisu_content'})
	
	episode_urls = []
	for link in container.find_all('a'):
		target = link.get('href')
		if '/helid?' in target:
			episode_urls.append(target)
	
	total = len(episode_urls)
	i = 1
	for episode in episode_urls:
		fetchEpisode(hostname, title, episode, i, total, pretend)
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
	
	block_sz = 8192
	while True:
	    buffer = u.read(block_sz)
	    if not buffer:
	        break
	
	    file_size_dl += len(buffer)
	    f.write(buffer)
	    status = r"[%3.2f%%]" % (file_size_dl * 100. / total_size)
	    sys.stdout.write("\r(%d/%d) r%s %s" % (nr, total, title, status))
	    sys.stdout.flush()
	
	f.close()
	print ''


def fetchEpisode(hostname, title, episode_url, nr, total, pretend):
	url = 'http://' + hostname + episode_url
	
	response = urllib2.urlopen(url)
	html = response.read().decode('utf-8', 'ignore')
	
	parsed_html = BeautifulSoup(html)
	episode = parsed_html.body.find('h3').text
	date = parsed_html.body.find('h5').text
	file_name = date + ' - ' + episode
	
	if pretend:
		print file_name
	else:
		sound_clip_id = re.search('(\d+)', episode_url).group(0)
		url = 'http://heli.er.ee/helid/klassika/' + sound_clip_id + '.mp3'
		download(url, title + '/' + file_name + '.mp3', file_name, nr, total)



parser = argparse.ArgumentParser(description='Fetches episodes from Klassikaraadio')
parser.add_argument('url', metavar='URL', help='URL of the Klassikaraadio episode list')
                   
parser.add_argument('--pretend', dest='pretend', action='store_true',
                   help='sum the integers (default: find the max)')

args = parser.parse_args()

fetchIndex(args.url, args.pretend)