import json
import re
import requests

class Tinder(object):

    headers = { "X-Auth-Token": "e5d3ea9c-75ae-430f-908d-717b3998bc99",
                "Content-type": "application/json",
                "app_version": "3",
                "User-agent": "Tinder/3.0.4 (iPhone; iOS 7.1; Scale/2.00)",
                "platform": "ios",
                "os_version": "700001"}

    cur_rec = None
    cached_recs = []
    facebook_token = "CAAGm0PX4ZCpsBAKuJpaRjxalcaPgpWgaz1SiyrRxbiJpHeZBXbQZBKADAWZA5fdX8v9wnZBGJusVozNm7hIsxTKMaWRLinzZAqLQrJAVhZBQtnAaB6ZA7YFUhKyDcZCkGG9ZCCDcQOdmANlAcwbXZA1KYMhkjaF1dhRcfaFwKE3RvznMvQad5jo5ZAmmwR5QQvGqiiIa0UMAY4e5beVMdFEbTdUw28QWJZBVUrt4ZD"
    facebook_id = "srinchiera@college.harvard.edu"

    @classmethod
    def __call__(cls, text):

        recs =  re.compile('!tinder$', re.IGNORECASE)
        swipe_left = re.compile('!swipe left', re.IGNORECASE)
        swipe_right = re.compile('!swipe right', re.IGNORECASE)
        next =  re.compile('!next photo', re.IGNORECASE)
        auth =  re.compile('!tinder auth (.+)? (.+)', re.IGNORECASE)
        auth_link =  re.compile('!tinder auth link', re.IGNORECASE)
        location =  re.compile('!tinder update location', re.IGNORECASE)

        command_to_func = { recs: cls.get_rec,
                            swipe_left: cls.swipe_left,
                            swipe_right: cls.swipe_right,
                            next: cls.next_photo,
                            auth: cls.auth,
                            auth_link: cls.auth_link,
                            location: cls.update_location }

        for command, func in command_to_func.items():
            match = command.match(text)
            if match:
                args = match.groups()
                return func(*args)

        return False

    @classmethod
    def auth_link(cls, facebook_id = None, facebook_token = None):
        return "https://www.facebook.com/dialog/oauth?client_id=464891386855067&redirect_uri=https://www.facebook.com/connect/login_success.html&scope=basic_info,email,public_profile,user_about_me,user_activities,user_birthday,user_education_history,user_friends,user_interests,user_likes,user_location,user_photos,user_relationship_details&response_type=token"

    @classmethod
    def auth(cls, facebook_id = None, facebook_token = None):

        facebook_token = facebook_token or cls.facebook_token
        facebook_id = facebook_id or cls.facebook_id

        auth = {"facebook_token": facebook_token,
                "facebook_id": facebook_id}

        try:
            del cls.headers['X-Auth-Token']
        except:
            pass

        auth_url = 'https://api.gotinder.com/auth'

        r = requests.post(auth_url, data = json.dumps(auth), headers = cls.headers)

        if r.status_code == 500:
            return "Please reauth using your facebook token"

        if r.status_code == 200:
            token = json.loads(r.text)['token']
            cls.headers['X-Auth-Token'] = token
            return "Sucessfully authenticated!"

    @classmethod
    def get_rec(cls):

        if cls.cached_recs:
            rec = cls.cached_recs.pop()
            cls.cur_rec = rec
            photo = rec['photos'].pop()
            photo_url = cls.get_photo_url(photo)
            bio = rec['bio']
            return u"{0}\n{1}".format(photo_url, bio)

        r = requests.get('https://api.gotinder.com/user/recs', headers = cls.headers)

        if r.status_code == 403 or r.status_code == 401:
            return "Please authenticate."

        if r.status_code == 200:
            cls.cached_recs = json.loads(r.text)['results']
            return cls.get_rec()

        return "Error... Not even goob can save your love life"

    @classmethod
    def next_photo(cls):
        if cls.cur_rec is None:
            return "No current recommendation"

        try:
            next = cls.cur_rec['photos'].pop()
            photo_url = cls.get_photo_url(next)
            return photo_url
        except:
            return "No more photos"

    @classmethod
    def swipe_right(cls):
        # Like, unlike. If like return match!
        user_id = cls.cur_rec['_id']
        r = requests.get("https://api.gotinder.com/like/{0}".format(user_id), headers = cls.headers)

        if r.status_code == 403 or r.status_code == 401:
            return "Please authenticate."

        if r.status_code == 200:
            match = json.loads(r.text)
            cls.cur_rec = None
            print match
            if match["match"] == False:
                return "No match :("
            else:
                return "It's a match!"

        return "Error... Not even goob can save your love life"

    @classmethod
    def swipe_left(cls):
        # Like, unlike. If like return match!

        user_id = cls.cur_rec['_id']
        r = requests.get("https://api.gotinder.com/pass/{0}".format(user_id), headers = cls.headers)

        if r.status_code == 403 or r.status_code == 401:
            return "Please authenticate."

        if r.status_code == 200:
            cls.cur_rec = None
            return "Success!"

        return "Error... Not even goob can save your love life"

    @classmethod
    def get_photo_url(cls, photo):
        return photo['processedFiles'][0]['url']

    @classmethod
    def update_location(cls):
         #'--data '{"lat": latitude, "lon": longitude}'

        loc = {"lat": "40.741847",
               "lon": "-73.990962"}

        loc_url = 'https://api.gotindaer.com/user/ping'
        r = requests.post(loc_url, data = json.dumps(loc), headers = cls.headers)

        if r.status_code == 403 or r.status_code == 401:
            return "Please authenticate."

        return "Done"

t = Tinder()
t.__name__ = 'tinder'

def on_message(msg, server):
    text = msg.get("text", "")
    return t.__call__(text)
