import json
import requests

class Auth:
    def __init__(self, url, apikey, pin=""):
        login_info = {"apikey": apikey}
        if pin:
            login_info["pin"] = pin
        headers = {"Content-Type": "application/json"}
        loginInfoBytes = json.dumps(login_info, indent=2).encode("utf-8")
        response = requests.post(url, data=loginInfoBytes, headers=headers)

        try:
            response.raise_for_status()
            res = json.loads(response.text)
            self.token = res["data"]["token"]
        except requests.HTTPError as e:
            res = json.loads(response.text)
            raise Exception("Code:{}, {}".format(response.status_code, res["message"]))

    def get_token(self):
        print(self.token)
        return self.token


class Request:
    def __init__(self, auth_token):
        self.auth_token = auth_token
        self.links = None

    def make_request(self, url, if_modified_since=None):
        headers = {"Authorization": "Bearer {}".format(self.auth_token)}
        if if_modified_since:
            headers["If-Modified-Since"] = "{}".format(if_modified_since)

        response = requests.get(url, headers=headers)

        try:
            response.raise_for_status()
            res = response.json()
        except requests.HTTPError as e:
            if e.response.status_code == 304:  # HTTPStatus.NOT_MODIFIED
                return {"code": 304, "message": "Not-Modified"}

            res = e.response.json()

        data = res.get("data", None)
        if data is not None and res.get("status", "failure") != "failure":
            self.links = res.get("links", None)
            return data

        msg = res.get("message", "UNKNOWN FAILURE")
        raise ValueError("failed to get %s %s" %(url, msg))


class Url:
    def __init__(self):
        self.base_url = "https://api4.thetvdb.com/v4/"

    def construct(
        self, url_sect, url_id=None, url_subsect=None, url_lang=None, **query
    ):
        url = self.base_url + url_sect
        if url_id:
            url += "/" + str(url_id)
        if url_subsect:
            url += "/" + url_subsect
        if url_lang:
            url += "/" + url_lang
        if query:
            query = {var: val for var, val in query.items() if val is not None}
            if query:
                url += "?" + "&".join(["%s=%s" % (key,val) for key, val in query.items()])
        return url



