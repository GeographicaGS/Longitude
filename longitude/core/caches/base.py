import hashlib
import logging
import pickle

from longitude.core.common.query_response import LongitudeQueryResponse


class LongitudeCache():

    def __init__(self, options={}):
        self.logger = logging.getLogger(self.__class__.__module__)

    @staticmethod
    def generate_key(query_template, params):
        """
        This is the default key generation algorithm, based in a digest from the sha256 hash of the query and parameters

        Override this method to provide your own key generation in case you need a specific way to store your cache.

        :param query_template: Query template (including placeholders) as it should be asked to the database
        :param params: Dictionary of values to be replaced in the placeholders in a safe manner
        :return: A (most likely) unique hash, generated from the query text
        """
        query_payload = str(query_template) + str(params)
        return hashlib.sha256(query_payload.encode('utf-8')).hexdigest()

    def get(self, query_template, query_params=None):
        if query_params is None:
            query_params = {}
        payload = self.execute_get(self.generate_key(query_template, query_params))
        return self.deserialize_payload(payload)

    async def get_async(self, query_template, query_params=None):
        if query_params is None:
            query_params = {}
        payload = await self.execute_get_async(self.generate_key(query_template, query_params))
        return self.deserialize_payload(payload)

    def put(self, query_template, payload, query_params=None, expiration_time_s=None):
        if query_params is None:
            query_params = {}
        if not isinstance(payload, LongitudeQueryResponse):
            raise TypeError('Payloads must be instances of LongitudeQueryResponse!')
        return self.execute_put(
            self.generate_key(query_template, query_params),
            self.serialize_payload(payload),
            expiration_time_s=expiration_time_s
        )

    async def put_async(self, query_template, payload, query_params=None, expiration_time_s=None):
        if query_params is None:
            query_params = {}
        if not isinstance(payload, LongitudeQueryResponse):
            raise TypeError('Payloads must be instances of LongitudeQueryResponse!')
        return await self.execute_put_async(
            self.generate_key(query_template, query_params),
            self.serialize_payload(payload),
            expiration_time_s=expiration_time_s
        )

    def execute_get(self, key):
        """
        Custom get action over the cache. The application must call this method for generic cache use. For queries, you
        should use .get(...)

        :return: Query response as it was saved if hit. None if miss.
        """
        raise NotImplementedError

    async def execute_get_async(self, key):
        raise NotImplementedError

    def execute_put(self, key, payload, expiration_time_s=None):
        """
        Custom put action over the cache. The application must call this method for generic cache use. For queries, you
        should use .put(...)

        :return: True if key was overwritten. False if key was new in the cache.
        """
        raise NotImplementedError

    async def execute_put_async(self, key, payload, expiration_time_s=None):
        raise NotImplementedError

    def flush(self):
        """
        Custom action to make the cache empty

        :return:
        """
        raise NotImplementedError

    async def flush_async(self):
        raise NotImplementedError

    @staticmethod
    def serialize_payload(payload):
        if payload:
            return pickle.dumps(payload)
        return None

    @staticmethod
    def deserialize_payload(payload):
        if payload:
            return pickle.loads(payload)
        return None
