from logging import debug, error

from passlib.hash import bcrypt, bcrypt_sha256


def allianceauth_check_hash(password, hash, hash_type):
    """
    Python implementation of the AllianceAuth MumbleUser hash function

    See https://gitlab.com/allianceauth/allianceauth/-/blob/master/allianceauth/services/modules/mumble/models.py
    :param password: Password to be verified
    :param hash: Hash for the password to be checked against
    :param hash_type: Hashing function originally used to generate the hash
    """
    debug(f"Checking password with hash type: {hash_type}")
    if not password:
        error("Empty password")
        return False
    if not hash:
        error("Empty hash")
        return False
    try:
        if hash_type == "bcrypt-sha256":
            return bcrypt_sha256.verify(password, hash)
        else:
            return bcrypt.verify(password, hash)
    except Exception as e:
        error(f"Failed to verify password hash: {e}")
        return False
