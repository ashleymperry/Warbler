"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for users."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

    def test_user_model(self):
        """Does basic model work?"""

        u = User.signup(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD",
            image_url=""
        )
        
        u2 = User.signup(
            email='testtest@test.com',
            username='testuser2',
            password="HASHED_PASSWORD",
            image_url=""
        )
        
        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)
        self.assertEqual(u.username, 'testuser')
        self.assertEqual(u.email, 'test@test.com')
        self.assertEqual(u.is_followed_by(u2), False)
        self.assertEqual(u2.is_following(u), False)
        
        # Have user 2 follow user
        u2.following.append(u)
        db.session.add(u2)
        db.session.commit()
        
        self.assertEqual(u.is_followed_by(u2), True)
        self.assertEqual(u2.is_following(u), True)
        self.assertEqual(len(u.followers), 1)
        
        self.assertEqual(str(u), f"<User #{u.id}: {u.username}, {u.email}>")
        
        #Test signup class method
        
        u3 = User.signup(
            email='testy@test.com',
            username='testuser',
            password='HASHED_PASSWORD',
            image_url=""
        )
        
        try:
            db.session.commit()
        except:
            db.session.rollback()
            self.assertIsNone(u3.id)
            
        u3 = User.signup(
            email='testy@test.com',
            username='testuser3',
            password='HASHED_PASSWORD',
            image_url=""
        )
        
        try:
            db.session.commit()
        except:
            self.assertIsNone(u3.id)
            
        self.assertIsNotNone(u3.id)
        
        user = User.authenticate(u3.username, 'HASHED_PASSWORD')
        self.assertEqual(user, u3)
        
        user = User.authenticate(u3.username, 'HASH_PASSWORD')
        self.assertFalse(user)
            