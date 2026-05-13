from sqlalchemy import create_engine, Column, String, Integer, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

engine = create_engine("sqlite:///videos.db")
Base = declarative_base()
Session = sessionmaker(bind=engine)

class Project(Base):
    __tablename__ = "projects"
    id           = Column(String, primary_key=True)
    topic        = Column(String)
    audience     = Column(String)
    duration_sec = Column(Integer, default=60)
    language     = Column(String, default="id")
    status       = Column(String, default="draft")
    scenes_json  = Column(Text)       # scenes disimpan sebagai JSON string
    video_path   = Column(String)
    error_msg    = Column(String)
    created_at   = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(engine)
