from esLib import estoken
from esLib import utils
import requests
import json

class User():
    """
    Various functions and actions an ES User could take
    Handles token automatically thanks to estoken,
    Support for websocket TBA (ETA: Never)
    Most functions for POSTing/GETing should be included
    """
    def __init__(self, refresh_token=None, **kwargs):
        if refresh_token:
            self.tokenManager=estoken.tokenManager(
                                                    refresh_token=refresh_token, 
                                                    refresh_token_expires=kwargs.get("refresh_token_expires", False), 
                                                    access_token_expires_after=kwargs.get("access_token_expires_after", 1800),
                                                    refresh_token_proxy=kwargs.get("refresh_token_proxy", False),
						    )
        else:
            print("you will need to use User.set_token(refresh_token=\"[...]\")!")
        
        self.user=kwargs.get("user", None)
        
        self.rs=kwargs.get("rs", utils.defaultSession(proxies=kwargs.get("proxies", False)))
    
    def readyAuth(self):
        self.rs.headers.update({
                    "authorization" : "Bearer " + self.tokenManager.get_token()
                })
        # do this often - perhaps we could move session management to estoken? idk lol
    
    def refreshUserData(self):
        self.readyAuth()
        self.user=self.rs.get("https://api.everskies.com/user")
        if self.user.ok:
            self.user=json.loads(self.user.text)
        else:

            self.user=None
            raise Exception("Failed to get user data!")

    def getData(self):
        print("Ok! Getting data.")
        return {
                "user" : self.user,
                "tokenManager" : self.tokenManager.get_data(),
                }

    def setToken(self, refresh_token):
        self.tokenManager=estoken.tokenManager(refresh_token=refresh_token)

    def createReply(self, threadid, text, **kwargs):
        self.readyAuth()
        data = {
                "content"         : text,
                "parent_reply_id" : kwargs.get("parent_reply_id", None),
                "attachments"     : kwargs.get("attachments", []),
                }
        url = f'https://api.everskies.com/discussion/{threadid}/reply'
        r=self.rs.post(url, data=json.dumps(data))
        if r.ok:
            print("successfully created post")
            return r
        else:
            raise Exception("Failed to create reply!")

        

    def createPost(self, title, text, categoryid=8, **kwargs):
        readyAuth()
        #{"title":"hi","tw":null,"tw_reason":null,"tags":"","category_id":8,"club_category_id":null,"content":"lol","event":null,"attachments":[]}
        data = {
                "title"            : title,
                "tw"               : kwargs.get("tw",None),
                "tw_reason"        : kwargs.get("tw_reason",None),
                "tags"             : kwargs.get("tags",""),
                "category_id"      : categoryid,
                "club_category_id" : kwargs.get("club_category_id",None),
                "content"          : text,
                "event"            : kwargs.get("event",None),
                "attachments"      : kwargs.get("attachments",[]),
                }
        #debug:
        #print(data)
        #print(json.dumps(data))
        url = 'https://api.everskies.com/discussion/create'
        r=self.rs.post(url, data=json.dumps(data))
        if r.ok:
            print("successfully created post")
            return r
        else:
            raise Exception("Failed to create Post")
