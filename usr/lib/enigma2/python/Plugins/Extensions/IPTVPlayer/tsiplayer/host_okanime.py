# -*- coding: utf-8 -*-
from Plugins.Extensions.IPTVPlayer.tools.iptvtools import printDBG
from Plugins.Extensions.IPTVPlayer.libs import ph
from Plugins.Extensions.IPTVPlayer.tsiplayer.tstools import TSCBaseHostClass

import re

def getinfo():
	info_={}
	info_['name']='Okanime.Com'
	info_['version']='1.0 19/05/2019'
	info_['dev']='RGYSoft'
	info_['cat_id']='203'
	info_['desc']='انمي مترجم'
	info_['icon']='https://i.ibb.co/88XFP0D/okanim.jpg'
	info_['recherche_all']='0'
	info_['update']='New Host'
	return info_
	
	
class TSIPHost(TSCBaseHostClass):
	def __init__(self):
		TSCBaseHostClass.__init__(self,{'cookie':'okanime.cookie'})
		self.USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0'
		self.MAIN_URL = 'https://www.okanime.com'
		self.HEADER = {'User-Agent': self.USER_AGENT, 'Connection': 'keep-alive', 'Accept-Encoding':'gzip', 'Content-Type':'application/x-www-form-urlencoded','Referer':self.getMainUrl(), 'Origin':self.getMainUrl()}
		self.defaultParams = {'header':self.HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': self.COOKIE_FILE}
		self.getPage = self.cm.getPage
		 
	def showmenu0(self,cItem):
		hst='host2'
		img_=cItem['icon']
		self.addMarker({'title':'أفلام','category' : 'host2','icon':img_} )									

		Cat_TAB = [
					{'category':hst,'title': 'الترتيب حسب الأبجدية', 'mode':'30','url':'https://www.okanime.com/movies?direction=asc&sort=title'},
					{'category':hst,'title': 'الترتيب حسب تقييم الأعضاء', 'mode':'30','url':'https://www.okanime.com/movies?direction=desc&sort=rating_caches.avg'},
					{'category':hst,'title': 'الترتيب حسب أحدث الافلام', 'mode':'30','url':'https://www.okanime.com/movies?direction=desc&sort=published_at'},
					]
		self.listsTab(Cat_TAB, {'import':cItem['import'],'icon':img_})	
		self.addMarker({'title':'قائمة الانميات','category' : 'host2','icon':img_} )	
		Cat_TAB = [
					{'category':hst,'title': 'الترتيب حسب الأبجدية', 'mode':'30','url':'https://www.okanime.com/animes?direction=asc&sort=title'},
					{'category':hst,'title': 'الترتيب حسب تقييم الأعضاء', 'mode':'30','url':'https://www.okanime.com/animes?direction=desc&sort=rating_caches.avg'},
					{'category':hst,'title': 'الترتيب حسب أحدث الانميات', 'mode':'30','url':'https://www.okanime.com/animes?direction=desc&sort=published_at'},

					{'category':'search','title': _('Search'), 'search_item':True,'page':1,'hst':'tshost'},
					]
		self.listsTab(Cat_TAB, {'import':cItem['import'],'icon':img_})			
		
		
	def showitms(self,cItem):
		url1=cItem['url']
		page=cItem.get('page',1)
		sts, data = self.getPage(url1+'&page='+str(page))
		films_list = re.findall('class=\'col-md-15.*?title="(.*?)".*?href="(.*?)".*?src="(.*?)".*?class="rating.*?>(.*?)</div>.*?class=\'genre-.*?>(.*?)</div>', data, re.S)		
		for (titre,url,image,rate,desc) in films_list:
			if not url.startswith('http'): url=self.MAIN_URL+url
			if not image.startswith('http'): image=self.MAIN_URL+image
			desc='Rating: \c00????00'+ph.clean_html(rate)+'\c00??????\\nGenre: \c00????00'+ph.clean_html(desc)
			self.addDir({'import':cItem['import'],'good_for_fav':True,'category' : 'host2','url': url,'title':titre,'desc':desc,'icon':image,'hst':'tshost','mode':'31'})	
		self.addDir({'import':cItem['import'],'title':'Page '+str(page+1),'page':page+1,'category' : 'host2','url':url1,'icon':image,'mode':'30'} )									

	def showelms(self,cItem):
		urlo=cItem['url']
		sts, data = self.getPage(urlo)
		Liste_els = re.findall('class="btn btn-lg2.*?href="(.*?)"', data, re.S)
		if Liste_els:
			url1=Liste_els[0]
			if not url1.startswith('http'): url1=self.MAIN_URL+url1
			sts, data = self.getPage(url1)
			films_list = re.findall('<ul class=\'episodes-list(.*?)</ul>', data, re.S)
			if films_list:
				films_list1 = re.findall('<a.*?href="(.*?)".*?class=\'episode\'>(.*?)</li>', films_list[0], re.S)				
				for (url,titre) in films_list1:
					if not url.startswith('http'): url=self.MAIN_URL+url
					self.addVideo({'import':cItem['import'],'good_for_fav':True,'category' : 'host2','url': url,'title':ph.clean_html(titre),'desc':cItem['desc'],'icon':cItem['icon'],'hst':'tshost'} )
			else:
				self.addVideo({'import':cItem['import'],'good_for_fav':True,'category' : 'host2','url': url1,'title':cItem['title'],'desc':cItem['desc'],'icon':cItem['icon'],'hst':'tshost'} )
		
	
	def SearchResult(self,str_ch,page,extra):
		url_='https://www.okanime.com/search?utf8=%E2%9C%93&%5Bsearch%5D='+str_ch
		sts, data = self.getPage(url_)
		films_list = re.findall('class=\'col-md-15.*?href="(.*?)".*?src="(.*?)".*?class="rating.*?>(.*?)</div>.*?title\'>(.*?)<', data, re.S)		
		for (url,image,rate,titre) in films_list:
			if not url.startswith('http'): url=self.MAIN_URL+url
			if not image.startswith('http'): image=self.MAIN_URL+image
			desc='Rating: \c00????00'+ph.clean_html(rate)
			self.addDir({'import':extra,'good_for_fav':True,'category' : 'host2','url': url,'title':titre,'desc':desc,'icon':image,'hst':'tshost','mode':'31'})	


	def get_links(self,cItem):
		urlTab = []	
		URL=cItem['url']
		sts, data = self.getPage(URL)
		Tab_els = re.findall('<ul class=\'servers-list(.*?)</ul>', data, re.S)
		if Tab_els:
			Liste_els = re.findall('<li>.*?href="(.*?)">(.*?)<', Tab_els[0], re.S)
			for (code,host_) in Liste_els:
				urlTab.append({'name':host_, 'url':'hst#tshost#'+code, 'need_resolve':1})						
		return urlTab
		
		 
	def getVideos(self,videoUrl):
		urlTab = []	
		sUrl = self.MAIN_URL+videoUrl
		sts, data = self.getPage(sUrl)
		Liste_els_3 = re.findall('url":"(.*?)"', data, re.S)	
		if Liste_els_3:
			URL=Liste_els_3[0]
			if 'https://www.okanime.com' in URL:
				sts, data = self.getPage(URL)
				Liste_els_3 = re.findall('sources.*?file":"(.*?)"', data, re.S)	
				if Liste_els_3:
					URL1=Liste_els_3[0]				
					urlTab.append((Liste_els_3[0],'0'))
			else:
				urlTab.append((Liste_els_3[0],'1'))
		return urlTab

	
	def start(self,cItem):      
		mode=cItem.get('mode', None)
		if mode=='00':
			self.showmenu0(cItem)
		if mode=='30':
			self.showitms(cItem)			
		if mode=='31':
			self.showelms(cItem)
			
