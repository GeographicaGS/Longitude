from longitude.models.postgresqlmodel import CRUDModel


class CredentialModel(CRUDModel):
    table_name = 'longitude_credentials'
