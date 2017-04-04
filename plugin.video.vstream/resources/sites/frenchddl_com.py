#-*- coding: utf-8 -*-
#Venom.
from resources.lib.gui.hoster import cHosterGui
from resources.lib.gui.gui import cGui
from resources.lib.handler.inputParameterHandler import cInputParameterHandler
from resources.lib.handler.outputParameterHandler import cOutputParameterHandler
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.config import cConfig
from resources.lib.parser import cParser
import re


SITE_IDENTIFIER = 'frenchddl_com'
SITE_NAME = 'FrenchDDL'
SITE_DESC = 'films en ddl'

URL_MAIN = 'http://www.frenchddl.com/'

URL_SEARCH = ('http://www.frenchddl.com/index.php?Query=', 'showMovies')
FUNCTION_SEARCH = 'showMovies'

MOVIE_MOVIE = (URL_MAIN , 'showMovies')
MOVIE_GENRES = (True, 'showGenres')

def load():
    oGui = cGui()

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', 'http://venom/')
    oGui.addDir(SITE_IDENTIFIER, 'showSearch', 'Recherche', 'search.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', MOVIE_MOVIE[0])
    oGui.addDir(SITE_IDENTIFIER, MOVIE_MOVIE[1], 'Films', 'films.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', MOVIE_GENRES[0])
    oGui.addDir(SITE_IDENTIFIER, MOVIE_GENRES[1], 'Films (Genres)', 'films_genres.png', oOutputParameterHandler)

    oGui.setEndOfDirectory()

def showSearch():
    oGui = cGui()

    sSearchText = oGui.showKeyBoard()
    if (sSearchText != False):
        sUrl = URL_SEARCH[0] + sSearchText
        showMovies(sUrl)
        oGui.setEndOfDirectory()
        return

def showGenres():
    oGui = cGui()

    oRequestHandler = cRequestHandler(URL_MAIN)
    sHtmlContent = oRequestHandler.request()
    sHtmlContent = sHtmlContent.decode('iso-8859-1').encode('utf8') # Site en latin1
    sPattern = '<td class="GenresCell"><a href=(.+?) class.+?>(.+?)</a></td>'

    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)

    liste = []
    if aResult[0]:
        for aEntry in aResult[1]:
            title = aEntry[1].replace('&eacute;', 'é')
            liste.append( [title,URL_MAIN + aEntry[0]] )

    for sTitle,sUrl in liste:#boucle

        oOutputParameterHandler = cOutputParameterHandler()
        oOutputParameterHandler.addParameter('siteUrl', sUrl)
        oGui.addDir(SITE_IDENTIFIER, 'showMovies', sTitle, 'genres.png', oOutputParameterHandler)

    oGui.setEndOfDirectory()

def showMovies(sSearch = ''):
    oGui = cGui()
    
    bGlobal_Search = False
    
    if sSearch:
        sUrl = sSearch
      
        if URL_SEARCH[0] in sSearch:
            bGlobal_Search = True
      
    else:
        oInputParameterHandler = cInputParameterHandler()
        sUrl = oInputParameterHandler.getValue('siteUrl')

    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()
    sHtmlContent = sHtmlContent.decode('iso-8859-1').encode('utf8') # Site en latin1

    sPattern = '<td class="FilmsTitre">(.+?)</tr>.+?<a href="([^"]+?)"><img src="(.+?)"'

    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)

    if (aResult[0] == True):
        total = len(aResult[1])

        dialog = cConfig().createDialog(SITE_NAME)

        for aEntry in aResult[1]:
            sTitle = re.sub('<[^<]+?>', '', aEntry[0])
            sUrl = URL_MAIN + '/' + aEntry[1]
            sThumbnail = aEntry[2]
            cConfig().updateDialog(dialog, total)

            oOutputParameterHandler = cOutputParameterHandler()
            oOutputParameterHandler.addParameter('siteUrl', sUrl) 
            oOutputParameterHandler.addParameter('sMovieTitle', sTitle)
            oOutputParameterHandler.addParameter('sThumbnail', sThumbnail)

            oGui.addMovie(SITE_IDENTIFIER, 'showHosters', sTitle, '', sThumbnail, sUrl, oOutputParameterHandler)

        cConfig().finishDialog(dialog)
        
        sNextPage = __checkForNextPage(sHtmlContent)
        
        if (sNextPage != False):
            oOutputParameterHandler = cOutputParameterHandler()
            oOutputParameterHandler.addParameter('siteUrl', sNextPage)
            oGui.addDir(SITE_IDENTIFIER, 'showMovies', '[COLOR teal]Next >>>[/COLOR]', 'next.png', oOutputParameterHandler)


    if not sSearch:
        oGui.setEndOfDirectory()


def __checkForNextPage(sHtmlContent):
    oParser = cParser()
    sPattern = '<a href="([^"]+?)">></a>';
    aResult = oParser.parse(sHtmlContent, sPattern)

    if (aResult[0] == True):
        return aResult[1][0]

    return False


def showHosters():
    oGui = cGui()
    oInputParameterHandler = cInputParameterHandler()
    sUrl = oInputParameterHandler.getValue('siteUrl')
    sMovieTitle = oInputParameterHandler.getValue('sMovieTitle')
    sThumbnail = oInputParameterHandler.getValue('sThumbnail')

    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()
    sHtmlContent = sHtmlContent.decode('iso-8859-1').encode('utf8') # Site en latin1

    oParser = cParser()
    sPattern = '<a href="([^"]+?)".+?>T.+?<td align=\'center\' class=\'TextLink\'>(.+?)</td>.*?<td align=\'center\' class=\'TextLink\'>(.+?)</td>.*?<td align=\'center\' class=\'TextLink\'>(.+?)</td>.*?<td align=\'center\' class=\'TextLink\'>(.+?)</td>'
    aResult = oParser.parse(sHtmlContent, sPattern)
    
    oGui.addText(SITE_IDENTIFIER,'[COLOR olive]' + sMovieTitle + '[/COLOR]')

    if (aResult[0] == True):
        for aEntry in aResult[1]:

            sHosterUrl = str(aEntry[0])
            sLang = str(aEntry[1]).upper()
            sType = str(aEntry[2]).upper()
            sFmt = str(aEntry[3]).upper()
            sSize = str(aEntry[4]).upper()
            sDisplay = '[COLOR teal]['+sType+']['+sLang+']['+sType+']['+sSize+'][/COLOR]'

            oHoster = cHosterGui().checkHoster(sHosterUrl)
            if (oHoster != False):
                oHoster.setDisplayName(sDisplay)
                oHoster.setFileName(sMovieTitle)
                cHosterGui().showHoster(oGui, oHoster, sHosterUrl, sThumbnail)

    oGui.setEndOfDirectory()
