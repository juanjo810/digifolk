import sqlalchemy as sa
from sqlalchemy.orm import relationship
from app.models.base import Base
from sqlalchemy.dialects.postgresql import JSONB #just for Postresql, otherwise use only json from sqlalchemy.JSON
#from app.models.relationships import model_music
#from app.models.country import Country

class PieceCol(Base):
    __tablename__ = "piece_col"
    col_id = sa.Column(sa.Integer, primary_key=True) 
    
    title=sa.Column(sa.ARRAY(sa.String)) #
    rights=sa.Column(sa.Integer) #
    extent=sa.Column(sa.String) #
    date=sa.Column(sa.String) #
    subject=sa.Column(sa.ARRAY(sa.String)) #
    language=sa.Column(sa.String) #
    creator_role = sa.Column(sa.ARRAY(JSONB)) # Save it as a dictionary
    contributor_role = sa.Column(sa.ARRAY(JSONB)) # Save it as a dictionary
    publisher = sa.Column(sa.String) # Save it as a dictionary
    source = sa.Column(sa.String) #
    source_type = sa.Column(sa.Integer) #
    description = sa.Column(sa.String) #
    formatting = sa.Column(sa.String) #
    relation = sa.Column(sa.ARRAY(sa.String)) #
    temporal = sa.Column(JSONB) #Encoded as a dictionary with Century/Decade/Year
    rights_holder = sa.Column(sa.String) #
    spatial = sa.Column(JSONB) #Encoded as a dictionary with Country-State/Province-City-Location
    coverage = sa.Column(sa.String) #
    review = sa.Column(sa.Boolean) #
    code = sa.Column(sa.String) #

    piece_col = relationship("Piece", back_populates="col_rel")
    
    class Config:
        validate_all = True
    