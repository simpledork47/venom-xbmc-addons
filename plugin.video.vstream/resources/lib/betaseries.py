#-*- coding: utf-8 -*-
#Venom.
from resources.lib.config import cConfig
from resources.lib.db import cDb
from resources.lib.gui.gui import cGui
from resources.lib.gui.guiElement import cGuiElement
from resources.lib.gui.hoster import cHosterGui
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.handler.inputParameterHandler import cInputParameterHandler
from resources.lib.handler.outputParameterHandler import cOutputParameterHandler

import urllib, urllib2, re
import xbmc
import time, md5
import unicodedata

import datetime, time

try:    import json
except: import simplejson as json

SITE_IDENTIFIER = 'cBseries'
SITE_NAME = 'Betaseries'

API_KEY = '7139b7dace25c7bdf0bd79acf46fb02bd63310548b1f671d88832f75a4ac3dd6'
API_SECRET = 'bb02b2b0267b045590bc25c21dac21b1c47446a62b792091b3275e9c4a943e74'
API_VERS = '2'
API_URL = 'https://api.betaseries.com'

POSTER_URL = 'https://image.tmdb.org/t/p/w396'
#FANART_URL = 'https://image.tmdb.org/t/p/w780/'
FANART_URL = 'https://image.tmdb.org/t/p/w1280'

