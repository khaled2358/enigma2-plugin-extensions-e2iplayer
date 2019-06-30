# -*- coding: utf-8 -*-
from Plugins.Extensions.IPTVPlayer.tools.iptvtools import printDBG
from Plugins.Extensions.IPTVPlayer.libs import ph
from Plugins.Extensions.IPTVPlayer.tsiplayer.tstools import TSCBaseHostClass,cryptoJS_AES_decrypt
from Plugins.Extensions.IPTVPlayer.libs.crypto.cipher.aes_cbc import AES_CBC
from Plugins.Extensions.IPTVPlayer.libs.e2ijson import loads as json_loads
from binascii import a2b_hex
from hashlib import sha256
import base64
import re
import urllib


from binascii import unhexlify
from hashlib import md5

def getinfo():
	info_={}
	info_['name']='Cimaflix.Net'
	info_['version']='1.1 29/05/2019'
	info_['dev']='RGYSoft (Thx to SAMSAM)'
	info_['cat_id']='201'
	info_['desc']='أفلام, مسلسلات و انمي عربية و اجنبية'
	info_['icon']='https://on.cimaflix.net/images/logo.png'
	info_['recherche_all']='0'
	info_['update']='Change host to on.cimaflix.net & Disable search temporarily'
		
	return info_
	
	
