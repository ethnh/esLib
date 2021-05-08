#!/usr/bin/env python3

#############################################
#               TODO
#  >  Implement Custom Errors
#  >  Add functionality to request api data
#  .
#  ?   > This should be written here in case
#      > I get around to writing ES-DB - 
#      > as ES-DB will make getting threads//
#      > userdata // etc much easier
#  .
#  ?   > Default proxy should also be added   
#      > here, as unless we require auth to
#      > collect, we should not identify
#      > ourselves.
#      > !!       ANON > KNOWN       !!
#
#  >  Ensure nothing is leaked! Proxies
#      > Everywhere!
#
#  !! Utils is about getting data, other
#  !! files will manage setting data.
#  !! (eg. esuser has createReply)
#
##############################################

from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem, SoftwareType, HardwareType
software_names = [SoftwareName.CHROME.value]
software_types = [SoftwareType.WEB_BROWSER.value]
hardware_types = [HardwareType.MOBILE.value, HardwareType.COMPUTER.value]
operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value, OperatingSystem.MAC.value]
user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems)
import requests
import jwt
from everskies import errors

def randomagent():
    return(user_agent_rotator.get_random_user_agent())

def defaultSession(proxies: dict = {}):
    """
    Default session for all requests!
    Generates a Requests Session with a random user-agent. Change this to change the default user agent.
    Proxies format:
        proxies = {
            'http' : 'http://proxy.com',
            'https' : 'https://proxy.com'
        }
    """
    session=requests.Session()
    session.headers.update({
        "content-type": "application/json",
        "user-agent": randomagent(),
    })
    if proxies:
        session.proxies.update(proxies)
    return session

def getUid(token: str):
    tdata = jwt.get_unverified_header(token)
    uid = tdata['user_id']
    return uid

def refreshToken(session: requests.Session, refresh_token: str, retries=10):
    if refresh_token:
        while retries is not 0:
            retries-=1
            try:
                # Get new access token
                print("Refreshing access token")
                r = session.post("https://api.everskies.com/user/refresh-token",
                                 json={"token": refresh_token}, timeout=5)
                if r.ok:
                    break
            except ConnectionError as err:
                time.sleep(1)
        if retries is 0:
            print("Could not refresh token")
            raise errors.RefreshError(userid=getUid(refresh_token))
            #self.disconnect()
        else:
            print("ok refreshed swag token")
            return r.text
            #return token just in case lol
    else:
        print("no refresh token supplied or invalid refresh token supplied")
        raise errors.RefreshError(userid=getUid(refresh_token))

def isbanned(uid, rs=defaultSession()):
    params = (
        ('search', '[{"attribute":"id","comparator":"eq","value":' + str(uid) + '}]'),
        ('single', '1'),
        ('withOptions', '1'),
    )
    r = rs.get('https://api.everskies.com/users', params=params)
    try:
        json.loads(r)['ban_id']
        return True
    except:
        return False