class cBseries:

    CONTENT = '0'

    def __init__(self):
        #self.__sFile = cConfig().getFileFav()
        self.__sTitle = ''
        self.__sAction = ''
        #self.__sFunctionName = ''


    def getToken(self):

        headers = {'Content-Type': 'application/json'}
        post = {'client_id': API_KEY}
        post = json.dumps(post)


        req = urllib2.Request('https://api.trakt.tv/oauth/device/code', post,headers)
        response = urllib2.urlopen(req)
        sHtmlContent = response.read()
        result = json.loads(sHtmlContent)
       # xbmc.log(str(result))
        response.close()

        #{"device_code":"a434135042b5a76159628bc974eed2f266fb47df9f438d5738ce40396d531490","user_code":"EBDFD843","verification_url":"https://trakt.tv/activate","expires_in":600,"interval":5}

        total = len(sHtmlContent)

        xbmc.log(str(sHtmlContent))

        if (total > 0):
            #self.__Token  = result['token']
            sText = (cConfig().getlanguage(30304)) % (result['verification_url'], result['user_code'])
            dialog = cConfig().createDialog('vStream')
            dialog.update(0, sText)

            for i in range(0, result['expires_in']):
                try:
                    dialog.update(i)
                    time.sleep(1)
                    if dialog.iscanceled():
                        break

                    headers = {'Content-Type': 'application/json'}
                    post = {'client_id': API_KEY, 'client_secret': API_SECRET, 'code': result['device_code']}
                    post = json.dumps(post)

                    req = urllib2.Request('https://api.trakt.tv/oauth/device/token', post,headers)
                    response = urllib2.urlopen(req)
                    sHtmlContent = response.read()
                    result = json.loads(sHtmlContent)
                    response.close()

                    if result['access_token']:
                        cConfig().setSetting('bstoken', str(result['access_token']))
                        break

                except:
                    pass
            cConfig().finishDialog(dialog)

            #xbmc.executebuiltin("Container.Refresh")
            return
        return False

    def getLoad(self):

        #self.getToken()
        oGui = cGui()

        if cConfig().getSetting("bstoken") == '':
            oOutputParameterHandler = cOutputParameterHandler()
            oOutputParameterHandler.addParameter('siteUrl', 'https://')
            oOutputParameterHandler.addParameter('type', 'movie')
            oGui.addDir(SITE_IDENTIFIER, 'getToken()', cConfig().getlanguage(30305), 'mark.png', oOutputParameterHandler)
        else:

            #nom de luser
            headers = {'Content-Type': 'application/json', 'trakt-api-key': API_KEY, 'trakt-api-version': API_VERS, 'Authorization': 'Bearer %s' % cConfig().getSetting("bstoken")}
            #post = {'client_id': API_KEY, 'client_secret': API_SECRET, 'code': result['device_code']}
            #post = json.dumps(post)

            req = urllib2.Request('https://api.trakt.tv/users/me', None,headers)
            response = urllib2.urlopen(req)
            sHtmlContent = response.read()
            result = json.loads(sHtmlContent)
            response.close()
            total = len(sHtmlContent)

            #stats user
            req2 = urllib2.Request('https://api.trakt.tv/users/me/stats', None,headers)
            response2 = urllib2.urlopen(req2)
            sHtmlContent2 = response2.read()
            result2 = json.loads(sHtmlContent2)
            response2.close()
            total2 = len(sHtmlContent2)
            #xbmc.log(str(result2))


            if (total > 0):
                sUsername = result['username']
                oOutputParameterHandler = cOutputParameterHandler()
                oOutputParameterHandler.addParameter('siteUrl', 'https://')
                oGui.addText(SITE_IDENTIFIER, (cConfig().getlanguage(30306)) % (sUsername), oOutputParameterHandler)

            sTitle = (cConfig().getlanguage(30307)) % (result2['movies']['plays'], result2['movies']['watched'], result2['movies']['minutes'], result2['shows']['watched'], result2['episodes']['plays'], result2['episodes']['watched'], result2['episodes']['minutes'])
            oOutputParameterHandler = cOutputParameterHandler()
            oOutputParameterHandler.addParameter('siteUrl', 'https://')
            oGui.addText(SITE_IDENTIFIER, '[COLOR white]'+sTitle+'[/COLOR]', oOutputParameterHandler)

            oOutputParameterHandler = cOutputParameterHandler()
            oOutputParameterHandler.addParameter('siteUrl', 'https://')
            oOutputParameterHandler.addParameter('type', 'movie')
            oGui.addDir(SITE_IDENTIFIER, 'getLists', cConfig().getlanguage(30120), 'films.png', oOutputParameterHandler)

            oOutputParameterHandler = cOutputParameterHandler()
            oOutputParameterHandler.addParameter('siteUrl', 'https://')
            oOutputParameterHandler.addParameter('type', 'show')
            oGui.addDir(SITE_IDENTIFIER, 'getLists', cConfig().getlanguage(30121), 'series.png', oOutputParameterHandler)

            oOutputParameterHandler = cOutputParameterHandler()
            oOutputParameterHandler.addParameter('siteUrl', 'https://api.trakt.tv/users/me/history')
            oGui.addDir(SITE_IDENTIFIER, 'getBseries', cConfig().getlanguage(30308), 'mark.png', oOutputParameterHandler)

            # oOutputParameterHandler = cOutputParameterHandler()
            # oOutputParameterHandler.addParameter('siteUrl', 'https://api.trakt.tv/users/me/watching')
            # oGui.addDir(SITE_IDENTIFIER, 'getBseries', 'Actuellement', 'mark.png', oOutputParameterHandler)

            oOutputParameterHandler = cOutputParameterHandler()
            oOutputParameterHandler.addParameter('siteUrl', 'https://api.trakt.tv/oauth/revoke')
            oGui.addDir(SITE_IDENTIFIER, 'getBsout', cConfig().getlanguage(30309), 'mark.png', oOutputParameterHandler)



        oGui.setEndOfDirectory()

    def getLists(self):

        oInputParameterHandler = cInputParameterHandler()
        sType = oInputParameterHandler.getValue('type')

        oGui = cGui()

        liste = []
        if sType == 'movie':
            liste.append( [cConfig().getlanguage(30310),'https://api.trakt.tv/users/me/collection/movies'] )
            liste.append( [cConfig().getlanguage(30311),'https://api.trakt.tv/users/me/watchlist/movies'] )
            liste.append( [cConfig().getlanguage(30312),'https://api.trakt.tv/users/me/watched/movies'] )
            liste.append( [cConfig().getlanguage(30313),'https://api.trakt.tv/recommendations/movies'] )
            liste.append( [cConfig().getlanguage(30314),'https://api.trakt.tv/movies/boxoffice'] )
            liste.append( [cConfig().getlanguage(30315),'https://api.trakt.tv/movies/popular'] )
            liste.append( [cConfig().getlanguage(30316),'https://api.trakt.tv/movies/played/weekly'] )
            liste.append( [cConfig().getlanguage(30317),'https://api.trakt.tv/movies/played/monthly'] )
            #liste.append( ['historique de Films','https://api.trakt.tv/users/me/history/movies'] )

        elif sType == 'show':
            liste.append( [cConfig().getlanguage(30310),'https://api.trakt.tv/users/me/collection/shows'] )
            liste.append( [cConfig().getlanguage(30311),'https://api.trakt.tv/users/me/watchlist/shows'] )
            liste.append( [cConfig().getlanguage(30318),'https://api.trakt.tv/users/me/watchlist/seasons'] )
            liste.append( [cConfig().getlanguage(30319),'https://api.trakt.tv/users/me/watchlist/episodes'] )
            liste.append( [cConfig().getlanguage(30312),'https://api.trakt.tv/users/me/watched/shows'] )
            liste.append( [cConfig().getlanguage(30313),'https://api.trakt.tv/recommendations/shows'] )
            liste.append( [cConfig().getlanguage(30315),'https://api.trakt.tv/shows/popular'] )
            liste.append( [cConfig().getlanguage(30316),'https://api.trakt.tv/shows/played/weekly'] )
            liste.append( [cConfig().getlanguage(30317),'https://api.trakt.tv/shows/played/monthly'] )
            #liste.append( ['Historique de séries','https://api.trakt.tv/users/me/history/shows'] )

        for sTitle,sUrl in liste:

            oOutputParameterHandler = cOutputParameterHandler()
            oOutputParameterHandler.addParameter('siteUrl', sUrl)
            oGui.addDir(SITE_IDENTIFIER, 'getBseries', sTitle, 'genres.png', oOutputParameterHandler)


        oGui.setEndOfDirectory()

    def getBsout(self):

        oInputParameterHandler = cInputParameterHandler()
        sUrl = oInputParameterHandler.getValue('siteUrl')

        oGui = cGui()

        headers = {'Content-Type': 'application/x-www-form-urlencoded', 'trakt-api-key': API_KEY, 'trakt-api-version': API_VERS, 'Authorization': 'Bearer %s' % cConfig().getSetting("bstoken")}
        post = {'token': cConfig().getSetting("bstoken")}
        post = json.dumps(post)

        req = urllib2.Request(sUrl, post,headers)
        response = urllib2.urlopen(req)
        sHtmlContent = response.read()
        result = json.loads(sHtmlContent)
        response.close()
        total = len(sHtmlContent)

        if (total > 0):
            cConfig().setSetting('bstoken', '')
            oGui.showNofication(cConfig().getlanguage(30320))
            xbmc.executebuiltin("Container.Refresh")

        return


    def getBseries(self):

        oInputParameterHandler = cInputParameterHandler()
        sUrl = oInputParameterHandler.getValue('siteUrl')

        oGui = cGui()

        headers = {'Content-Type': 'application/json', 'trakt-api-key': API_KEY, 'trakt-api-version': API_VERS, 'Authorization': 'Bearer %s' % cConfig().getSetting("bstoken")}
        #post = {'extended': 'metadata'}
        # post = json.dumps(post)
        req = urllib2.Request(sUrl, None,headers)
        response = urllib2.urlopen(req)
        sHtmlContent = response.read()
        result = json.loads(sHtmlContent)
        #xbmc.log(str(result))

        response.close()
        total = len(sHtmlContent)
        sKey = 0
        if (total > 0):
            for i in result:

                if 'collection' in sUrl:
                    if  'show' in i:
                        sTrakt, sTitle, sYear, sTmdb, sDate = i['show']['ids']['trakt'], i['show']['title'], i['show']['year'], i['show']['ids']['tmdb'], i['last_collected_at']
                        sDate = datetime.datetime(*(time.strptime(sDate, "%Y-%m-%dT%H:%M:%S.%fZ")[0:6])).strftime('%d-%m-%Y %H:%M')
                        cBseries.CONTENT = '2'
                    else:
                        sTrakt, sTitle, sYear, sTmdb, sDate = i['movie']['ids']['trakt'], i['movie']['title'], i['movie']['year'], i['movie']['ids']['tmdb'], i['collected_at']
                        sDate = datetime.datetime(*(time.strptime(sDate, "%Y-%m-%dT%H:%M:%S.%fZ")[0:6])).strftime('%d-%m-%Y %H:%M')
                        cBseries.CONTENT = '1'

                    sFile = ('%s - (%s)') % (sTitle.encode("utf-8"), int(sYear))
                    sTitle = ('[COLOR white]%s[/COLOR] %s - (%s)') % (sDate, sTitle.encode("utf-8"), int(sYear))

                elif 'history' in sUrl:
                #commun
                    sAction, sType, sWatched_at  = i['action'], i['type'], i['watched_at']
                    #2016-11-16T09:21:18.000Z
                    sDate = datetime.datetime(*(time.strptime(sWatched_at, "%Y-%m-%dT%H:%M:%S.%fZ")[0:6])).strftime('%d-%m-%Y %H:%M')
                    if 'episode' in i:
                        sTrakt, sTitle, sTmdb, sSeason, sNumber = i['episode']['ids']['trakt'], i['episode']['title'], i['episode']['ids']['tmdb'], i['episode']['season'],  i['episode']['number']
                        sExtra = ('(S%sEP%s)') % (sSeason, sNumber)
                        cBseries.CONTENT = '2'
                    else:
                        sTrakt, sTitle, sTmdb, sYear = i['movie']['ids']['trakt'], i['movie']['title'], i['movie']['ids']['tmdb'], i['movie']['year']
                        sExtra = ('(%s)') % (sYear)
                        cBseries.CONTENT = '1'

                    sTitle = unicodedata.normalize('NFD',  sTitle).encode('ascii', 'ignore').decode("unicode_escape")
                    sTitle.encode("utf-8")
                    sFile = ('%s - (%s)') % (sTitle.encode("utf-8"), sExtra)
                    sTitle = ('[COLOR white]%s - %s %s[/COLOR] - %s %s') % (sDate, sAction, sType, sTitle, sExtra )


                elif 'watchlist' in sUrl:
                    #commun
                    sType, sListed_at  = i['type'], i['listed_at']
                    #2016-11-16T09:21:18.000Z
                    sDate = datetime.datetime(*(time.strptime(sListed_at, "%Y-%m-%dT%H:%M:%S.%fZ")[0:6])).strftime('%d-%m-%Y %H:%M')
                    if  'show' in i:
                        sTrakt, sTitle, sYear, sTmdb = i['show']['ids']['trakt'], i['show']['title'], i['show']['year'], i['show']['ids']['tmdb']
                        sExtra = ('(%s)') % (sYear)
                        cBseries.CONTENT = '2'
                    elif 'episode' in i:
                        sTrakt, sTitle, sTmdb, sSeason, sNumber = i['episode']['ids']['trakt'], i['episode']['title'], i['episode']['ids']['tmdb'], i['episode']['season'],  i['episode']['number']
                        sExtra = ('(S%sEP%s)') % (sSeason, sNumber)
                        cBseries.CONTENT = '2'
                    else:
                        sTrakt, sTitle, sTmdb, sYear = i['movie']['ids']['trakt'], i['movie']['title'], i['movie']['ids']['tmdb'], i['movie']['year']
                        sExtra = ('(%s)') % (sYear)
                        cBseries.CONTENT = '1'

                    sTitle = unicodedata.normalize('NFD',  sTitle).encode('ascii', 'ignore').decode("unicode_escape")
                    sTitle.encode("utf-8")
                    sFile = ('%s - (%s)') % (sTitle.encode("utf-8"), sExtra)
                    sTitle = ('[COLOR white]%s - %s[/COLOR] - %s %s') % (sDate, sType, sTitle, sExtra )


                elif 'watched' in sUrl:
                #commun
                    sLast_watched_at, sPlays  = i['last_watched_at'], i['plays']
                    #2016-11-16T09:21:18.000Z
                    sDate = datetime.datetime(*(time.strptime(sLast_watched_at, "%Y-%m-%dT%H:%M:%S.%fZ")[0:6])).strftime('%d-%m-%Y %H:%M')
                    if  'show' in i:
                        sTrakt, sTitle, sYear, sTmdb = i['show']['ids']['trakt'], i['show']['title'], i['show']['year'], i['show']['ids']['tmdb']
                        cBseries.CONTENT = '2'
                    else:
                        sTrakt, sTitle, sTmdb, sYear = i['movie']['ids']['trakt'], i['movie']['title'], i['movie']['ids']['tmdb'], i['movie']['year']
                        cBseries.CONTENT = '1'

                    sTitle = unicodedata.normalize('NFD',  sTitle).encode('ascii', 'ignore').decode("unicode_escape")
                    sTitle.encode("utf-8")
                    sFile = ('%s - (%s)') % (sTitle.encode("utf-8"), sYear)
                    sTitle = ('[COLOR white]%s - %s Lectures[/COLOR] - %s (%s)') % (sDate, sPlays, sTitle, sYear )

                elif 'played' in sUrl:
                #commun
                    sWatcher_count, sPlay_count, sCollected_count = i['watcher_count'], i['play_count'], i['collected_count']
                    if  'show' in i:
                        sTrakt, sTitle, sYear, sTmdb = i['show']['ids']['trakt'], i['show']['title'], i['show']['year'], i['show']['ids']['tmdb']
                        cBseries.CONTENT = '2'
                    else:
                        sTrakt, sTitle, sTmdb, sYear = i['movie']['ids']['trakt'], i['movie']['title'], i['movie']['ids']['tmdb'], i['movie']['year']
                        cBseries.CONTENT = '1'
                    sFile = ('%s - (%s)') % (sTitle.encode("utf-8"), int(sYear))
                    sTitle = ('Spectateur [COLOR white](%s)[/COLOR] - Collection [COLOR white](%s)[/COLOR] - %s - (%s)') % (int(sPlay_count), int(sCollected_count), sTitle.encode("utf-8"), int(sYear))


                elif 'recommendations' in sUrl or 'popular' in sUrl:
                    if 'shows' in sUrl:
                        cBseries.CONTENT = '2'
                    else :
                        cBseries.CONTENT = '1'
                    sTrakt, sTitle, sYear, sTmdb = i['ids']['trakt'], i['title'], i['year'], i['ids']['tmdb']
                    sFile = ('%s - (%s)') % (sTitle.encode("utf-8"), int(sYear))
                    sTitle = ('%s - (%s)') % (sTitle.encode("utf-8"), int(sYear))

                elif 'boxoffice' in sUrl:
                        sTrakt, sTitle, sYear, sTmdb, sRevenue = i['movie']['ids']['trakt'], i['movie']['title'], i['movie']['year'], i['movie']['ids']['tmdb'], i['revenue']
                        cBseries.CONTENT = '1'
                        sFile = ('%s - (%s)') % (sTitle.encode("utf-8"), int(sYear))
                        sTitle = ('Revenues [COLOR white](%s)[/COLOR] - %s - (%s)') % (sRevenue, sTitle.encode("utf-8"), int(sYear))



                else: return

                oOutputParameterHandler = cOutputParameterHandler()
                oOutputParameterHandler.addParameter('siteUrl', sUrl)
                oOutputParameterHandler.addParameter('file', sFile)
                oOutputParameterHandler.addParameter('key', sKey)
                self.getFolder(oGui, sTitle, sFile, 'getBseasons', sTmdb, oOutputParameterHandler)
                sKey += 1
        oGui.setEndOfDirectory()
        return

    def getBseasons(self):

        oInputParameterHandler = cInputParameterHandler()
        sUrl = oInputParameterHandler.getValue('siteUrl')
        sFile = oInputParameterHandler.getValue('file')
        sKey = oInputParameterHandler.getValue('key')

        oGui = cGui()

        headers = {'Content-Type': 'application/json', 'trakt-api-key': API_KEY, 'trakt-api-version': API_VERS, 'Authorization': 'Bearer %s' % cConfig().getSetting("bstoken")}
        #post = {'extended': 'metadata'}
        # post = json.dumps(post)

        req = urllib2.Request(sUrl, None,headers)
        response = urllib2.urlopen(req)
        sHtmlContent = response.read()
        result = json.loads(sHtmlContent)

        response.close()
        total = len(sHtmlContent)

        oGui = cGui()

        total = len(result)
        sNum = 0
        if (total > 0):
            for i in result[int(sKey)]['seasons']:

                if 'collection' in sUrl or 'watched' in sUrl:
                    sNumber = i['number']
                    cBseries.CONTENT = '2'
                else: return

                sTitle2 = ('%s - (S%s)') % (sFile.encode("utf-8"), int(sNumber))
                oOutputParameterHandler = cOutputParameterHandler()
                oOutputParameterHandler.addParameter('siteUrl', sUrl)
                oOutputParameterHandler.addParameter('Key', sKey)
                oOutputParameterHandler.addParameter('sNum', sNum)
                oOutputParameterHandler.addParameter('file', sFile)
                oOutputParameterHandler.addParameter('title', sTitle2)
                self.getFolder(oGui, sTitle2, sFile, 'getBepisodes', '', oOutputParameterHandler)
                sNum += 1

        oGui.setEndOfDirectory()
        return

    def getBepisodes(self):

        oInputParameterHandler = cInputParameterHandler()
        sUrl = oInputParameterHandler.getValue('siteUrl')
        sTitle = oInputParameterHandler.getValue('title')
        sFile = oInputParameterHandler.getValue('file')
        sKey = oInputParameterHandler.getValue('key')
        sNum = oInputParameterHandler.getValue('sNum')

        oGui = cGui()
        cBseries.CONTENT = '2'

        headers = {'Content-Type': 'application/json', 'trakt-api-key': API_KEY, 'trakt-api-version': API_VERS, 'Authorization': 'Bearer %s' % cConfig().getSetting("bstoken")}
        #post = {'extended': 'metadata'}
        # post = json.dumps(post)

        req = urllib2.Request(sUrl, None,headers)
        response = urllib2.urlopen(req)
        sHtmlContent = response.read()
        result = json.loads(sHtmlContent)

        response.close()
        total = len(sHtmlContent)

        oGui = cGui()
        #xbmc.log(str(sKey))
        total = len(result)
        if (total > 0):
            for i in result[int(sKey)]['seasons'][int(sNum)]['episodes']:

                if 'collection' in sUrl:
                    sNumber, sDate = i['number'],  i['collected_at']
                    sDate = datetime.datetime(*(time.strptime(sDate, "%Y-%m-%dT%H:%M:%S.%fZ")[0:6])).strftime('%d-%m-%Y %H:%M')

                    sTitle2 = ('[COLOR white]%s [/COLOR] %s - (ep%s)') % (sDate, sTitle.encode("utf-8"), int(sNumber))

                elif 'watched' in sUrl:
                    sNumber, sPlays, sDate = i['number'], i['plays'], i['last_watched_at']
                    sDate = datetime.datetime(*(time.strptime(sDate, "%Y-%m-%dT%H:%M:%S.%fZ")[0:6])).strftime('%d-%m-%Y %H:%M')

                    sTitle2 = ('[COLOR white]%s - %s Lectures[/COLOR] - %s - (ep%s)') % (sDate, sPlays, sTitle.encode("utf-8"), int(sNumber))

                else: return

                oOutputParameterHandler = cOutputParameterHandler()
                oOutputParameterHandler.addParameter('siteUrl', sUrl)
                #oOutputParameterHandler.addParameter('Key', skey)
                self.getFolder(oGui, sTitle2, sFile, 'load', '', oOutputParameterHandler)

        oGui.setEndOfDirectory()
        return

    def getFolder(self, oGui, sTitle, sFile, sFunction, sTmdb, oOutputParameterHandler):

        oGuiElement = cGuiElement()

        oGuiElement.setSiteName(SITE_IDENTIFIER)
        oGuiElement.setFunction(sFunction)
        oGuiElement.setTitle(sTitle)
        oGuiElement.setFileName(sFile)
        oGuiElement.setIcon("mark.png")
        #oGuiElement.setThumbnail(sThumb)
        oGuiElement.setTmdb(sTmdb)
        oGuiElement.setImdbId(sTmdb)

        #self.getTmdb(sTmdb, oGuiElement)
        #xbmc.log(str(cBseries.CONTENT))
        if cBseries.CONTENT == '2':
            oGuiElement.setMeta(2)
        else:
            oGuiElement.setMeta(1)

        #oGuiElement.setDescription(sDesc)
        #oGuiElement.setFanart(fanart)

        #oGui.createContexMenuDelFav(oGuiElement, oOutputParameterHandler)

         #oGui.addHost(oGuiElement, oOutputParameterHandler)
        oGui.addFolder(oGuiElement, oOutputParameterHandler)
        #oGui.addDir(SITE_IDENTIFIER, 'showMovies', sTitle, 'next.png', oOutputParameterHandler)



    def getContext(self):

        import xbmcgui
        disp = ['https://api.trakt.tv/sync/collection/','https://api.trakt.tv/sync/history','https://api.trakt.tv/sync/watchlist']
        dialog2 = xbmcgui.Dialog()
        dialog_select = cConfig().getlanguage(30321), cConfig().getlanguage(30322), cConfig().getlanguage(30323)

        ret = dialog2.select('Trakt',dialog_select)

        if ret > -1:
            self.__sAction = disp[ret]
        return self.__sAction

    def getAction(self):

        sAction = self.getContext()
        if not sAction:
            return

        oGuiElement = cGuiElement()
        sId = oGuiElement.getTmdb()
        oInputParameterHandler = cInputParameterHandler()
        aParams = oInputParameterHandler.getAllParameter()
        sImdb = oInputParameterHandler.getValue('sImdb')

        headers = {'Content-Type': 'application/json', 'trakt-api-key': API_KEY, 'trakt-api-version': API_VERS, 'Authorization': 'Bearer %s' % cConfig().getSetting("bstoken")}
        #sUrl =  ('%s%s') % (sAction, str(sImdb))
        sPost = {"movies": [{"ids": {"imdb": sImdb}}]}
        sPost = json.dumps(sPost)

        req = urllib2.Request(sAction, sPost,headers)
        response = urllib2.urlopen(req)
        sHtmlContent = response.read()
        result = json.loads(sHtmlContent)
        xbmc.log(str(result))


        return

    def getTmdb(self, sTmdb, oGuiElement):

        oRequestHandler = cRequestHandler('https://api.themoviedb.org/3/movie/'+str(sTmdb))
        oRequestHandler.addParameters('api_key', '92ab39516970ab9d86396866456ec9b6')
        oRequestHandler.addParameters('language', 'fr')

        sHtmlContent = oRequestHandler.request()
        result = json.loads(sHtmlContent)
        #xbmc.log(str(result))

        total = len(sHtmlContent)
        #format
        meta = {}
        meta['imdb_id'] = result['id']
        meta['title'] = result['title']
        meta['tagline'] = result['tagline']
        meta['rating'] = result['vote_average']
        meta['votes'] = result['vote_count']
        meta['duration'] = result['runtime']
        meta['plot'] = result['overview']
        #meta['mpaa'] = result['certification']
        #meta['premiered'] = result['released']
        #meta['director'] = result['director']
        #meta['writer'] = result['writer']
        # if (total > 0):

        for key, value in meta.items():
            oGuiElement.addItemValues(key, value)

        return
