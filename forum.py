#!/usr/bin/env python3
import logging

import requests
from everskies import utils

log = logging.getLogger(__name__)


class Forum(object):
    """Everskies Forum
    Class meant to handle actions one could take on a forum, or data one could try to get from one.
    """
    def __init__(self, fid: int, **kwargs):
        """Set URLs for data aquisition. Use getter or setter to change or get these values.
                Args:
        0            fid: int, represents the forum ID
                Kwargs:
                    "apiUrl" : str, example:
                                    https://api.everskies.com/discussion/1
                    "forumTitle" : str, should be the safe-title if you get'd the data
                                    example:
                                    hi-everyone-welcome111
                    "humanUrl" : str, example:
                                    https://everskies.com/community/forums/general/hi-everyone-welcome111-12345

        """
        self.__id = fid
        self.__api_url = kwargs.get(
            "apiUrl", f"https://api.everskies.com/discussion/{self.__id}")
        self._forum_title = kwargs.get("forumTitle")
        self.__human_url = kwargs.get(
            "humanUrl",
            f"https://everskies.com/community/forums/{self._forum_title}-{self.__id}",
        )

    def __repr__(self):
        return f"Forum {self.__id} ({self._forum_title})"

    # add stuff lol

class Reply(object):
    pass