class TSIPHost(TSCBaseHostClass):
	def __init__(self):
		TSCBaseHostClass.__init__(self,{'cookie':'cimaflix.cookie'})
		self.USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0'
		self.MAIN_URL = 'https://on.cimaflix.net'
		self.HEADER = {'User-Agent': self.USER_AGENT, 'Connection': 'keep-alive', 'Accept-Encoding':'gzip', 'Upgrade-Insecure-Requests':'1','Referer':self.getMainUrl(), 'Origin':self.getMainUrl()}
		self.defaultParams = {'header':self.HEADER,'with_metadata':True,'no_redirection':False, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': self.COOKIE_FILE}
		self.getPage = self.cm.getPage
		 
	def showmenu0(self,cItem):

		sts, data = self.getPage(self.MAIN_URL)
		if sts:
			Liste_els = re.findall('<a href="#"><i class="fa fa.*?>(.*?)<\/a>(.*?)<\/ul>', data, re.S)
			for (titre,data_) in Liste_els:
				self.addDir({'import':cItem['import'],'category' : 'host2','title':ph.clean_html(titre),'icon':cItem['icon'],'mode':'20','data':data_} )
		#self.addDir({'import':cItem['import'],'category':'search','title': _('Search'), 'search_item':True,'page':1,'hst':'tshost','icon':cItem['icon']})
		
	def showmenu1(self,cItem):
		Liste_els = re.findall('<li>.*?href="(.*?)">(.*?)<', cItem['data'], re.S)
		for (url,titre) in Liste_els:
			self.addDir({'import':cItem['import'],'category' : 'host2','url':url,'title':titre,'icon':cItem['icon'],'mode':'30'} )
			
			
	def showitms(self,cItem):
		url1=cItem['url']
		page=cItem.get('page',1)
		index = (page-1)*49
		sts, data = self.getPage(url1+'page-'+str(index))
		Liste_els = re.findall('<div class="list-item">.*?href="(.*?)".*?src="(.*?)".*?title">(.*?)<\/div>', data, re.S)
		i=0
		for (url,image,titre) in Liste_els:
			self.addDir({'import':cItem['import'],'good_for_fav':True,'EPG':True,'category' : 'host2','url':url,'title':ph.clean_html(titre),'icon':image,'mode':'31','hst':'tshost'} )			
			i=i+1
		if i>47:
			self.addDir({'import':cItem['import'],'title':'Page Suivante','page':page+1,'category' : 'host2','url':url1,'icon':cItem['icon'],'mode':'30'} )									
		

	def showelms(self,cItem):
		url1=cItem['url']
		sts, data = self.getPage(url1)
		Liste_els = re.findall('class="post">.*?href="(.*?)".*?title="(.*?)".*?src="(.*?)"', data, re.S)
		if Liste_els:
			for (url,titre,image) in Liste_els:
				self.addVideo({'import':cItem['import'],'good_for_fav':True,'category' : 'host2','url':url+'?sv=1','title':titre,'icon':image,'hst':'tshost'} )			
		else:
			self.addVideo({'import':cItem['import'],'good_for_fav':True,'category' : 'host2','url':url1+'?sv=1','title':cItem['title'],'icon':cItem['icon'],'hst':'tshost'} )			
			
	
	
	
	def SearchResult1(self,str_ch,page,extra):
		searchPattern=str_ch
		marker = 'google.search.Search.csqr2538'
		url = 'https://cse.google.com/cse.js?cx=002905823017627243012:xoba_omzj5w'
		sts, data = self.getPage(url)
		if not sts: return
		data_els = re.findall('\(({.*?})\);', data, re.S)
		if data_els:
			tmp = data_els[1]
			printDBG('ttttttttttttttttt'+tmp)
			tmp = json_loads(tmp)
			url = tmp['protocol'] + '://' + tmp['uds'] + '/' +  tmp['loaderPath']
			url += '?autoload=%7B%22modules%22%3A%5B%7B%22name%22%3A%22search%22%2C%22version%22%3A%221.0%22%2C%22callback%22%3A%22__gcse.scb%22%2C%22style%22%3A%22http%3A%2F%2Fwww.google.com%2Fcse%2Fstatic%2Fstyle%2Flook%2Fv2%2Fdefault.css%22%2C%22language%22%3A%22'
			url += tmp['language'] + '%22%7D%5D%7D'
			lang = tmp['language']
			token = tmp['cse_token']
			sts, tmp = self.getPage(url)
			if not sts: return
			hash = ph.search(tmp, '''google\.search\.JSHash\s*?=\s*?['"]([^'^"]+?)['"]''')[0]

			baseUrl = 'https://cse.google.com/cse/element/v1?rsz=filtered_cse&num=10&hl='
			baseUrl += lang + '&source=gcsc&gss=.tv&sig=' + hash + '&start={0}&cx=' + cx
			baseUrl += '&q=dead&safe=off&cse_tok=' + token + '&googlehost=www.google.com&callback=' + marker


			url = baseUrl.format(str(page*10))
			sts, data = self.getPage(url)
			printDBG('ddddddddddddd'+data)
		
	def SearchResult(self,str_ch,page,extra):
		url='https://cse.google.com/cse/element/v1?rsz=filtered_cse&num=10&hl=ar&source=gcsc&gss=.com&cselibv=5d7bf4891789cfae&cx=002905823017627243012:xoba_omzj5w&q='+str_ch+'&safe=off&cse_tok=AKaTTZgv7DKIyeQSmxrA753KYYq3:1557397954561&sort=&exp=csqr,4229469&oq='+str_ch+'&callback=google.search.cse.api13946'

		url='https://cse.google.com/cse/element/v1?rsz=filtered_cse&num=10&hl=ar&source=gcsc&gss=.com&cselibv=5d7bf4891789cfae&cx=002905823017627243012:xoba_omzj5w&q='+str_ch+'&safe=off&cse_tok=AKaTTZgv7DKIyeQSmxrA753KYYq3:1557397954561&sort=&exp=csqr,4229469&oq='+str_ch+'&gs_l=partner-generic.12...13879.13879.1.14802.1.1.0.0.0.0.190.190.0j1.1.0.gsnos,n=13...0.0....34.partner-generic..3.0.0.g0m1uVF97m8&callback=google.search.cse.api13946'
		url='https://cse.google.com/cse/element/v1?rsz=filtered_cse&num=10&hl=ar&source=gcsc&gss=.com&cselibv=5d7bf4891789cfae&cx=002905823017627243012:xoba_omzj5w&q='+urllib.quote(str_ch)+'&safe=off&cse_tok=AKaTTZj3wNKpWeOU1-_LoEOy_2ff:1557398789721&sort=&exp=csqr,4229469&callback=google.search.cse.api4514'
		sts, data = self.getPage(url)
		data_els = re.findall('\(({.*?})\);', data, re.S)
		if data_els:
			data = data_els[0]
			printDBG(data)
			jdata = json_loads(data)
			items=jdata['results']
			for item in items:
				title=ph.clean_html(item['title'].encode("utf-8").replace(' اون لاين مباشرة على موقع سيما فليكس','').replace('...',''))
				link=item['url']
				try:
					image=item['richSnippet']['cseImage']['src']
				except:
					image=''
				self.addDir({'import':extra,'good_for_fav':True,'category' : 'host2','title':title,'icon':image,'url':link,'mode':'31','good_for_fav':True})
			
				
	def get_links(self,cItem):
		urlTab = []	
		URL=cItem['url']
		sts, data = self.getPage(URL)
		printDBG('ddddddddaaaaaaaat'+data)
		data_els = re.findall('(class="serverslist active"|class="serverslist").*?data-server="(.*?)">(.*?)<', data, re.S)
		for (x1,data_,host_) in data_els:
			host_ = host_.replace(' ','')
			urlTab.append({'name':host_, 'url':'hst#tshost#'+data_, 'need_resolve':1})		
		return urlTab
		
		 
	def getVideos(self,videoUrl):
		urlTab = []	
		data = urllib.unquote(videoUrl)
		data = json_loads(data.strip())
		ciphertext = base64.b64decode(data['ct'])
		iv = unhexlify(data['iv'])
		salt = unhexlify(data['s'])
		b = "Fex-XFa_x3MjW4w"
		decrypted = cryptoJS_AES_decrypt(ciphertext, b, salt)
		cUrl = decrypted.replace('\\','').replace('"','')
		sts, data = self.getPage(cUrl,dict(self.defaultParams))
		if sts:
			cUrl = data.meta['url']		
			urlTab.append((cUrl,'1'))
		return urlTab
		
	def getArticle(self, cItem):
		printDBG("cima4u.getVideoLinks [%s]" % cItem) 
		otherInfo1 = {}
		desc = cItem.get('desc','')
		sts, data = self.getPage(cItem['url'])
		lst_dat2=re.findall('<div class="field">.*?title">(.*?)<.*?>(.*?)</div>', data, re.S)
		for (x1,x2) in lst_dat2:
			if 'اسم فيلم'    in x1: otherInfo1['original_title'] = ph.clean_html(x2)
			if 'اسم مسلسل'   in x1: otherInfo1['original_title'] = ph.clean_html(x2)
			if 'اسم سلسلة'   in x1: otherInfo1['original_title'] = ph.clean_html(x2)
			if 'اسم برنامج'  in x1: otherInfo1['original_title'] = ph.clean_html(x2)
			if 'اسماء اخرى'  in x1: otherInfo1['alternate_title'] = ph.clean_html(x2)			
			if 'الجودة'      in x1: otherInfo1['quality'] = ph.clean_html(x2)					
			if 'عدد حلقات'   in x1: otherInfo1['episodes'] = ph.clean_html(x2)	
			if 'تصنيف'       in x1: otherInfo1['genres'] = ph.clean_html(x2)
			if 'النوع'       in x1: otherInfo1['categories'] = ph.clean_html(x2)			
			if 'منتج'        in x1: otherInfo1['creator'] = ph.clean_html(x2)					
			if 'العمري'      in x1: otherInfo1['type'] = ph.clean_html(x2)			
			if 'حالة'        in x1: otherInfo1['status'] = ph.clean_html(x2)			
			if 'تاريخ'       in x1: otherInfo1['year'] = ph.clean_html(x2)					
			if 'قصة'         in x1: desc = ph.clean_html(x2)			
			
				
		icon = cItem.get('icon')
		title = cItem['title']		
		return [{'title':title, 'text': desc, 'images':[{'title':'', 'url':icon}], 'other_info':otherInfo1}]

	
	def start(self,cItem):      
		mode=cItem.get('mode', None)
		if mode=='00':
			self.showmenu0(cItem)
		if mode=='20':
			self.showmenu1(cItem)
		if mode=='30':
			self.showitms(cItem)			
		if mode=='31':
			self.showelms(cItem)

			
