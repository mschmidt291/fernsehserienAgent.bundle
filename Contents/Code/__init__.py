import re
import json
import requests
import time
import tvdb_v4_official

def ValidatePrefs():
    pass

def removeLeadingZeros(num): 
  
    # traverse the entire string 
    for i in range(len(num)): 
  
        # check for the first non-zero character 
        if num[i] != '0': 
            # return the remaining string 
            res = num[i::]; 
            return res; 
          
    # If the entire string is traversed 
    # that means it didn't have a single 
    # non-zero character, hence return "0" 
    return "0"; 
def Start():
    Log("Fernsehserien.de metadata agent started")
    HTTP.Headers['Accept'] = 'application/json'
    HTTP.CacheTime = 0.1
    ValidatePrefs()
def getPoster(metadata):
  ids = metadata.id.split("||")
  posters = []
  if ids[1] == "NoIMDB" or Prefs['APIKey'] == None:
    url = "https://www.fernsehserien.de/%s" % ids[0]
    Log(ids[0])
    r = requests.get(url)
    images = re.findall('<meta itemprop="image" content="(https://bilder.fernsehserien.de/sendung/.*?[^"]+?[.](?:png|jpg|jpeg))"',r.text)
    for image in images:
      posters.append(image)
  elif Prefs['APIKey']:
    tvdb = tvdb_v4_official.TVDB('%s' % Prefs['APIKey'])
    result = tvdb.search_by_remote_id(ids[1])
    image = result[0]['series']['image']
    posters.append(image)
  if Prefs['Debug']:
    Log(posters)
  return posters

def getSummary(metadata):
  url = "https://www.fernsehserien.de/%s" % metadata
  r = requests.get(url)
  summary = re.findall('"serie-beschreibung"[^>]*>(.*?)</div><', r.text)
  clean = re.compile('<.*?>')
  summary = clean.sub('', summary[0])
  return summary

def getEpisodeInfo(metadata, season, episode):
  if Prefs['Debug']:
    Log("Calling getEpisodeInfo for Metadata: %s, Season: %s, Episode: %s" % (metadata, season, episode) )
  overview = "https://www.fernsehserien.de/%s/episodenguide" % metadata
  r = requests.get(overview)
  episodes = re.findall('<a role="row" data-event-category="liste-episoden" href="/([^"]+?)" title="([^"]+?)"', r.text)
  for title in episodes:
    results = re.findall('(\d+)[.](\d+)', title[1])
    for result in results:
      if removeLeadingZeros(result[0]) == season or removeLeadingZeros(result[0]) == '0':
        if removeLeadingZeros(result[1]) == episode:
          title_match = re.sub('(\d+)[.](\d+)', '', title[1])
          summary = getEpisodeSummary(title[0])
          firstAired = getFirstAired(title[0])
          if Prefs['Debug']:
            Log("Title: %s, Summary: %s, firstAired: %s" % (title_match, summary, firstAired))
          return title_match, summary, firstAired

def getEpisodeSummary(url):
  if Prefs['Debug']:
    Log("Calling getEpisodeSummary with URL: %s" % url)
  episodeInfo = "https://www.fernsehserien.de/%s" % url
  r = requests.get(episodeInfo)
  summary = re.findall('<div class="episode-output-inhalt-inner">(.*?)</div><ea', r.text)
  clean = re.compile('<.*?>')
  summary = clean.sub('',summary[0])
  if summary != "":
    if Prefs['Debug']:
      Log("Summary: %s" % summary)
    return summary
  else:
    if Prefs['Debug']:
      Log("Summary: TBA")
    return "TBA"
  
def getFirstAired(url):
  if Prefs['Debug']:
    Log("Calling getFirstAired with URL %s" % url)
  episodeInfo = "https://www.fernsehserien.de/%s" % url
  r = requests.get(episodeInfo)
  date = re.search('<ea-angabe-datum>.*?(\d{2})\.(\d{2})\.(\d{4}).*?</ea-angabe-datum>', r.text)
  day = date.group(1)
  month = date.group(2)
  year = date.group(3)
  formatted_date = "%s-%s-%s" % (year,month,day)
  if Prefs['Debug']:
    Log("FirstAired Date: %s" % formatted_date)
  return Datetime.ParseDate(formatted_date).date()  

def getActors(metadata):
  if Prefs['Debug']:
    Log("Calling getActors with metadata: %s" % metadata)
  url = "https://www.fernsehserien.de/%s/cast-crew" % metadata
  r = requests.get(url)
  roles = re.findall('<h2 class="header-.*?" id="(.*?)">(.*?)</h2>', r.text)
  actors = []
  for role in roles:
    persons = re.findall('<a itemprop="url" data-event-category="liste-%s" href="/(.*?)/filmografie" class="ep-hover" title="(.*?)"><figure class="fs-picture.*?"><span class="fs-picture-placeholder" style=".*?">.*?src="(.*?)"' % role[1].lower() ,r.text)
    for person in persons:
      actors.append((person[1], role[1], person[2]))
  if Prefs['Debug']:
    Log("Actors: %s" % actors)
  return actors
  
