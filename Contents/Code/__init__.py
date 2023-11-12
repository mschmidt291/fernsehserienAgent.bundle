import re
import json
import requests
import re
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
    Log("Stash metadata agent started")
    HTTP.Headers['Accept'] = 'application/json'
    HTTP.CacheTime = 0.1

def getPosters(metadata):
  url = "https://www.fernsehserien.de/%s" % metadata.id
  r = requests.get(url)
  images = re.findall('<meta itemprop="image" content="(https://bilder.fernsehserien.de/sendung/.*?[^"]+?[.](?:png|jpg|jpeg))"',r.text)
  return images

def getSummary(metadata):
  url = "https://www.fernsehserien.de/%s" % metadata.id
  r = requests.get(url)
  summary = re.findall('"serie-beschreibung"[^>]*>(.*?)</div><', r.text)
  clean = re.compile('<.*?>')
  summary = clean.sub('', summary[0])
  return summary

def getEpisodeInfo(metadata, season, episode):
  overview = "https://www.fernsehserien.de/%s/episodenguide" % metadata.id
  r = requests.get(overview)
  episodes = re.findall('<a role="row" data-event-category="liste-episoden" href="/([^"]+?)" title="([^"]+?)"', r.text)
  for title in episodes:
    results = re.findall('(\d+)[.](\d+)', title[1])
    for result in results:
      if removeLeadingZeros(result[0]) == season or removeLeadingZeros(result[0]) == '0':
        if removeLeadingZeros(result[1]) == episode:
          title_match = re.sub('(\d+)[.](\d+)', '', title[1])
          summary = getEpisodeSummary(title[0])
          return title_match, summary

def getEpisodeSummary(url):
  episodeInfo = "https://www.fernsehserien.de/%s" % url
  r = requests.get(episodeInfo)
  summary = re.findall('<div class="episode-output-inhalt-inner">(.*?)</div><ea', r.text)
  clean = re.compile('<.*?>')
  summary = clean.sub('',summary[0])
  if summary != "":
    return summary
  else:
    return "TBA"
  
def getActors(metadata):
  url = "https://www.fernsehserien.de/%s/cast-crew" % metadata.id
  r = requests.get(url)
  roles = re.findall('<h2 class="header-.*?" id="(.*?)">(.*?)</h2>', r.text)
  actors = []
  for role in roles:
    persons = re.findall('<li itemscope itemtype="http://schema\.org/Person"><a itemprop="url" data-event-category="liste-%s" href="/(.*?)/filmografie" class="ep-hover" title="(.*?)"><figure class="fs-picture.*?"><span class="fs-picture-placeholder" style=".*?">.*?src="(.*?)"' % role[1].lower() ,r.text)
    for person in persons:
      actors.append((person[1], role[1], person[2]))
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
        
      searchUrl = 'https://www.fernsehserien.de/fastsearch'

      json_data = {"suchwort": "%s" % media.show}
      r = requests.post('https://www.fernsehserien.de/fastsearch', cookies=cookies, headers=headers, data=json.dumps(json_data))
      r = json.loads(r.text)
      for result in r['items']:
        fsId = result['s']
        fsTitle = result['t']
        fsAired = result['l']
        fsScore = 100 - Util.LevenshteinDistance(media.show,fsTitle)
        results.Append(MetadataSearchResult(id=fsId, name=fsTitle, year=fsAired, score=fsScore, lang=lang))

    def update(self, metadata, media, lang):
      #Log("LANG: %s " % dir(lang))
      #Log("MEDIA: %s" % dir(media))
      metadata.title = media.title
      metadata.summary = getSummary(metadata=metadata)
      posters = getPosters(metadata=metadata)
      actors = getActors(metadata=metadata)
      for actor in actors:
        role = metadata.roles.new()
        role.name = actor[0]
        role.role = actor[1]
        role.photo = actor[2] 

      for poster in posters:
        metadata.posters[poster] = Proxy.Preview(HTTP.Request(poster))
      for season in media.seasons:
        for episode in media.seasons[season].episodes:
          title, summary = getEpisodeInfo(metadata=metadata, season=season, episode=episode)
          metadata.seasons[season].episodes[episode].title = title
          metadata.seasons[season].episodes[episode].summary = summary