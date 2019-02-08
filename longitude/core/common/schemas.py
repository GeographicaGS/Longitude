from marshmallow import Schema, fields


class LongitudeDefaultSchema(Schema):
    pass


class LongitudeOkResponseSchema(LongitudeDefaultSchema):
    payload = fields.Raw(default={})


class LongitudeCreated(LongitudeDefaultSchema):
    pass


class LongitudeAccepted(LongitudeDefaultSchema):
    pass


class LongitudeEmptyContent(LongitudeDefaultSchema):
    pass


class LongitudeNotFoundResponseSchema(LongitudeDefaultSchema):
    error = fields.String(default="Resource not found")


class LongitudeNotAllowedResponseSchema(LongitudeDefaultSchema):
    error = fields.String(default="Not authorized")


class LongitudeServerError(LongitudeDefaultSchema):
    error = fields.String(default="Internal server error. Contact support team.")
