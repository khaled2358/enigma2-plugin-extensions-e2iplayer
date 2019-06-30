# -*- coding: utf-8 -*-
###################################################
# LOCAL import
###################################################
from Plugins.Extensions.IPTVPlayer.components.iptvplayerinit import TranslateTXT as _
from Plugins.Extensions.IPTVPlayer.components.ihost import CHostBase, CBaseHostClass
from Plugins.Extensions.IPTVPlayer.tools.iptvtools import printDBG, printExc, byteify, MergeDicts, GetDefaultLang
from Plugins.Extensions.IPTVPlayer.libs.urlparserhelper import getDirectM3U8Playlist
from Plugins.Extensions.IPTVPlayer.libs.urlparser import urlparser
###################################################

###################################################
# FOREIGN import
###################################################
import urllib
try: import json
except Exception: import simplejson as json
from datetime import timedelta
###################################################


def gettytul():
    return 'https://twitch.tv/'

def jstr(item, key, default=''):
    v = item.get(key, default)
    if type(v) == type(u''): return v.encode('utf-8')
    elif type(v) == type(''): return v
    else: return default

class Twitch(CBaseHostClass):

    def __init__(self):
        CBaseHostClass.__init__(self, {'history':'Twitch', 'cookie':'Twitch.cookie'})

        self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
        self.defaultParams = {'header':self.HTTP_HEADER}#, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': self.COOKIE_FILE}

        self.DEFAULT_ICON_URL = 'http://s.jtvnw.net/jtv_user_pictures/hosted_images/GlitchIcon_WhiteonPurple.png'
        self.MAIN_URL = 'https://www.twitch.tv/'
        self.API1_URL = 'https://api.twitch.tv/'
        self.API2_URL = 'https://gql.twitch.tv/'
        
        self.CHANNEL_TOKEN_URL = self.getFullUrl('/api/channels/%s/access_token')
        self.LIVE_URL = 'http://usher.justin.tv/api/channel/hls/%s.m3u8?token=%s&sig=%s&allow_source=true'
        self.CHANNEL_TOKEN_URL = self.API1_URL + 'api/channels/%s/access_token?need_https=false&oauth_token&platform=web&player_backend=mediaplayer&player_type=site'
        
        self.VOD_TOKEN_URL = self.API1_URL + 'api/vods/%s/access_token?need_https=true&oauth_token&platform=web&player_backend=mediaplayer&player_type=site'
        self.VOD_URL = 'https://usher.ttvnw.net/vod/%s.m3u8?token=%s&sig=%s&allow_source=true'

        self.platformFilters = [{'title':_('All Platforms'), 'platform_type':'all'}, {'title':_('Xbox One'), 'platform_type':'xbox'}, {'title':_('PlayStation 4'), 'platform_type':'ps4'}]
        self.languagesFilters = [{'lang':"ar",'title':"العربية"},{'lang':"bg",'title':"Български"},{'lang':"cs",'title':"Čeština"},{'lang':"da",'title':"Dansk"},{'lang':"de",'title':"Deutsch"},{'lang':"el",'title':"Ελληνικά"},{'lang':"en",'title':"English"},{'lang':"es",'title':"Español"},{'lang':"fi",'title':"Suomi"},{'lang':"fr",'title':"Français"},{'lang':"hu",'title':"Magyar"},{'lang':"it",'title':"Italiano"},{'lang':"ja",'title':"日本語"},{'lang':"ko",'title':"한국어"},{'lang':"nl",'title':"Nederlands"},{'lang':"no",'title':"Norsk"},{'lang':"pl",'title':"Polski"},{'lang':"pt",'title':"Português"},{'lang':"ro",'title':"Română"},{'lang':"ru",'title':"Русский"},{'lang':"sk",'title':"Slovenčina"},{'lang':"sv",'title':"Svenska"},{'lang':"th",'title':"ภาษาไทย"},{'lang':"tr",'title':"Türkçe"},{'lang':"vi",'title':"TiếngViệt"},{'lang':"zh-hk",'title':"中文(粵語)"},{'lang':"zh",'title':"中文"},{'lang':'asl', 'title':'American Sign Language'},{'lang':'other', 'title':'Other'}]

        lang = GetDefaultLang()
        default = None
        defaultEn = None
        self.langItems = []
        for item in self.languagesFilters:
            if lang == item['lang']:
                default = item
                continue
            if 'en' == item['lang']:
                defaultEn = item
                continue
            self.langItems.append(item)
        if defaultEn: self.langItems.insert(0, defaultEn)
        if default: self.langItems.insert(0, default)
        self.langItems.insert(0, {'title':_('All')})
        
        
        self.VIDEOS_TYPES_TAB = [{'title':_('All')}, 
                                 {'title':_('Past premieres'), 'videos_type':'PAST_PREMIERE'},
                                 {'title':_('Archive'),        'videos_type':'ARCHIVE'      },
                                 {'title':_('Highlights'),     'videos_type':'HIGHLIGHT'    },
                                 {'title':_('Uploads'),        'videos_type':'UPLOAD'       },]
 
        self.VIDEOS_SORT_TAB = [{'title':_('Popular'), 'sort':'VIEWS' },
                                {'title':_('Recent'),  'sort':'TIME'  },]

        self.CLIPS_FILTERS_TAB = [{'title':_('Trending'),         'clips_filter':'TRENDING'   },
                                  {'title':_('Last day'),         'clips_filter':'LAST_DAY'   },
                                  {'title':_('Last week'),        'clips_filter':'LAST_WEEK'  },
                                  {'title':_('Last month'),       'clips_filter':'LAST_MONTH' },
                                  {'title':_('All time'),         'clips_filter':'ALL_TIME'   },]
                                  
        self.GAME_CAT_TAB = [{'category':'game_lang', 'next_category':'game_channels',      'title': _('Channels')},
                             {'category':'game_lang', 'next_category':'game_videos_types',  'title': _('Videos') },
                             {'category':'game_lang', 'next_category':'game_clips_filters', 'title': _('Clips') },
                            ]

    def getPage(self, baseUrl, addParams={}, post_data=None):
        if addParams == {}:
            addParams = dict(self.defaultParams)
        if 'api.twitch.tv' in baseUrl:
            addParams['header'] = MergeDicts(addParams['header'], {'Accept': 'application/vnd.twitchtv.v5+json', 'Client-ID':'jzkbprff40iqj646a697cyrvl0zt2m6'})
        elif 'gql.twitch.tv' in baseUrl:
            addParams['header'] = MergeDicts(addParams['header'], {'Accept': '*/*', 'Client-ID':'kimne78kx3ncx6brgo4mv6wki5h1ko'})
        return self.cm.getPage(baseUrl, addParams, post_data)

    def listMain(self, cItem):
        printDBG("Twitch.listMain")

        MAIN_CAT_TAB = [{'category':'browse',         'title': _('Browse') },
                        {'category':'search',         'title': _('Search'),       'search_item':True       },
                        {'category':'search_history', 'title': _('Search history'),                        }]
        self.listsTab(MAIN_CAT_TAB, cItem)

    def listDirectories(self, cItem):
        printDBG("Twitch.listDirectories")

        dirChannels = []
        for pItem in self.platformFilters:
            params = MergeDicts(cItem, pItem)
            subItems = [ MergeDicts(params, x, {'category':'dir_channels'}) for x in self.langItems ]
            params.update({'category':'sub_items', 'sub_items':subItems})
            dirChannels.append(params)

        TAB = [{'category':'dir_games',         'title': _('Games') },
               #{'category':'dir_communities',   'title': _('Communities') },
               #{'category':'dir_communities',   'title': _('Creative') },
               {'category':'sub_items',         'title': _('Channels'), 'sub_items':dirChannels },
        ]
        self.listsTab(TAB, cItem)

    def _listChannels(self, cItem, nextCategory, streamsData):
        try:
            cursor = ''
            for item in streamsData['edges']:
                cursor = jstr(item, 'cursor')
                item = item['node']
                descTab = []
                if item.get('broadcaster'):
                    title = jstr(item['broadcaster'], 'displayName')
                    icon = self.getFullIconUrl(jstr(item, 'previewImageURL'), self.cm.meta['url'])
                    descTab.append('[%s] %s' % (jstr(item, 'type'), jstr(item, 'title')))
                    descTab.append(jstr(item, '__typename') + ' | ' + _('%s viewers') % item['viewersCount'])
                    if item.get('broadcaster'):
                        descTab.append(jstr(item['broadcaster'], '__typename') + ': ' + jstr(item['broadcaster'], 'displayName'))
                    if item.get('game'):
                        descTab.append(jstr(item['game'], '__typename') + ': ' + jstr(item['game'], 'name'))
                    params = {'good_for_fav':True, 'name':'category', 'type':'category', 'category':nextCategory, 'title':title, 'user_login':str(item['broadcaster']['login']), 'icon':icon, 'desc':'[/br]'.join( descTab )}
                    self.addDir(params)

            if cursor != '' and streamsData['pageInfo']['hasNextPage']:
                self.addDir( MergeDicts(cItem, {'title':_('Next page'), 'cursor':cursor}) )
        except Exception:
            printExc()

    def listDirChannels(self, cItem, nextCategory):
        printDBG("Twitch.listDirChannels")

        lang = '"%s"' % cItem['lang'].upper() if 'lang' in cItem else ''
        cursor = ',"cursor":"%s"' % cItem['cursor'] if 'cursor' in cItem else ''
        type = cItem.get('platform_type', 'all')
        post_data = '[{"operationName":"BrowsePage_Popular","variables":{"limit":30,"platformType":"%s","languages":[%s],"tags":[],"isTagsExperiment":false%s},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"4a3254b9537ad005b6fbc6e7a811a4045312d4a4b5c0541bea86df60383972fd"}}}]' % (type, lang, cursor)
        url = self.getFullUrl('/gql', self.API2_URL)
        sts, data = self.getPage(url, MergeDicts(self.defaultParams, {'raw_post_data':True}), post_data)
        if not sts: return
        try:
            data = json.loads(data)
            self._listChannels(cItem, nextCategory, data[0]['data']['streams'])
        except Exception:
            printExc()

    def listDirGames(self, cItem, nextCategory):
        printDBG("Twitch.listDirGames")

        cursor = ',"cursor":"%s"' % cItem['cursor'] if 'cursor' in cItem else ''
        post_data = '[{"operationName":"BrowsePage_AllDirectories","variables":{"limit":30,"directoryFilters":["GAMES"],"isTagsExperiment":false,"tags":[]%s},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"dd3c574a80407f76e94a6e6c90e427cdca29a74791308b686aa2f35895f50a8f"}}}]' % (cursor)
        url = self.getFullUrl('/gql', self.API2_URL)
        sts, data = self.getPage(url, MergeDicts(self.defaultParams, {'raw_post_data':True}), post_data)
        if not sts: return
        try:
            cursor = ''
            data = json.loads(data)
            for item in data[0]['data']['directories']['edges']:
                cursor = jstr(item, 'cursor')
                item = item['node']
                if item['directoryType'] == 'GAME':
                    title = jstr(item, 'displayName')
                    icon = self.getFullIconUrl(jstr(item, 'avatarURL'), self.cm.meta['url'])
                    desc = jstr(item, '__typename') + ' | ' + _('%s viewers') % item['viewersCount']
                    params = {'good_for_fav':True, 'name':'category', 'category':nextCategory, 'title':title, 'game_id':str(item['id']), 'game_name':jstr(item, 'name'), 'icon':icon, 'desc':desc}
                    self.addDir(params)

            if cursor != '' and data[0]['data']['directories']['pageInfo']['hasNextPage']:
                self.addDir( MergeDicts(cItem, {'title':_('Next page'), 'cursor':cursor}) )

        except Exception:
            printExc()

    def listGameChannels(self, cItem, nextCategory):
        printDBG("Twitch.listGameChannels")
        lang = '"%s"' % cItem['lang'].upper() if 'lang' in cItem else ''
        cursor = ',"cursor":"%s"' % cItem['cursor'] if 'cursor' in cItem else ''
        post_data = '[{"operationName":"DirectoryPage_Game","variables":{"name":"%s","limit":30,"languages":[%s],"type":"GAME","filters":{"hearthstoneBroadcasterHeroName":"","pubgGameMode":"","pubgPlayerAliveMax":"","pubgPlayerAliveMin":"","hearthstoneBroadcasterHeroClass":"","hearthstoneGameMode":"","overwatchBroadcasterCharacter":"","leagueOfLegendsChampionID":"","counterStrikeMap":"","counterStrikeSkill":""},"sort":"VIEWER_COUNT","isTagsExperiment":false,"tags":[]%s},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"f19f66b5297929dcc6c8903aa65a09fd5635b6dcabed11db3ba80eef99303fda"}}}]' % (cItem['game_name'], lang, cursor)
        url = self.getFullUrl('/gql', self.API2_URL)
        sts, data = self.getPage(url, MergeDicts(self.defaultParams, {'raw_post_data':True}), post_data)
        if not sts: return
        try:
            data = json.loads(data)
            self._listChannels(cItem, nextCategory, data[0]['data']['directory']['streams'])
        except Exception:
            printExc()

    def listChannel(self, cItem):
        printDBG("Twitch.listChannel %s" % cItem['user_login'])

        login = cItem['user_login']
        post_data = []
        post_data.append('{"operationName":"ChannelPage_StreamType_User","variables":{"channelLogin":"%s"},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"43b152e4f17090ece0b50a5bc41e4690c7a6992ad3ed876d88bf7292be2d2cba"}}}' % login)
        post_data.append('{"operationName":"ChannelPage__ChannelViewersCount","variables":{"login":"%s"},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"3b5b233b59cc71f5ab273c74a30c46485fa52901d98d7850d024ad0669270184"}}}' % login)
        post_data.append('{"operationName":"ChannelPage_ChannelInfoBar_User_RENAME1","variables":{"login":"%s"},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"07256d20a34cd864e68e39cd5d4235e795895b5e4717b4ed041ad7f94982f78f"}}}' % login)
        post_data.append('{"operationName":"ChannelPage_ChannelHeader","variables":{"login":"%s"},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"32f05e9f36086c6e6930e3f3d0d515eea61cc3263bf7f92870f97c9aae024593"}}}' % login)
        url = self.getFullUrl('/gql', self.API2_URL)
        sts, data = self.getPage(url, MergeDicts(self.defaultParams, {'raw_post_data':True}), '[%s]' % ','.join(post_data))
        if not sts: return

        icon = ''
        try:
            data = json.loads(data)
            try:
                if data[0]['data']['user']['stream']['type'] == 'live':
                    descTab = []
                    viewers = str(data[1]['data']['user']['stream']['viewersCount'])
                    descTab.append(_('%s viewers') % viewers)
                    item = data[2]['data']['user']['lastBroadcast']
                    title = jstr(item, 'title')
                    if item.get('game'):
                        descTab.append( '%s: %s' % (jstr(item['game'], '__typename'), jstr(item['game'], 'name')) )
                        icon = self.getFullIconUrl(jstr(item['game'], 'boxArtURL'), self.cm.meta['url'])
                    else:
                        icon = ''

                    params = {'good_for_fav':False, 'title':title, 'game_id':str(item['id']), 'video_type':'live', 'channel_id':login, 'icon':icon, 'desc':'[/br]'.join(descTab)}
                    self.addVideo(params)
            except Exception:
                printExc()
            
            item = data[3]['data']['user']
            icon = self.getFullIconUrl(jstr(item, 'profileImageURL'), self.cm.meta['url'])
            videosCount = int(item['videos']['totalCount'])
            if videosCount:
                params = dict(cItem)
                params.update({'good_for_fav':False, 'category':'videos_types', 'title':_('Videos %s') % videosCount, 'icon':icon, 'desc':''})
                self.addDir(params)
        except Exception:
            printExc()

        params = MergeDicts(cItem, {'good_for_fav':False, 'category':'clips_filters', 'title':_('Clips'), 'icon':icon, 'desc':''})
        self.addDir(params)

    def _listVideos(self, cItem, videosData):
        printDBG("Twitch.listVideos")
        try:
            cursor = ''
            for item in videosData['edges']:
                cursor = jstr(item, 'cursor')
                item = item['node']
                descTab = []
                descTab.append( '{0}'.format(timedelta(seconds=item['lengthSeconds'])) )
                descTab.append( _('%s viewers') % item['viewCount'] )
                descTab.append( jstr(item, 'publishedAt') )
                descTab = [' | '.join(descTab)]
                
                icon = self.getFullIconUrl(jstr(item, 'previewThumbnailURL'), self.cm.meta['url'])
                title = jstr(item, 'title')

                if item.get('owner'):
                    descTab.append(jstr(item['owner'], '__typename') + ': ' + jstr(item['owner'], 'displayName'))
                if item.get('game'):
                    descTab.append(jstr(item['game'], '__typename') + ': ' + jstr(item['game'], 'name'))
                     
                params = {'good_for_fav':True, 'title':title, 'video_type':'video', 'video_id':jstr(item, 'id'), 'icon':icon, 'desc':'[/br]'.join( descTab )}
                self.addVideo(params)

            if cursor != '' and videosData['pageInfo']['hasNextPage']:
                self.addDir( MergeDicts(cItem, {'title':_('Next page'), 'cursor':cursor}) )
        except Exception:
            printExc()

    def listVideos(self, cItem):
        printDBG("Twitch.listVideos")
        cursor = ',"cursor":"%s"' % cItem['cursor'] if 'cursor' in cItem else ''
        broadcastType = '"%s"' % cItem['videos_type'] if 'videos_type' in cItem else 'null'
        post_data = '[{"operationName":"FilterableVideoTower_Videos","variables":{"limit":30,"channelOwnerLogin":"%s","broadcastType":%s,"videoSort":"%s"%s},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"352ca6e327523f88b08390bf79d1b1d6e5f67b46981c900cf41eca56ef9d3cfc"}}}]' % (cItem['user_login'], broadcastType, cItem['sort'], cursor)
        url = self.getFullUrl('/gql', self.API2_URL)
        sts, data = self.getPage(url, MergeDicts(self.defaultParams, {'raw_post_data':True}), post_data)
        if not sts: return

        try:
            data = json.loads(data)
            self._listVideos(cItem, data[0]['data']['user']['videos'])
        except Exception:
            printExc()

    def listGameVideos(self, cItem):
        printDBG("Twitch.listGameVideos")
        cursor = ',"followedCursor":"%s"' % cItem['cursor'] if 'cursor' in cItem else ''
        broadcastType = ',"broadcastTypes":["%s"]' % cItem['videos_type'].lower() if 'videos_type' in cItem else ''
        post_data = '[{"operationName":"DirectoryVideos_Game","variables":{"gameName":"%s","videoLimit":30,"languages":[]%s,"videoSort":"%s"%s},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"643351f6cff5d248aa2b827f912c80bf387b918c01089526b05d628cf04a5706"}}}]' % (cItem['game_name'], broadcastType, cItem['sort'], cursor)
        url = self.getFullUrl('/gql', self.API2_URL)
        sts, data = self.getPage(url, MergeDicts(self.defaultParams, {'raw_post_data':True}), post_data)
        if not sts: return

        try:
            data = json.loads(data)
            self._listVideos(cItem, data[0]['data']['game']['videos'])
        except Exception:
            printExc()

    def _listClips(self, cItem, clipsData):
        try:
            cursor = ''
            for item in clipsData['edges']:
                cursor = jstr(item, 'cursor')
                item = item['node']
                descTab = []

                descTab.append( jstr(item, 'language') )
                descTab.append( '{0}'.format(timedelta(seconds=item['durationSeconds'])) )
                descTab.append( _('%s viewers') % item['viewCount'] )
                descTab = [' | '.join(descTab)]

                icon = self.getFullIconUrl(jstr(item, 'thumbnailURL'), self.cm.meta['url'])
                title = '[%s] %s' % (jstr(item, 'createdAt'), jstr(item, 'title'))

                if item.get('curator'):
                    descTab.append(jstr(item['curator'], '__typename') + ': ' + jstr(item['curator'], 'displayName'))
                if item.get('broadcaster'):
                    descTab.append(jstr(item['broadcaster'], '__typename') + ': ' + jstr(item['broadcaster'], 'displayName'))
                if item.get('game'):
                    descTab.append(jstr(item['game'], '__typename') + ': ' + jstr(item['game'], 'name'))

                params = {'good_for_fav':True, 'title':title, 'url': jstr(item, 'url'), 'video_type':'clip', 'clip_slug':jstr(item, 'slug'), 'clip_id':jstr(item, 'id'), 'icon':icon, 'desc':'[/br]'.join( descTab )}
                self.addVideo(params)

            if cursor != '' and clipsData['pageInfo']['hasNextPage']:
                self.addDir( MergeDicts(cItem, {'title':_('Next page'), 'cursor':cursor}) )

        except Exception:
            printExc()

    def listClips(self, cItem):
        printDBG("Twitch.listClips")
        cursor = ',"cursor":"%s"' % cItem['cursor'] if 'cursor' in cItem else ''
        post_data = '[{"operationName":"ClipsCards__User","variables":{"login":"%s","limit":20,"criteria":{"filter":"%s"}%s},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"b661fa0b88f774135c200d64b7248ff21263c12db79e0f7d33aeedb0315cdcbb"}}}]' % (cItem['user_login'], cItem['clips_filter'], cursor)
        url = self.getFullUrl('/gql', self.API2_URL)
        sts, data = self.getPage(url, MergeDicts(self.defaultParams, {'raw_post_data':True}), post_data)
        if not sts: return

        try:
            data = json.loads(data)
            self._listClips(cItem, data[0]['data']['user']['clips'])
        except Exception:
            printExc()

    def listGameClips(self, cItem):
        printDBG("Twitch.listGameClips")
        lang = '"%s"' % cItem['lang'].upper() if 'lang' in cItem else ''
        cursor = ',"cursor":"%s"' % cItem['cursor'] if 'cursor' in cItem else ''
        post_data = '[{"operationName":"ClipsCards__Game","variables":{"gameName":"%s","limit":20,"criteria":{"languages":[%s],"filter":"%s"}%s},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"0d8d0eba9fc7ef77de54a7d933998e21ad7a1274c867ec565ac14ffdce77b1f9"}}}]' % (cItem['game_name'], lang, cItem['clips_filter'], cursor)
        url = self.getFullUrl('/gql', self.API2_URL)
        sts, data = self.getPage(url, MergeDicts(self.defaultParams, {'raw_post_data':True}), post_data)
        if not sts: return

        try:
            data = json.loads(data)
            self._listClips(cItem, data[0]['data']['game']['clips'])
        except Exception:
            printExc()

    def listSubItems(self, cItem):
        printDBG("Twitch.listSubItems")
        self.currList = cItem['sub_items']
        
    def listV5Channels(self, cItem):
        printDBG("Twitch.listV5Channels")
        offset = cItem.get('offset', 0)
        url = cItem['url'] + str(offset)
        sts, data = self.getPage(url)
        if not sts: return
        try:
            data = json.loads(data)
            for item in data['channels']:
                descTab = [_('Language: %s') % (jstr(item, 'language'))]
                descTab.append(_('%s views') % item['views'])
                descTab.append(_('%s followers') % item['followers'] )
                params = {'good_for_fav':True, 'name':'category', 'type':'category', 'category':'list_channel', 'user_login':jstr(item, 'name'), 'title':jstr(item, 'display_name'), 'icon':jstr(item, 'logo'), 'desc':'[/br]'.join(descTab)}
                self.addDir(params)
            offset += len(self.currList)
            if offset < data['_total']:
                self.addDir(MergeDicts(cItem, {'title':_('Next page'), 'offset':offset}))
        except Exception:
            printExc()

    def listV5Channels(self, cItem):
        printDBG("Twitch.listV5Channels")
        offset = cItem.get('offset', 0)
        url = cItem['url'] + str(offset)
        sts, data = self.getPage(url)
        if not sts: return
        try:
            data = json.loads(data)
            for item in data['channels']:
                descTab = [_('Language: %s') % (jstr(item, 'language'))]
                descTab.append(_('%s views') % item['views'])
                descTab.append(_('%s followers') % item['followers'] )
                params = {'good_for_fav':True, 'name':'category', 'type':'category', 'category':'list_channel', 'user_login':jstr(item, 'name'), 'title':jstr(item, 'display_name'), 'icon':jstr(item, 'logo'), 'desc':'[/br]'.join(descTab)}
                self.addDir(params)
            offset += len(self.currList)
            if offset < data['_total']:
                self.addDir(MergeDicts(cItem, {'title':_('Next page'), 'offset':offset}))
        except Exception:
            printExc()

    def listV5Games(self, cItem):
        printDBG("Twitch.listV5Games")
        offset = cItem.get('offset', 0)
        url = cItem['url'] + str(offset)
        sts, data = self.getPage(url)
        if not sts: return
        try:
            data = json.loads(data)
            for item in data['games']:
                params = {'good_for_fav':True, 'name':'category', 'type':'category', 'category':'browse_game', 'game_name':jstr(item, 'name'), 'game_id':str(item['_id']), 'title':jstr(item, 'localized_name'), 'icon':jstr(item['box'], 'medium'), 'desc':_('Popularity: %s') % item['popularity']}
                self.addDir(params)
            offset += len(self.currList)
            if offset < data.get('_total', 0):
                self.addDir(MergeDicts(cItem, {'title':_('Next page'), 'offset':offset}))
        except Exception:
            printExc()

    def listV5Streams(self, cItem):
        printDBG("Twitch.listV5Streams")
        offset = cItem.get('offset', 0)
        url = cItem['url'] + str(offset)
        sts, data = self.getPage(url)
        if not sts: return
        try:
            data = json.loads(data)
            for item in data['streams']:
                descTab = [_('Language: %s') % (jstr(item['channel'], 'broadcaster_language'))]
                descTab.append(_('%s viewers') % item['viewers'])
                descTab.append(_('Broadcaster: %s') % jstr(item['channel'], 'display_name') )
                descTab.append(_('Game: %s') % jstr(item, 'game') )
                title = '[%s] %s' % (jstr(item, 'stream_type'), jstr(item['channel'], 'status'))
                params = {'good_for_fav':False,  'title':title, 'video_type':jstr(item, 'stream_type'), 'channel_id':jstr(item['channel'], 'name'), 'icon':jstr(item['preview'], 'medium'), 'desc':'[/br]'.join(descTab)}
                self.addVideo(params)
            offset += len(self.currList)
            if offset < data['_total']:
                self.addDir(MergeDicts(cItem, {'title':_('Next page'), 'offset':offset}))
        except Exception:
            printExc()

    def listSearchResult(self, cItem, searchPattern, searchType):
        if searchType == 'channels':
            url = self.API1_URL + 'kraken/search/channels?query=%s&limit=25&offset=' % (urllib.quote_plus(searchPattern))
            cItem = MergeDicts(cItem, {'url':url, 'category':'v5_channels'})
            self.listV5Channels(cItem)
        elif searchType == 'games':
            url = self.API1_URL + 'kraken/search/games?query=%s&limit=25&offset=' % (urllib.quote_plus(searchPattern))
            cItem = MergeDicts(cItem, {'url':url, 'category':'v5_games'})
            self.listV5Games(cItem)
        elif searchType == 'streams':
            url = self.API1_URL + 'kraken/search/streams?query=%s&limit=25&offset=' % (urllib.quote_plus(searchPattern))
            cItem = MergeDicts(cItem, {'url':url, 'category':'v5_streams'})
            self.listV5Streams(cItem)
            
    def getLinksForVideo(self, cItem):
        printDBG("Twitch.getLinksForVideo [%s]" % cItem)
        urlTab = []
        
        id = ''
        if cItem['video_type'] == 'clip':
            url = 'https://clips.twitch.tv/api/v2/clips/%s/status' % cItem['clip_slug']
            sts, data = self.getPage(url)
            if not sts: return urlTab
            try:
                data = byteify(json.loads(data))
                for item in data['quality_options']:
                    urlTab.append({'name':'%sp, %sfps' % (item['quality'], item['frame_rate']), 'url':item['source'], 'need_resolve':0})
            except Exception:
                printExc()
        elif cItem['video_type'] == 'live':
            id = cItem['channel_id']
            tokenUrl = self.CHANNEL_TOKEN_URL
            vidUrl   = self.LIVE_URL
            liveStream = True
        else:
            id = cItem.get('video_id', '')
            tokenUrl = self.VOD_TOKEN_URL
            vidUrl   = self.VOD_URL
            liveStream = False

        if id != '':
            url = tokenUrl % id
            sts, data = self.getPage(url)
            if sts:
                try:
                    data = json.loads(data)
                    url =  vidUrl % (id, urllib.quote(jstr(data, 'token')), jstr(data, 'sig'))
                    data = getDirectM3U8Playlist(url, checkExt=False)
                    for item in data:
                        item['url'] = urlparser.decorateUrl(item['url'], {'iptv_proto':'m3u8', 'iptv_livestream':liveStream})
                        urlTab.append(item)
                except Exception: printExc()

        return urlTab

    def handleService(self, index, refresh = 0, searchPattern = '', searchType = ''):
        printDBG('handleService start')
        
        CBaseHostClass.handleService(self, index, refresh, searchPattern, searchType)

        name     = self.currItem.get("name", '')
        category = self.currItem.get("category", '')
        printDBG( "handleService: ||| name[%s], category[%s] " % (name, category) )
        self.currList = []

    #MAIN MENU
        if name == None:
            self.listMain({'name':'category', 'type':'category'})

        elif category == 'browse':
            self.listDirectories(self.currItem)

        elif category == 'sub_items':
            self.listSubItems(self.currItem)

        elif category == 'dir_channels':
            self.listDirChannels(self.currItem, 'list_channel')
        elif category == 'list_channel':
            self.listChannel(self.currItem)

        elif category == 'videos_types':
            self.listsTab(self.VIDEOS_TYPES_TAB, MergeDicts(self.currItem, {'category':'videos_sort'}))
        elif category == 'videos_sort':
            self.listsTab(self.VIDEOS_SORT_TAB, MergeDicts(self.currItem, {'category':'list_videos'}))
        elif category == 'list_videos':
            self.listVideos(self.currItem)

        elif category == 'clips_filters':
            self.listsTab(self.CLIPS_FILTERS_TAB, MergeDicts(self.currItem, {'category':'list_clips'}))
        elif category == 'list_clips':
            self.listClips(self.currItem)

        elif category == 'dir_games':
            self.listDirGames(self.currItem, 'browse_game')
        elif category == 'browse_game':
           self.listsTab(self.GAME_CAT_TAB, self.currItem)
        elif category == 'game_lang':
            self.listsTab(self.langItems, MergeDicts(self.currItem, {'category':self.currItem['next_category']}))
        elif category == 'game_channels':
            self.listGameChannels(self.currItem, 'list_channel')

        elif category == 'game_videos_types':
            self.listsTab(self.VIDEOS_TYPES_TAB, MergeDicts(self.currItem, {'category':'game_videos_sort'}))
        elif category == 'game_videos_sort':
            self.listsTab(self.VIDEOS_SORT_TAB, MergeDicts(self.currItem, {'category':'game_list_videos'}))
        elif category == 'game_list_videos':
            self.listGameVideos(self.currItem)
            
        elif category == 'game_clips_filters':
            self.listsTab(self.CLIPS_FILTERS_TAB, MergeDicts(self.currItem, {'category':'game_list_clips'}))
        elif category == 'game_list_clips':
            self.listGameClips(self.currItem)

        elif category == 'v5_channels':
            self.listV5Channels(self.currItem)
        elif category == 'v5_games':
            self.listV5Games(self.currItem)
        elif category == 'v5_streams':
            self.listV5Streams(self.currItem)

    #SEARCH
        elif category in ["search", "search_next_page"]:
            cItem = dict(self.currItem)
            cItem.update({'search_item':False, 'name':'category'}) 
            self.listSearchResult(cItem, searchPattern, searchType)
    #HISTORIA SEARCH
        elif category == "search_history":
            self.listsHistory({'name':'history', 'category': 'search'}, 'desc', _("Type: "))
        else:
            printExc()
        
        CBaseHostClass.endHandleService(self, index, refresh)

class IPTVHost(CHostBase):

    def __init__(self):
        CHostBase.__init__(self, Twitch(), True, [])

    def getSearchTypes(self):
        searchTypesOptions = []
        searchTypesOptions.append((_("Games"), "games"))
        searchTypesOptions.append((_("Live streams"), "streams"))
        searchTypesOptions.append((_("Channles"), "channels"))
        return searchTypesOptions
