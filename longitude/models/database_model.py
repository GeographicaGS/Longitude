from abc import ABC
from ..config import cfg
from .base_models import CartoModel, PostgresModel


class DatabaseModel(ABC):

    def __init__(self):
        if cfg['DATABASE_MODEL'] == 'CARTO':
            self.base_model = CartoModel()
        elif cfg['DATABASE_MODEL'] == 'POSTGRES':
            self.base_model = PostgresModel()
        else:
            raise Exception('You need to specify a DATABASE_MODEL in environment variables')

    def query(self, sql_query, opts=None, **kwargs):
        return self.base_model.query(sql_query, opts, **kwargs)
