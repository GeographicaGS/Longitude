from .base import DataSource


class AsyncDataSource(DataSource):

    async def query(self, query_template, params=None, cache=True, expiration_time_s=None,
                    query_config=None, **opts):
        """
        This method has to be called to interact with the data source. Each children class will
        have to implement its own .execute_query(...) with the specific behavior for each interface.

        :param query_template: Unformatted SQL query
        :param params: Values to be passed to the query when formatting it
        :param cache: Boolean to indicate if this specific query should use cache or not
            (default: True)
        :param expiration_time_s: If using cache and cache supports expiration, amount of seconds
            for the payload to be stored
        :param query_config: Specific query configuration. If None, the default one will be used.
        :param opts:
        :return: Result of querying the database
        """
        if params is None:
            params = {}

        response = None
        if self._cache and self._use_cache and cache:
            response = await self._cache.get_async(query_template, params)

        if response:
            response.mark_as_cached()
        else:
            response = await self.execute_query(
                query_template=query_template,
                params=params,
                query_config=query_config,
                **opts
            )

            response = self.parse_response(response)
            if self._cache and self._use_cache and cache:
                await self._cache.put_async(
                    query_template,
                    payload=response,
                    query_params=params,
                    expiration_time_s=expiration_time_s
                )

        return response
