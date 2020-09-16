from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE = 'keywords_finder'
USER = 'keywords_finder'
PASSWORD = 'keywords_finder'
HOST = 'postgres'
PORT = '5432'
DB_NAME = 'keywords_finder'
engine = create_engine(f'postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB_NAME }')

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
