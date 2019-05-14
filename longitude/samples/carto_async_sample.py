import os
import sys
import asyncio
import aiohttp  # noqa

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))  # noqa
from longitude.core.data_sources.carto_async import CartoAsyncDataSource
from longitude.samples.config import config


async def query_1(ds):
    print('Running query_1...')
    res = await ds.query('select * from country_population limit 30')
    print('query_1 finished')
    return res


async def query_2(ds):
    print('Running query_2...')
    res = await ds.query('select count(*) from country_population')
    print('query_2 finished')
    return res


async def query_3(ds):
    print('Running query_3...')
    res = await ds.query('select max(pop2005) from country_population')
    print('query_3 finished')
    return res


async def main():
    # If you have your own aiohttp ClientSession object:
    # async with aiohttp.ClientSession() as session:
    #     ds = CartoAsyncDataSource(
    #         user=config['carto_user'],
    #         api_key=config['carto_api_key'],
    #         options={
    #             'session': session  # Optional
    #         }
    #     )

    #     # Parallel execution of coroutines:
    #     res_1, res_2, res_3 = await asyncio.gather(
    #         query_1(ds), query_2(ds), query_3(ds)
    #     )

    # Otherwise, if you don't want to pass your own ClientSession in the constructor,
    # this would be the recommended way to use this datasource:
    async with CartoAsyncDataSource(config['carto_user'], config['carto_api_key']) as ds:
        # Parallel execution of coroutines:
        res_1, res_2, res_3 = await asyncio.gather(
            query_1(ds), query_2(ds), query_3(ds)
        )

    print('Query 1: {}'.format(res_1.meta))
    # [print('id={}, pop={}'.format(r['cartodb_id'], r['pop2005'])) for r in res_1.rows]

    print('Query 2: {}. Result: {}'.format(
        res_2.meta,
        [r for r in res_2.rows]
    ))

    print('Query 3: {}. Result: {}'.format(
        res_3.meta,
        [r for r in res_3.rows]
    ))


if __name__ == "__main__":
    asyncio.run(main())
