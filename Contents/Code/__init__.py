NAME = 'רשת'
BASE_URL = 'http://reshet.tv/'

SHOWS_URL = '%s/Shows/VOD/page-%%d' % BASE_URL
SHOW_URL = '%s/Shows/VOD/%%s/' % BASE_URL
SEASON_URL = '%s/Shows/VOD/%%s/season-%%d/' % BASE_URL

ART = 'art-default.jpg'
ICON = 'icon-default.jpg'

####################################################################################################
def Start():

	ObjectContainer.art = R(ART)
	ObjectContainer.title1 = NAME
	DirectoryObject.thumb = R(ICON)

	HTTP.CacheTime = CACHE_1HOUR
	HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.107 Safari/537.36'

####################################################################################################
@handler('/video/clicktoplay', NAME, thumb=ICON, art=ART)
def MainMenu():

	return Shows()

####################################################################################################
@route('/video/clicktoplay/shows/{page}', page=int)
def Shows(page=1):

	oc = ObjectContainer()
	html = HTML.ElementFromURL(SHOWS_URL % page, sleep=0.5)

	for show in html.xpath('//ul[@class="coll_list"]/li'):
		title = show.xpath('.//span[@class="title"]/text()')[0]
		thumb = show.xpath('.//span[@class="coll_poster"]/@style')[0].split('(')[-1].split(')')[0]
		show_id = show.xpath('.//a/@href')[0].split('/')[-2]

		oc.add(DirectoryObject(
			key = Callback(Seasons, title=title, thumb=thumb, show_id=show_id),
			title = title,
			thumb = thumb
		))

	if len(html.xpath('//span[@class="next"]')) > 0:
		oc.extend(Shows(page=page+1))

	oc.objects.sort(key = lambda obj: obj.title)
	return oc

####################################################################################################
@route('/video/clicktoplay/seasons/{show_id}')
def Seasons(title, thumb, show_id):

	oc = ObjectContainer(title2=title)
	html = HTML.ElementFromURL(SHOW_URL % show_id)
	num_season = len(html.xpath('//ul[@id="tabs-ul"]/li/a[contains(., "Season ")]'))

	for i in range(1, num_season+1):
		oc.add(DirectoryObject(
			key = Callback(Episodes, title='Season %d' % i, show_id=show_id, season=i),
			title = 'Season %d' % i,
			thumb = thumb
		))

	return oc

####################################################################################################
@route('/video/clicktoplay/episodes/{show_id}/{season}', season=int)
def Episodes(title, show_id, season):

	oc = ObjectContainer(title2=title)
	html = HTML.ElementFromURL(SEASON_URL % (show_id, season))

	for episode in html.xpath('//div[@id="tabs-content"]/ul/li'):
		url = episode.xpath('./a/@href')[0]
		show = episode.xpath('./a/@title')[0].split(' / ')[0]
		(index, title) = episode.xpath('.//span[@class="title"]/@title')[0].split(' - ', 1)
		thumb = episode.xpath('.//span[@class="thumb"]/@style')[0].split('(')[-1].split(')')[0]

		try: index = int(index.split(' ')[-1])
		except: index = None

		try:
			oc.add(EpisodeObject(
				url = url,
				title = title,
				show = show,
				index = index,
				season = season,
				thumb = thumb
			))
		except:
			continue

	return oc
