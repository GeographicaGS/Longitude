"""init credentials

Revision ID: c6a61e3cc7ec
Revises: 
Create Date: 2018-03-20 15:00:08.997147

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c6a61e3cc7ec'
down_revision = None
branch_labels = ('longitude.credential',)
depends_on = None


def upgrade():

    conn = op.get_bind()

    op.create_table(
        'longitude_credentials',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False, autoincrement=True),
        sa.Column('active', sa.Boolean(), nullable=False, server_default=sa.true()),

        sa.Column('type', sa.String(32), nullable=True, server_default=None),

        sa.Column('auth_name', sa.Binary(), nullable=True, server_default=None),
        sa.Column('key', sa.Binary(), nullable=False),

        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.current_timestamp()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_onupdate=sa.func.current_timestamp()),

        sa.Column('expires', sa.DateTime(timezone=True), server_default=None)
    )

    conn.execute("CREATE EXTENSION pgcrypto")


def downgrade():
    conn = op.get_bind()

    op.drop_table('longitude_credentials')

    conn.execute("DROP EXTENSION pgcrypto")