class FernsehserienAgent(Agent.TV_Shows):
    name = 'Fernsehserien.de Agent'
    languages = [Locale.Language.English, 'fr', 'zh', 'sv', 'no', 'da', 'fi', 'nl', 'de', 'it', 'es', 'pl', 'hu', 'el', 'tr', 'ru', 'he', 'ja', 'pt', 'cs', 'ko', 'sl', 'hr']
    accepts_from = ["com.plexapp.agents.localmedia"] 

    def search(self, results, media, lang, manual=False):

      cookies = {
          'PHPSESSID': 'uq66hhhgln1j3g5s18gjhjnskd',
          'fs_ppid': '8cea158e72e590c46335b95da634ed00',
          '_pbjs_userid_consent_data': '8316820400794021',
          'fs_sessiontiefe': '13',
      }

      headers = {
          'authority': 'www.fernsehserien.de',
          'accept': '*/*',
          'accept-language': 'en-GB,en;q=0.8',
          'content-type': 'application/json',
          'cookie': 'PHPSESSID=uq66hhhgln1j3g5s18gjhjnskd; fs_ppid=8cea158e72e590c46335b95da634ed00; _pbjs_userid_consent_data=8316820400794021; fs_sessiontiefe=13',
          'origin': 'https://www.fernsehserien.de',
          'referer': 'https://www.fernsehserien.de/7-vs-wild',
          'sec-ch-ua': '"Brave";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
          'sec-ch-ua-mobile': '?0',
          'sec-ch-ua-platform': '"macOS"',
          'sec-fetch-dest': 'empty',
          'sec-fetch-mode': 'cors',
          'sec-fetch-site': 'same-origin',
          'sec-gpc': '1',
          'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
          'x-csrf-token': '$2y$10$OuY9ezTFhPLwQZARYUxikuFCwnD7amYIltelrhgFzxVK8ypU2lgdm',
        }
        
      json_data = {"suchwort": "%s" % media.show}
      search = requests.post('https://www.fernsehserien.de/fastsearch', cookies=cookies, headers=headers, data=json.dumps(json_data))
      search = json.loads(search.text)
      for result in search['items']:
        overview = requests.get('https://www.fernsehserien.de/%s' % result['s']) 
        overview = overview.text
        imdbId = re.search('imdb.com/title/(.*?)/.*?</figure>IMDb', overview)
        if imdbId != None:
          ids = result['s'] + "||" + imdbId.group(1)
        else:
          ids = result['s'] + "||NoIMDB"
        fsTitle = result['t']
        fsAired = result['l']
        fsScore = 100 - Util.LevenshteinDistance(media.show,fsTitle)
        thumb = result['b']
        if result['a'] == "sg":
          results.Append(MetadataSearchResult(id=ids, name=fsTitle, year=fsAired, score=fsScore, lang=lang, thumb=thumb))

    def update(self, metadata, media, lang):
      #Log("LANG: %s " % dir(lang))
      #Log("MEDIA: %s" % dir(media))
      ids = metadata.id.split("||")
      metadata.title = media.title
      metadata.summary = getSummary(metadata=ids[0])
      metadata.originally_available_at = getFirstAired(url=ids[0])
      posters = getPoster(metadata=metadata)
      actors = getActors(metadata=ids[0])
      for actor in actors:
        role = metadata.roles.new()
        role.name = actor[0]
        role.role = actor[1]
        role.photo = actor[2] 
      
      # Delete FS Posters if APIKey for TVDB is set.
      if Prefs['APIKey']:
        for poster in metadata.posters.keys():
          if "fernsehserien.de/" in poster:
            del metadata.posters[poster]
      
      for poster in posters:
        metadata.posters[poster] = Proxy.Preview(HTTP.Request(poster))
      
      for season in media.seasons:
        if Prefs['Debug']:
          Log("Updating Season %s" % season)
        for episode in media.seasons[season].episodes:
          if Prefs['Debug']:
            Log("Updating Episode: %s" % episode)
          try:
            title, summary, firstAired = getEpisodeInfo(metadata=ids[0], season=season, episode=episode)
            metadata.seasons[season].episodes[episode].title = title
            metadata.seasons[season].episodes[episode].summary = summary
            metadata.seasons[season].episodes[episode].originally_available_at = firstAired
          except:
            Log("Could not Update Episode %s in Season %s" % (episode, season))