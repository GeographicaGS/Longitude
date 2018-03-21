from sanic import Blueprint
from sanic.response import json

from .model import CredentialModel

bp = Blueprint('longitude.credentials', url_prefix='/credentials')


@bp.get('/')
async def credentials(request):

    m = CredentialModel(request.app.sql_model)

    return json(await m.list())


@bp.get('/<integer:eid>')
async def credentials(request, eid):

    m = CredentialModel(request.app.sql_model)

    return json(await m.get(eid))


@bp.post('/')
async def credentials(request):
    return json({
        'active': True,
        'created': '2018-01-31T21:19.000',
        'expires': '2019-01-31T21:19.000',
         # PGP-encoded
        'auth_name': '893249023490890fjasdgasdasd',
        'key': '893249023490890fjasdgasdasd',
    })





@bp.put('/<integer_arg:eid>')
async def credentials(request, eid):
    return json({
        'active': True,
        'created': '2018-01-31T21:19.000',
        'expires': '2019-01-31T21:19.000',
         # PGP-encoded
        'auth_name': '893249023490890fjasdgasdasd',
        'key': '893249023490890fjasdgasdasd',
    })


@bp.delete('/<integer_arg:eid>')
async def credentials(request, eid):
    pass
