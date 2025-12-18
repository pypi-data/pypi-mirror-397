from enum import Enum


class AuthenticationState(Enum):
    """
    The authentication status is used
    to indicate whether a user is authenticated or not.

    Attrtibutes:
        FAILURE (int): Authentication failure
        FALLTHROUGH (int): Unknown user (fallthrough)
        TEMPORARILY (int): Authentication failure where
                           the data could (temporarily) not be verified
    """

    FAILURE = -1
    FALLTHROUGH = -2
    TEMPORARILY = -3


class GetInfoState(Enum):
    """
    The get info status is used to indicate
    if the get info request is successful or not.

    Attrtibutes:
        FAILURE (bool): if information is not present, fall through
        SUCCESS (bool): if information is present
    """

    FALLTHROUGH = False
    SUCCESS = True


class NameToIdState(Enum):
    """
    The name to id status is used to indicate
    if the name to id request is successful or not.

    Attrtibutes:
        UNKNOWN (int): if user is unknown
    """

    UNKNOWN = -2


class IdToNameState(Enum):
    """
    The id to name status is used to indicate
    if the id to name request is successful or not.

    Attrtibutes:
        UNKNOWN (str): if id is unknown
    """

    UNKNOWN = ""


class IdToTextureState(Enum):
    """
    The id to texture status is used to indicate
    if the id to texture request is successful or not.

    Attrtibutes:
        UNKNOWN (byte): if empty texture for unknown users
                        or users without textures.
    """

    UNKNOWN = b""


class RegisterUserState(Enum):
    """
    The register user status is used to indicate
    if the register user request is successful or not.

    Attrtibutes:
        FAILURE (int): if registration failed
        FALLTHROUGH (int): if registration fallthrough
    """

    FAILURE = -1
    FALLTHROUGH = -2


class UnregisterUserState(Enum):
    """
    The unregister user status is used to indicate
    if the unregister user request is successful or not.

    Attrtibutes:
        SUCCESS (int): if unregistration succeeded
        FAILURE (int): if unregistration failed
        FALLTHROUGH (int): if unregistration fallthrough
    """

    SUCCESS = 1
    FAILURE = 0
    FALLTHROUGH = -1


class SetInfoState(Enum):
    """
    The set info status is used to indicate
    if the set info request is successful or not.

    Attrtibutes:
        SUCCESS (int): if set info succeeded
        FAILURE (int): if set info failed
        FALLTHROUGH (int): if set info fallthrough
    """

    SUCCESS = 1
    FAILURE = 0
    FALLTHROUGH = -1


class SetTextureState(Enum):
    """
    The set texture status is used to indicate
    if the set texture request is successful or not.

    Attrtibutes:
        SUCCESS (int): if set texture succeeded
        FAILURE (int): if set texture failed
        FALLTHROUGH (int): if set texture fallthrough
    """

    SUCCESS = 1
    FAILURE = 0
    FALLTHROUGH = -1
