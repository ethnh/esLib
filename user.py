#!/usr/bin/env python3
# unused import - consider removing
import json
import logging

import requests
from everskies import errors
from everskies import token
from everskies import utils

log = logging.getLogger(__name__)
"""TODO:
    1. Update setLayout
    2. Add functionality for more GET's!
        - Yes, most of these functions are supposed to belong in utils,
            but if it's data only a User could get about themselves,
            it belongs in User
    3. Websocket? Python cryptography ?!?!
    4. Custom errors for when r.ok is false?
    """


class User(object):
    """
    Various functions and actions an ES User could take
    Handles token automatically thanks to estoken,
    Support for websocket TBA (ETA: Never)
    Most functions for POSTing/GETing should be included
    """
    def __init__(self, refresh_token: str = None, **kwargs):
        if refresh_token:
            self.Tokenmanager = token.Tokenmanager(
                refresh_token=refresh_token,
                refresh_token_expires=kwargs.get("refresh_token_expires"),
                access_token_expires_after=kwargs.get(
                    "access_token_expires_after", 1800),
                refresh_token_proxy=kwargs.get("refresh_token_proxy", kwargs.get("proxies")),
            )   # I'm not sure if we SHOULD pull from proxies kwarg as backup for rproxy,
                # but I see no harm in it
        else:
            log.info(
                'you will need to use User.set_token(refresh_token="[...]")!')
            self.Tokenmanager = token.Tokenmanager()

        self.user = kwargs.get("user")
        # self.user is a dict object with the same data 
        # you would get from api.everskies.com/user
        
        self.rs = kwargs.get("rs")
        # self.(r)equest (s)ession

        self.proxies = kwargs.get("proxies")

        if self.rs is None:
            self.rs = utils.defaultSession(proxies=self.proxies)
            # defaultSession seems good enough honestly
            # if defaultSession is removed, add check for 
            #   if self.proxies: self.rs.proxies.update(self.proxies)
    def readyAuth(self):
        """Ensures the User's requests session has a valid authorization"""
        self.rs.headers.update(
            {"authorization": "Bearer " + self.Tokenmanager.get_token()})
        # do this often - perhaps we could move session management to estoken? idk lol
        # maybe a decorator-worthy function
    def refreshUserData(self):
        self.readyAuth()
        self.user = self.rs.get("https://api.everskies.com/user")
        if self.user.ok:
            self.user = json.loads(self.user.text)
        else:
            raise errors.GetterError("User Data")

    def __repr__(self) -> str:
        if isinstance(self.user, dict):
            username = str(self.user.get("alias", "Unknown"))
        else:
            username = "Unknown"
        return str(f"User {username}")

    def getData(self) -> dict:
        """Meant for debugging and checking the internal status of any everskies User instance
        Any useful debugging data can be added here"""
        log.info("Ok! Getting data.")
        return {
            "user": self.user,
            "Tokenmanager": self.Tokenmanager.get_data(),
        }

    def setToken(self, refresh_token: str, **kwargs):
        self.Tokenmanager = token.Tokenmanager(
            refresh_token=refresh_token,
            refresh_token_expires=kwargs.get("refresh_token_expires"),
            access_token_expires_after=kwargs.get("access_token_expires_after",
                                                  1800),
            refresh_token_proxy=kwargs.get("refresh_token_proxy"),
        )
        log.info(
            "Set refresh token! It is recommended that you refresh the access token through "
            "User.Tokenmanager.do_refresh_token() , as the access token is what controls the currently used "
            "account")

    def createReply(self, forumid: int, text: str, **kwargs) -> requests.models.Response:
        self.readyAuth()
        data = {
            "content": text,
            "parent_reply_id": kwargs.get("parent_reply_id"),
            "attachments": kwargs.get("attachments", []),
        }
        url = f"https://api.everskies.com/discussion/{forumid}/reply"
        r = self.rs.post(url, data=json.dumps(data))
        if r.ok:
            log.info("successfully created post")
            return r
        log.error(f"Failed to create reply on {forumid}")
        return r

    def createPost(self, title: str, text: str, categoryid=8, **kwargs) -> requests.models.Response:
        self.readyAuth()
        # {"title":"hi","tw":null,"tw_reason":null,"tags":"","category_id":8,"club_category_id":null,"content":"lol","event":null,"attachments":[]}
        data = {
            "title": title,
            "tw": kwargs.get("tw"),
            "tw_reason": kwargs.get("tw_reason"),
            "tags": kwargs.get("tags", ""),
            "category_id": categoryid,
            "club_category_id": kwargs.get("club_category_id"),
            "content": text,
            "event": kwargs.get("event"),
            "attachments": kwargs.get("attachments", []),
        }
        # debug:
        # print(data)
        # print(json.dumps(data))
        url = "https://api.everskies.com/discussion/create"
        r = self.rs.post(url, data=json.dumps(data))
        if r.ok:
            log.info(f"successfully created post {title}")
            return r
        log.error("Failed to create post")
        return r

    def claimGift(self, code) -> requests.models.Response:
        self.readyAuth()
        r = self.rs.post(
            "https://api.everskies.com/payments/gift/claim",
            data=json.dumps({"code": code}),
        )
        if r.ok:
            log.info(f"Claimed gift {code} successfully!")
            return r
        log.error("Failed to claim gift")
        return r

    def setLayout(self, layout: str, mode="create", **kwargs) -> requests.models.Response:
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
        # work in progress!
        # doesn't support images completely yet- probably an easy fix

        def rebuild_data(data):
            #very much work in progress
            """Attempts to take profile data from api/user/layout?search=((userid)) and edit it to be apply-able to
            one's own profile through morphing the data Used in "stealing" anothers profile

            TODO: Implement method to take images from other's profiles
            """
            datatemp = data["userProfileElements"]
            for element in datatemp:
                element["id"] = -26045899
                element["user_profile_layout_id"] = None
            datatemp = {
                "elements": datatemp,
                "layout": {
                    "id": None,
                    "name": kwargs.get("name", "new!"),
                    "themeColor": data.get("themeColor", None),
                    "showClouds": data.get("showClouds", None),
                    "backgroundRepeat": data.get("backgroundRepeat", None),
                    "backgroundSize": data.get("backgroundSize", None),
                    "backgroundUrl": data.get("backgroundUrl", None),
                },
                "apply": kwargs.get("apply", False),
            }

            return datatemp

        # ugly elif chain :(( python match case better release soon
        if mode == "steal":
            t_layout = kwargs.get("steal_url")

            if t_layout:
                """TODO:
                Perhaps allow grabbing from just user id alone,
                Ensure consistent results - Fix images!
                Maybe error if specified user to steal from has blank layout
                """
                layout = json.loads(self.rs.get(t_layout).text)
            layout = rebuild_data(layout)
            self.readyAuth()
            return self.rs.post("https://api.everskies.com/user/layout/update",
                         data=json.dumps(layout))

        elif mode == "create":
            raise NotImplementedError
        elif mode == "update":
            raise NotImplementedError
        else:
            log.warning("Not a valid mode!")
            raise NotImplementedError

    def auctionBid(self, itemid: int, amount: int, **kwargs) -> requests.models.Response:
        # TODO: Add kwargs or remove the option to input them!
        self.readyAuth()
        r = self.rs.post(
            f"https://api.everskies.com/outlet/bid/{itemid}",
            data=json.dumps({"price": amount}),
        )
        if r.ok:
            return r
        log.error(f"Failed to bid {amount} on {itemid}")
        return r

    def createTrade(self, userid: int, **kwargs) -> requests.models.Response:
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
        Returns a requests.response object
        """
        self.readyAuth()
        trade = {
            "user_id": userid,
            "offeredItemSetIds": kwargs.get("offeredItemSets", []),
            "offeredItemVariationIds": kwargs.get("offeredItemVariations", []),
            "requestedItemSetIds": kwargs.get("requestItemSets", []),
            "requestedItemVariationIds": kwargs.get("requestItemVariations",
                                                    []),
            "offer_primary": kwargs.get("offerPrimary"),
            "offer_secondary": kwargs.get("offerSecondary"),
            "request_primary": kwargs.get("requestPrimary"),
            "request_secondary": kwargs.get("requestSecondary"),
        }
        r = self.rs.post("https://api.everskies.com/user/message/trade",
                         data=json.dumps(trade))
        if r.ok:
            log.info(
                f"Successfully sent trade request to {userid}, data: {kwargs}")
            return r
        log.error(
                f"Failed to send trade request to {userid}, status code: {r.status_code}")
        return r

    def cancelTrade(self, tradeid: int) -> requests.models.Response:
        self.readyAuth()
        r = self.rs.post(
            f"https://api.everskies.com/user/message/trade/{tradeid}/cancel",
            data="")
        if r.ok:
            log.info(f"Cancelled trade id {tradeid}")
            return r
        log.error(
            f"Failed to cancel trade id {tradeid}. Status code: {r.status_code}"
        )
        return r

    def acceptTrade(self, tradeid: int) -> requests.models.Response:
        self.readyAuth()
        r = self.rs.post(
            f"https://api.everskies.com/user/message/trade/{tradeid}/accept",
            data="")
        if r.ok:
            log.info(f"Accepted trade id {tradeid}")
            return r
        log.error(
            f"Failed to accept trade id {tradeid}. Status code: {r.status_code}"
        )
        return r

    def getDailyReward(self) -> requests.models.Response:
        """Does not claim daily reward, only GET's the endpoint and returns data as dict
        Returns a dict"""
        self.readyAuth()
        r=self.rs.get("https://api.everskies.com/user/reward")
        if r.ok:
            log.debug("Retrieved daily reward")
            return r
        log.error(f"failed to get daily reward. Status code: {r.status_code}")
        return r

    def claimDailyReward(self) -> requests.models.Response:
        """POSTs to ES daily reward that it is done!
        Returns request object"""
        self.readyAuth()
        r=self.rs.post("https://api.everskies.com/user/claim-reward",
                            json={"done": True})
        if r.ok:
            log.debug("Claimed daily reward")
            return r
        log.error("failed to claim daily reward")
        return r

    def friendReq(self, userid: int, message: str = "", **kwargs) -> requests.models.Response:
        data={
                'message': message
                }
        url=f'https://api.everskies.com/user/friends/{id}/add'
        
        self.readyAuth()
        r=self.rs.post(url, data=json.dumps(data))
        
        if r.ok:
            log.info(f'friended {id}')
            return r

        log.error(f"unable to friend {id}")
        return r
