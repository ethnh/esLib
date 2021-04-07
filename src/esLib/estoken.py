#!/usr/bin/env python3
import time
from esLib.utils import refreshToken, defaultSession
import json

class tokenManager():
    """Pass it a refresh token and forget! 
    Will request a new access token automatically as long as it is regularly get'd, or you can do do_refresh_token on access_token failure"""
    
    def __init__(self, refresh_token=False, refresh_token_expires=False, access_token_expires_after=1800, **kwargs):
        
        self.refresh_token=refresh_token
        #!!!
        #should be a string - required
        #!!!
        
        self._refresh_expires=refresh_token_expires
        #whether or not to stop refreshing after a certain time 
        #can also be a time.time() if you want it to not refresh after a certain time
        
        self.__token=False
        #the token value - should only be set by this class
        
        self._token_expires_after=access_token_expires_after
        #how much to add to time.time() for _token_expires - 
        #after this much time passes, the token should be refresh'd!
        
        self._token_expires=0
        #when the token will expire (time.time())
        #set all values beforehand so we can use getdata() lol
        #default is 0 so get_token refreshs token on first run
        
        self.refresh_token_proxy=kwargs.get("refresh_token_proxy", False)
    
    def set_refresh_token(self, refresh_token, expires=False):
        self.refresh_token=refresh_token
        #expects string
        self._refresh_expires=expires
        #expects time.time() or bool
    
    def get_token(self, allow_refresh=True):
        if self._token_expires < time.time():
            print('token expired. refreshing')
            if allow_refresh:
                self.do_refresh_token()
            else:
                raise Exception('Access_Token_Expired')
        return self.__token
    
    def do_refresh_token(self, session=False):
        if self._refresh_expires and (self._refresh_expires < time.time()):
            print(f'refresh token {self.refresh_token} expired')
            raise Exception('Refresh_Token_Expired')
            pass
        else:
            if session:
                self.__token=json.loads(refreshToken(session, self.refresh_token))["access_token"]
                #refreshToken returns token as string
            else:
                self.__token=json.loads(refreshToken(defaultSession(self.refresh_token_proxy), self.refresh_token))["access_token"]
                #defaultSession is a rotating proxy session - will just get the
            self._token_expires=time.time()+self._token_expires_after
    
    def get_data(self):
        return {
                'access_token' : self.__token,
                'access_token_expires' : self._token_expires,
                'access_token_expires_after' : self._token_expires_after,
                'refresh_token' : self.refresh_token,
                'refresh_token_expires' : self._refresh_expires,
		'refresh_token_proxy' : self.refresh_token_proxy,
                }

