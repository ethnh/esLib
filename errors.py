#!/usr/bin/env python3
class RefreshError(Exception):
    def __init__(self, userid="None"):
        super().__init__(f"User ID {userid} Failed to refresh token.")


class TokenExpiredError(Exception):
    def __init__(self, ttype="Unknown"):
        super().__init__(f"{ttype} Token has expired.")


class CreationError(Exception):
    def __init__(self, creating="Unknown"):
        super().__init__(f"Failed to create {creating}")


class GetterError(Exception):
    def __init__(self, getting="Unknown"):
        super().__init__(f"Failed to get {getting}")


class SetterError(Exception):
    def __init__(self, setting="Unknown"):
        super().__init__(f"Failed to set {setting}")