class TVDB:
    def __init__(self, apikey, pin=""):
        self.url = Url()
        login_url = self.url.construct("login")
        self.auth = Auth(login_url, apikey, pin)
        auth_token = self.auth.get_token()
        self.request = Request(auth_token)

    def get_req_links(self):
        return self.request.links

    def get_artwork_statuses(self, meta=None, if_modified_since=None):
        """Returns a list of artwork statuses"""
        url = self.url.construct("artwork/statuses", meta=meta)
        return self.request.make_request(url, if_modified_since)

    def get_artwork_types(self, meta=None, if_modified_since=None):
        """Returns a list of artwork types"""
        url = self.url.construct("artwork/types", meta=meta)
        return self.request.make_request(url, if_modified_since)

    def get_artwork(self, id, meta=None, if_modified_since=None):
        """Returns an artwork dictionary"""
        url = self.url.construct("artwork", id, meta=meta)
        return self.request.make_request(url, if_modified_since)

    def get_artwork_extended(self, id, meta=None, if_modified_since=None):
        """Returns an artwork extended dictionary"""
        url = self.url.construct("artwork", id, "extended", meta=meta)
        return self.request.make_request(url, if_modified_since)

    def get_all_awards(self, meta=None, if_modified_since=None):
        """Returns a list of awards"""
        url = self.url.construct("awards", meta=meta)
        return self.request.make_request(url, if_modified_since)

    def get_award(self, id, meta=None, if_modified_since=None):
        """Returns an award dictionary"""
        url = self.url.construct("awards", id, meta=meta)
        return self.request.make_request(url, if_modified_since)

    def get_award_extended(self, id, meta=None, if_modified_since=None):
        """Returns an award extended dictionary"""
        url = self.url.construct("awards", id, "extended", meta=meta)
        return self.request.make_request(url, if_modified_since)

    def get_all_award_categories(self, meta=None, if_modified_since=None):
        """Returns a list of award categories"""
        url = self.url.construct("awards/categories", meta=meta)
        return self.request.make_request(url, if_modified_since)

    def get_award_category(self, id, meta=None, if_modified_since=None):
        """Returns an award category dictionary"""
        url = self.url.construct("awards/categories", id, meta=meta)
        return self.request.make_request(url, if_modified_since)

    def get_award_category_extended(
        self, id, meta=None, if_modified_since=None
    ):
        """Returns an award category extended dictionary"""
        url = self.url.construct("awards/categories", id, "extended", meta=meta)
        return self.request.make_request(url, if_modified_since)

    def get_content_ratings(self, meta=None, if_modified_since=None):
        """Returns a list of content ratings"""
        url = self.url.construct("content/ratings", meta=meta)
        return self.request.make_request(url, if_modified_since)

    def get_countries(self, meta=None, if_modified_since=None):
        """Returns a list of countries"""
        url = self.url.construct("countries", meta=meta)
        return self.request.make_request(url, if_modified_since)

    def get_all_companies(self, page=None, meta=None, if_modified_since=None):
        """Returns a list of companies"""
        url = self.url.construct("companies", page=page, meta=meta)
        return self.request.make_request(url, if_modified_since)

    def get_company_types(self, meta=None, if_modified_since=None):
        """Returns a list of company types"""
        url = self.url.construct("companies/types", meta=meta)
        return self.request.make_request(url, if_modified_since)

    def get_company(self, id, meta=None, if_modified_since=None):
        """Returns a company dictionary"""
        url = self.url.construct("companies", id, meta=meta)
        return self.request.make_request(url, if_modified_since)

    def get_all_series(self, page=None, meta=None, if_modified_since=None):
        """Returns a list of series"""
        url = self.url.construct("series", page=page, meta=meta)
        return self.request.make_request(url, if_modified_since)

    def get_series(self, id, meta=None, if_modified_since=None):
        """Returns a series dictionary"""
        url = self.url.construct("series", id, meta=meta)
        return self.request.make_request(url, if_modified_since)

    def get_series_by_slug(
        self, slug, meta=None, if_modified_since=None
    ):
        """Returns a series dictionary"""
        url = self.url.construct("series/slug", slug, meta=meta)
        return self.request.make_request(url, if_modified_since)

    def get_series_extended(
        self, id, meta=None, short=False, if_modified_since=None
    ):
        """Returns a series extended dictionary"""
        url = self.url.construct("series", id, "extended", meta=meta, short=short)
        return self.request.make_request(url, if_modified_since)

    def get_series_episodes(
        self,
        id,
        season_type = "default",
        page = 0,
        lang = None,
        meta=None,
        if_modified_since=None,
    ):
        """Returns a series episodes dictionary"""
        url = self.url.construct(
            "series", id, "episodes/" + season_type, lang, page=page, meta=meta
        )
        return self.request.make_request(url, if_modified_since)

    def get_series_translation(
        self, id, lang, meta=None, if_modified_since=None
    ):
        """Returns a series translation dictionary"""
        url = self.url.construct("series", id, "translations", lang, meta=meta)
        return self.request.make_request(url, if_modified_since)

    def get_series_artworks(
        self, id, lang, type=None, if_modified_since=None
    ):
        """Returns a series record with an artwork array"""
        url = self.url.construct("series", id, "artworks", lang=lang, type=type)
        return self.request.make_request(url, if_modified_since)

    def get_series_nextAired(self, id, if_modified_since=None):
        """Returns a series extended dictionary"""
        url = self.url.construct("series", id, "nextAired")
        return self.request.make_request(url, if_modified_since)

    def get_all_movies(self, page=None, meta=None, if_modified_since=None):
        """Returns a list of movies"""
        url = self.url.construct("movies", page=page, meta=meta)
        return self.request.make_request(url, if_modified_since)

    def get_movie(self, id, meta=None, if_modified_since=None):
        """Returns a movie dictionary"""
        url = self.url.construct("movies", id, meta=meta)
        return self.request.make_request(url, if_modified_since)

    def get_movie_by_slug(
        self, slug, meta=None, if_modified_since=None
    ):
        """Returns a movie dictionary"""
        url = self.url.construct("movies/slug", slug, meta=meta)
        return self.request.make_request(url, if_modified_since)

    def get_movie_extended(
        self, id, meta=None, short=False, if_modified_since=None
    ):
        """Returns a movie extended dictionary"""
        url = self.url.construct("movies", id, "extended", meta=meta, short=short)
        return self.request.make_request(url, if_modified_since)

    def get_movie_translation(
        self, id, lang, meta=None, if_modified_since=None
    ):
        """Returns a movie translation dictionary"""
        url = self.url.construct("movies", id, "translations", lang, meta=meta)
        return self.request.make_request(url, if_modified_since)

    def get_all_seasons(self, page=None, meta=None, if_modified_since=None):
        """Returns a list of seasons"""
        url = self.url.construct("seasons", page=page, meta=meta)
        return self.request.make_request(url, if_modified_since)

    def get_season(self, id, meta=None, if_modified_since=None):
        """Returns a season dictionary"""
        url = self.url.construct("seasons", id, meta=meta)
        return self.request.make_request(url, if_modified_since)

    def get_season_extended(self, id, meta=None, if_modified_since=None):
        """Returns a season extended dictionary"""
        url = self.url.construct("seasons", id, "extended", meta=meta)
        return self.request.make_request(url, if_modified_since)

    def get_season_types(self, meta=None, if_modified_since=None):
        """Returns a list of season types"""
        url = self.url.construct("seasons/types", meta=meta)
        return self.request.make_request(url, if_modified_since)

    def get_season_translation(
        self, id, lang, meta=None, if_modified_since=None
    ):
        """Returns a seasons translation dictionary"""
        url = self.url.construct("seasons", id, "translations", lang, meta=meta)
        return self.request.make_request(url, if_modified_since)

    def get_all_episodes(self, page=None, meta=None, if_modified_since=None):
        """Returns a list of episodes"""
        url = self.url.construct("episodes", page=page, meta=meta)
        return self.request.make_request(url, if_modified_since)

    def get_episode(self, id, meta=None, if_modified_since=None):
        """Returns an episode dictionary"""
        url = self.url.construct("episodes", id, meta=meta)
        return self.request.make_request(url, if_modified_since)

    def get_episode_extended(self, id, meta=None, if_modified_since=None):
        """Returns an episode extended dictionary"""
        url = self.url.construct("episodes", id, "extended", meta=meta)
        return self.request.make_request(url, if_modified_since)

    def get_episode_translation(
        self, id, lang, meta=None, if_modified_since=None
    ):
        """Returns an episode translation dictionary"""
        url = self.url.construct("episodes", id, "translations", lang, meta=meta)
        return self.request.make_request(url, if_modified_since)

    get_episodes_translation = (
        get_episode_translation  # Support the old name of the function.
    )

    def get_all_genders(self, meta=None, if_modified_since=None):
        """Returns a list of genders"""
        url = self.url.construct("genders", meta=meta)
        return self.request.make_request(url, if_modified_since)

    def get_all_genres(self, meta=None, if_modified_since=None):
        """Returns a list of genres"""
        url = self.url.construct("genres", meta=meta)
        return self.request.make_request(url, if_modified_since)

    def get_genre(self, id, meta=None, if_modified_since=None):
        """Returns a genres dictionary"""
        url = self.url.construct("genres", id, meta=meta)
        return self.request.make_request(url, if_modified_since)

    def get_all_languages(self, meta=None, if_modified_since=None):
        """Returns a list of languages"""
        url = self.url.construct("languages", meta=meta)
        return self.request.make_request(url, if_modified_since)

    def get_all_people(self, page=None, meta=None, if_modified_since=None):
        """Returns a list of people"""
        url = self.url.construct("people", page=page, meta=meta)
        return self.request.make_request(url, if_modified_since)

    def get_person(self, id, meta=None, if_modified_since=None):
        """Returns a people dictionary"""
        url = self.url.construct("people", id, meta=meta)
        return self.request.make_request(url, if_modified_since)

    def get_person_extended(self, id, meta=None, if_modified_since=None):
        """Returns a people extended dictionary"""
        url = self.url.construct("people", id, "extended", meta=meta)
        return self.request.make_request(url, if_modified_since)

    def get_person_translation(
        self, id, lang, meta=None, if_modified_since=None
    ):
        """Returns an people translation dictionary"""
        url = self.url.construct("people", id, "translations", lang, meta=meta)
        return self.request.make_request(url, if_modified_since)

    def get_character(self, id, meta=None, if_modified_since=None):
        """Returns a character dictionary"""
        url = self.url.construct("characters", id, meta=meta)
        return self.request.make_request(url, if_modified_since)

    def get_people_types(self, meta=None, if_modified_since=None):
        """Returns a list of people types"""
        url = self.url.construct("people/types", meta=meta)
        return self.request.make_request(url, if_modified_since)

    get_all_people_types = get_people_types  # Support the old function name

    def get_source_types(self, meta=None, if_modified_since=None):
        """Returns a list of source types"""
        url = self.url.construct("sources/types", meta=meta)
        return self.request.make_request(url, if_modified_since)

    get_all_sourcetypes = get_source_types  # Support the old function name

    # kwargs accepts args such as: page=2, action='update', type='artwork'
    def get_updates(self, since, **kwargs):
        """Returns a list of updates"""
        url = self.url.construct("updates", since=since, **kwargs)
        return self.request.make_request(url)

    def get_all_tag_options(self, page=None, meta=None, if_modified_since=None):
        """Returns a list of tag options"""
        url = self.url.construct("tags/options", page=page, meta=meta)
        return self.request.make_request(url, if_modified_since)

    def get_tag_option(self, id, meta=None, if_modified_since=None):
        """Returns a tag option dictionary"""
        url = self.url.construct("tags/options", id, meta=meta)
        return self.request.make_request(url, if_modified_since)

    def get_all_lists(self, page=None, meta=None):
        url = self.url.construct("lists", page=page, meta=meta)
        return self.request.make_request(url)

    def get_list(self, id, meta=None, if_modified_since=None):
        url = self.url.construct("lists", id, meta=meta)
        return self.request.make_request(url), if_modified_since

    def get_list_by_slug(self, slug, meta=None, if_modified_since=None):
        """Returns a movie dictionary"""
        url = self.url.construct("lists/slug", slug, meta=meta)
        return self.request.make_request(url, if_modified_since)

    def get_list_extended(self, id, meta=None, if_modified_since=None):
        url = self.url.construct("lists", id, "extended", meta=meta)
        return self.request.make_request(url), if_modified_since

    def get_list_translation(
        self, id, lang, meta=None, if_modified_since=None
    ):
        """Returns an list translation dictionary"""
        url = self.url.construct("lists", id, "translations", lang, meta=meta)
        return self.request.make_request(url, if_modified_since)

    def get_inspiration_types(self, meta=None, if_modified_since=None):
        url = self.url.construct("inspiration/types", meta=meta)
        return self.request.make_request(url), if_modified_since

    def search(self, query, **kwargs):
        """Returns a list of search results"""
        url = self.url.construct("search", query=query, **kwargs)
        return self.request.make_request(url)

    def search_by_remote_id(self, remoteid):
        """Returns a list of search results by remote id exact match"""
        url = self.url.construct("search/remoteid", remoteid)
        return self.request.make_request(url)

    def get_tags(self, slug, if_modified_since=None):
        """Returns a tag option dictionary"""
        url = self.url.construct("entities", url_subsect=slug)
        return self.request.make_request(url, if_modified_since)

    def get_entities_types(self, if_modified_since=None):
        """Returns a entities types dictionary"""
        url = self.url.construct("entities")
        return self.request.make_request(url, if_modified_since)

    def get_user_by_id(self, id):
        """Returns a user info dictionary"""
        url = self.url.construct("user", id)
        return self.request.make_request(url)

    def get_user(self):
        """Returns a user info dictionary"""
        url = self.url.construct("user")
        return self.request.make_request(url)