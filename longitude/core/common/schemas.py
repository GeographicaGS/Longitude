from marshmallow import Schema, fields


class LongitudeDefaultSchema(Schema):
    pass


class LongitudeOkResponseSchema(LongitudeDefaultSchema):
    payload = fields.Raw(default={})


class LongitudeCreated(LongitudeDefaultSchema):
    pass


class LongitudeAccepted(LongitudeDefaultSchema):
    pass


class LongitudeBadRequest(LongitudeDefaultSchema):
    errors = fields.Dict(default={})


class LongitudeEmptyContent(LongitudeDefaultSchema):
    pass


class LongitudeNotFoundResponseSchema(LongitudeDefaultSchema):
    errors = fields.String(default="Resource not found")


class LongitudeNotAllowedResponseSchema(LongitudeDefaultSchema):
    errors = fields.String(default="Not authorized")


class LongitudeServerError(LongitudeDefaultSchema):
    errors = fields.String(default="Internal server error. Contact support team.")
