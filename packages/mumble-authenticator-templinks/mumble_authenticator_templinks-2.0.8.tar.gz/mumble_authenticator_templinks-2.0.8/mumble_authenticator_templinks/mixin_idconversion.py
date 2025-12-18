class IDConversionMixin:
    def __init__(self, base_offset: int = 1000000000):
        self.base_offset = base_offset
        self.tempuser_offset = base_offset * 2

    def _to_mumble_baseuser_id(self, user_id: int) -> int:
        """
        Convert user id from database to mumble user id
        """
        return user_id + self.base_offset

    def _to_baseuser_id(self, mubmeble_user_id: int) -> int:
        """
        Convert user id from mumble user id to database user id
        """
        return mubmeble_user_id - self.base_offset

    def _to_mumble_tempuser_id(self, user_id: int) -> int:
        """
        Convert Templink user id from database to mumble user id
        """
        return user_id + self.tempuser_offset

    def _to_tempuser_id(self, mubmeble_user_id: int) -> int:
        """
        Convert user id from mumble user id to Templink database user id
        """
        return mubmeble_user_id - self.tempuser_offset

    def _is_tempuser(self, mubmeble_user_id: int) -> bool:
        """
        Check if the given mubmeble_user_id is for a temporary user.

        Returns True if the ID belongs to a temporary user, False otherwise.
        """
        return mubmeble_user_id >= self.tempuser_offset

    def _is_baseuser(self, mubmeble_user_id: int) -> bool:
        """
        Check if the given mubmeble_user_id is for a base user.

        Returns True if the ID belongs to a regular user, False otherwise.
        """
        return self.base_offset <= mubmeble_user_id < self.tempuser_offset
