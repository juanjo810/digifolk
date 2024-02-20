import sqlalchemy as sa
from sqlalchemy.orm import relationship
from app.models.base import Base

class ListItem(Base):
    __tablename__ = "items"
    id_db= sa.Column(sa.Integer, primary_key=True)
    type_item = sa.Column(sa.Integer)
    id = sa.Column(sa.Integer)
    name = sa.Column(sa.String)

    class Config:
        validate_all = True