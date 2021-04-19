from everskies import estoken
from everskies import utils
import requests
import json
"""TODO:
    1. Update setLayout
    2. Add functionality for more GET's!
        - Yes, most of these functions are supposed to belong in utils, 
            but if it's data only a User could get about themselves, 
            it belongs in User
    3. Websocket? Python cryptography ?!?!

    """
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

    def __repr__(self):
        if isinstance(self.user, dict):
            username=str(self.user.get("alias", "Unknown"))
        else:
            username="Unknown"
        return str(f"User {username}")

    def getData(self, silent=True):
        if not silent:
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

    def claimReward(self):
        self.readyAuth()
        reward=json.loads(self.rs.get("https://api.everskies.com/user/reward"))
        if reward:
            print("Claiming reward!")
            self.rs.post("https://api.everskies.com/user/claim-reward", data='{"done":true}')
        else:
            print("Nothing to claim")
        return reward

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

    def claimGift(self, code):
        self.readyAuth()
        r=self.rs.post("https://api.everskies.com/payments/gift/claim", data=json.dumps({"code" : code}))
        if r.ok:
            print("Claimed gift successfully!")
        else:
            print("Failed to claim gift")
        return r
    
    def setLayout(self, layout, mode="create", **kwargs):
        """Expects layout to look similar to a layout directly from everskies api

        Mode=create - Make new layout
        Mode=update - Change a layout
        Mode=steal - take someone else's layout
            Mode=steal expects either a kwarg for url or a layout already provided

        Kwargs options:
            "name" : theme name if creating or stealing - Str
            "apply" : apply this new//updated layout - Bool
            "steal_url" : GET this layout and make it work (somehow)! 
                                - If supplied, ignore layout and set internally
                                - Str
        """
        # doesn't support images completely yet- probably an easy fix

        def rebuild_data(data):    
            datatemp=data["userProfileElements"]
            for element in datatemp:
                    element["id"]=-26045899
                    element["user_profile_layout_id"]=None
            datatemp={"elements":datatemp}
            datatemp["layout"]={
                    "id":None,
                    "name": kwargs.get("name", "new!"),
                    "themeColor":data.get("themeColor", None),
                    "showClouds":data.get("showClouds", None),
                    "backgroundRepeat":data.get("backgroundRepeat", None),
                    "backgroundSize":data.get("backgroundSize", None),
                    "backgroundUrl":data.get("backgroundUrl", None)
            }
            datatemp["apply"]=kwargs.get("apply", False)
            
            return datatemp
        
        #ugly elif chain :(( python match case better release soon
        if mode == "steal":
            t_layout=kwargs.get("steal_url", False)
            if t_layout:
                layout=self.rs.get(t_layout)
            layout=rebuild_data(layout)
            self.readyAuth()
            self.rs.post("https://api.everskies.com/user/layout/update", data=json.dumps(layout))

        elif mode == "create":
            pass
        elif mode == "update":
            pass
        else:
            print("Not a valid mode!")
        
    def auctionBid(self, itemid, amount, **kwargs):
        self.readyAuth()
        r=self.rs.post(f'https://api.everskies.com/outlet/bid/{itemid}', data=json.dumps({"price":amount}))
        if r.ok:
            return r
        else:
            print(f"Failed to bid {amoun} on {itemid}")
            return r

    def createTrade(self, userid, **kwargs):
        """
        kwargs:
            - offeredItemSets - list of ints
            - offeredItemVariations - list of ints
            - offerPrimary - int (stardust)
            - offerSecondary - int (stars)
            - requestItemSets - list of ints
            - requestItemVariations - list of ints
            - requestPrimary - int
            - requestSecondary - int
        """
        self.readyAuth()
        trade={
                "user_id" : userid,
                "offeredItemSetIds" : kwargs.get("offeredItemSets", []),
                "offeredItemVariationIds" : kwargs.get("offeredItemVariations", []),
                "requestedItemSetIds" : kwargs.get("requestItemSets", []),
                "requestedItemVariationIds" : kwargs.get("requestItemVariations", []),
                "offer_primary" : kwargs.get("offerPrimary", None),
                "offer_secondary" : kwargs.get("offerSecondary", None),
                "request_primary" : kwargs.get("requestPrimary", None),
                "request_secondary" : kwargs.get("requestSecondary", None),
                }
        r=self.rs.post("https://api.everskies.com/user/message/trade", data=json.dumps(trade))
        if r.ok:
            print(f"Successfully sent trade reqest to {userid}, data: {kwargs}")
            return r
        else:
            print(f"Failed to send trade request to {userid}, data: {kwargs}")
            return r

    def cancelTrade(self, tradeid):
        self.readyAuth()
        r=self.rs.post(f"https://api.everskies.com/user/message/trade/{tradeid}/cancel", data="")
        if r.ok:
            print(f"Cancelled trade id {tradeid}")
            return r
        else:
            print(f"Failed to cancel trade id {tradeid}. Status code: {r.status_code}")
            return r
    
    def acceptTrade(self, tradeid):
        self.readyAuth()
        r=self.rs.post(f"https://api.everskies.com/user/message/trade/{tradeid}/accept", data="")
        if r.ok:
            print(f"Accepted trade id {tradeid}")
            return r
        else:
            print(f"Failed to accept trade id {tradeid}. Status code: {r.status_code}")
            return r

