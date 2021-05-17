#!/usr/bin/env python3
import json
import logging
import time

import requests
from everskies import errors
from everskies.utils import randomagent, refreshToken

log = logging.getLogger(__name__)


class Tokenmanager:
    """Pass it a refresh token and forget!
    Will request a new access token automatically as long as it is regularly
    get'd, or you can do do_refresh_token on access_token failure"""

    def __init__(
        self,
        refresh_token: str,
        refresh_token_expires: int = 0,
        access_token_expires_after: int = 1800,
        **kwargs,
    ):
        """Sets up token internals! Args: refresh_token : str, should be held in localstorage in a browser
        refresh_token_expires : time.time() (int) - when the refresh token should be considered invalid
        access_token_expires_after : int - how often to refresh access token Kwargs: "access_token" : If you want to
        explicitly pass in an access token "refresh_token_proxy" : a dict containing proxies in case of
        do_refresh_token failing to receive a requests.Session object example: {"http" :
        "http://proxy.proxy.com:12345", "https" : "https://proxy.proxy.com:12345"}
        See requests documentation for further information
        """
        self.refresh_token = refresh_token

        self._refresh_expires = refresh_token_expires
        # Expects time.time() or similar value

        self.__token = kwargs.get("access_token", False)
        # the token value - should only be set by this class

        self._token_expires_after = access_token_expires_after
        # how much to add to time.time() for _token_expires -
        # after this much time passes, the token should be refreshed!

        if self.__token:
            self._token_expires_after = time.time() + self._token_expires_after

        self._token_expires = 0
        # when the token will expire (time.time())
        # set all values beforehand so we can use getdata() lol
        # default is 0 so get_token refreshes token on first run

        self.refresh_token_proxy = kwargs.get("refresh_token_proxy")
        if self.refresh_token_proxy is None:
            self.refresh_token_proxy = {}

    def set_refresh_token(self, refresh_token: str, expires: int = 0):
        self.refresh_token = refresh_token
        # expects string
        self._refresh_expires = expires
        # expects time.time() or bool

    def get_token(self, allow_refresh: bool = True):
        """Get access token
        Checks if token is still valid, and whether or not to refresh in the event of invalid
        Raises everskies.errors.TokenExpiredError with message "Access" in event of disallowed to refresh
        """
        if self._token_expires < time.time():
            log.warning("token expired. refreshing")
            if allow_refresh:
                self.do_refresh_token()
            else:
                log.error(
                    f"access token {self.__token} of refresh token {self.refresh_token} expired"
                )
                raise errors.TokenExpiredError("Access")
        return self.__token

    def do_refresh_token(self, session=None):
        """Refresh's token Args: session : requests.Session should session be failed to pass or falsy,
        will use everskies.utils.defaultSession with self.refresh_token_proxy"""
        if session is None:
            session = requests.Session()
            session.headers.update(
                {
                    "content-type": "application/json",
                    "user-agent": randomagent(),
                }
            )
            if self.refresh_token_proxy:
                session.proxies.update(self.refresh_token_proxy)
            # defaultSession constructs a requests.Session object

        if self._refresh_expires:
            # if the refresh token can expire, make sure it's still valid
            if self._refresh_expires < time.time():
                log.error(f"refresh token {self.refresh_token} expired")
                raise errors.TokenExpiredError("Refresh")

        else:
            # if refresh token can never expire, just refresh lol
            self.__token = json.loads(refreshToken(session, self.refresh_token))[
                "access_token"
            ]
            # refreshToken returns token as string
            self._token_expires = time.time() + self._token_expires_after

    def get_data(self):
        """Returns all relevant data as a dict."""
        return {
            "access_token": self.__token,
            "access_token_expires": self._token_expires,
            "access_token_expires_after": self._token_expires_after,
            "refresh_token": self.refresh_token,
            "refresh_token_expires": self._refresh_expires,
            "refresh_token_proxy": self.refresh_token_proxy,
        }
