## Imports
from datetime import datetime
import logging
from multiprocessing import synchronize

from sqlalchemy import create_engine, BigInteger, Column, Integer, Boolean
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

import tweepy
from twitterconfig import twitter as config, postgres as dbConfig


# Database connection secrets
SERVER = dbConfig['server']
USER = dbConfig['user']
PASSWORD = dbConfig['password']
HOST = dbConfig['host']
PORT = dbConfig['port']
DB_NAME=dbConfig['db_name']

## Tweepy Authentication
CONSUMER_KEY = config['consumer_key']
CONSUMER_SECRET = config['consumer_secret']
ACCESS_KEY = config['access_key']
ACCESS_SECRET = config['access_secret']

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)

## Tweepy API
api = tweepy.API(auth)

## connection URL
url = f"{SERVER}://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB_NAME}"
## Database engine
engine = create_engine(url)
## Session maker
Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)
## Database metadata
Base = declarative_base()


class Twitter(Base):
    """Twitter table model. We only need the ID column"""

    __tablename__ = "twitter"

    tweet_id = Column(BigInteger, primary_key=True)


class Interactions(Base):
    """Interactions table"""

    __tablename__ = "twitter_interactions"

    tweet_id = Column(BigInteger, primary_key=True)
    likes = Column(Integer)
    retweets = Column(Integer)
    protected = Column(Boolean, unique=False, default=False)


def main():

    # Database connection
    Base.metadata.create_all(engine)
    logging.info(f"Database connection started at {datetime.now().strftime('%Y %m %d  %H:%M:%S')}")

    db = Session()
    logging.info(f"Session started at {datetime.now()}")

    # Get all tweet ids
    ids = db.query(Twitter).all()

    # Empty interactions table
    db.query(Interactions).delete(synchronize_session=False)
    db.commit()

    for element in ids:
    
        try:
            status = api.get_status(element.tweet_id)
            try:
                likes = status.retweeted_status.favorite_count
            except:
                likes = status.favorite_count

            new_interaction = Interactions(tweet_id=element.tweet_id, retweets=status.retweet_count, likes=likes, protected=False)
            db.add(new_interaction)
            db.commit()
            db.refresh(new_interaction)
        except tweepy.errors.TweepyException:
            new_interaction = Interactions(tweet_id=element.tweet_id, retweets=0, likes=0, protected=True)
            db.add(new_interaction)
            db.commit()
            db.refresh(new_interaction)

    logging.info(f"Interactions table updated at {datetime.now().strftime('%Y %m %d  %H:%M:%S')}")

    ## Close connection
    db.close()
    

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    main()
