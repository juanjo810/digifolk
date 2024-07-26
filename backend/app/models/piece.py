import sqlalchemy as sa
from sqlalchemy.orm import relationship
from app.models.base import Base
from sqlalchemy.dialects.postgresql import JSONB
#from app.models.relationships import model_music
#from app.models.country import Country


class Piece(Base):
    __tablename__ = "piece"
    music_id = sa.Column(sa.Integer, primary_key=True)

    #Uploader Metadata
    publisher = sa.Column(sa.String) #
    creator = sa.Column(sa.String)  #
    title = sa.Column(sa.ARRAY(sa.String)) #
    rights = sa.Column(sa.Integer) #
    date = sa.Column(sa.String) #
    type_file = sa.Column(sa.Integer) #
    #formatting = sa.Column(sa.String)
    contributor_role = sa.Column(sa.ARRAY(JSONB)) # Save it as a dictionary creator+role
    desc = sa.Column(sa.String)
    
    # Piece Metadata
	
    rightsp = sa.Column(sa.Integer)
    contributorp_role = sa.Column(sa.ARRAY(JSONB)) # save at as a dictionary contributor+role
    creatorp_role = sa.Column(sa.ARRAY(JSONB)) # save at as a dictionary contributor+role
    alt_title = sa.Column(sa.String)
    datep = sa.Column(sa.String)
    descp = sa.Column(sa.String)
    type_piece = sa.Column(sa.Integer)
    formattingp = sa.Column(sa.String)
    subject = sa.Column(sa.ARRAY(sa.String))
    language = sa.Column(sa.String)
    relationp = sa.Column(sa.ARRAY(sa.String))
    hasVersion = sa.Column(sa.ARRAY(sa.String))
    isVersionOf	= sa.Column(sa.ARRAY(sa.String))
    coverage = sa.Column(sa.String)
    temporal = sa.Column(JSONB) #Encoded as a dictionary with Century/Decade/Year
    spatial = sa.Column(JSONB) #Encoded as a dictionary with Country-State/Province-City-Location
    
    # Piece Analysis
    genre = sa.Column(sa.ARRAY(sa.String))
    meter = sa.Column(sa.String)
    tempo = sa.Column(sa.String)
    real_key = sa.Column(sa.String)
    mode = sa.Column(sa.String)
    instruments= sa.Column(sa.ARRAY(sa.String))

    title_xml=sa.Column(sa.String)
    xml = sa.Column(sa.String)
    mei = sa.Column(sa.String)
    midi = sa.Column(sa.String)
    audio = sa.Column(sa.String)
    video = sa.Column(sa.String)
    review = sa.Column(sa.Boolean)
    user_id = sa.Column(sa.Integer, sa.ForeignKey('user.user_id'))
    col_id = sa.Column(sa.Integer, sa.ForeignKey('piece_col.col_id'))
    
    # Relationships
    users_rel = relationship(
        "User", back_populates="piece"
    )
    col_rel = relationship(
        "PieceCol", back_populates="piece_col"
    )
    class Config:
        validate_all = True
