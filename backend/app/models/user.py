import sqlalchemy as sa
from sqlalchemy.orm import relationship
from app.models.base import Base


class User(Base):
    __tablename__ = "user"

    user_id = sa.Column(sa.Integer, primary_key=True)
    first_name=sa.Column(sa.String)
    last_name=sa.Column(sa.String)
    email = sa.Column(sa.String, unique=True, nullable=False)
    username = sa.Column(sa.String, unique=True, nullable=False)
    password = sa.Column(sa.String)
    is_admin = sa.Column(sa.Boolean, default=False, nullable=False)
    institution = sa.Column(sa.String)
    # Relationships
    piece = relationship("Piece", back_populates="users_rel")

    class Config:
        use_enum_values = True
        validate_all = True
