import sqlalchemy

metadata = sqlalchemy.MetaData()


users_table = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column(
        "id",
        sqlalchemy.Integer,
        sqlalchemy.Sequence('users_id_seq', start=1, increment=1),
        primary_key=True,
        autoincrement=True
        ),
    sqlalchemy.Column("email", sqlalchemy.String(), unique=True, index=True),
    sqlalchemy.Column("hashed_password", sqlalchemy.String()),
    sqlalchemy.Column(
        "is_active",
        sqlalchemy.Boolean(),
        server_default=sqlalchemy.sql.expression.true(),
        nullable=False,
    ),
    sqlalchemy.Column(
        'auth_token', sqlalchemy.String(),
        default=""),
    sqlalchemy.Column(
        "role",
        sqlalchemy.String()),
)

tokens = sqlalchemy.Table(
    "tokens",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column(
        "access_token",
        sqlalchemy.String(256),
        unique=True,
        nullable=False,
        index=True,
    ),
    sqlalchemy.Column("expires", sqlalchemy.DateTime()),
    sqlalchemy.Column("user_id", sqlalchemy.ForeignKey("users.id")),
)
