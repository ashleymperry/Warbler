"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py

import pdb
import os
from unittest import TestCase

from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)
        
        self.test_message = Message(
            text="""Lorem ipsum dolor sit amet consectetur adipisicing 
            elit. Quibusdam, sed odio. Laudantium, commodi? Dictare!"""
        )
        
        db.session.add_all([self.testuser, self.test_message])
        self.testuser.messages.append(self.test_message)

        db.session.commit()
        
    def test_add_message(self):
        """Can use add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.order_by(Message.id.desc()).first()
            self.assertEqual(msg.text, "Hello")
            
    def test_show_message(self):        
        with self.client as c:
            content = self.test_message.text                                
            res = c.get(f'/messages/{self.test_message.id}')
            html = res.get_data(as_text=True)
            self.assertIn(content, html)
            
    def test_delete_message(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
                message_id = self.testuser.messages[0].id
            
            res = c.post(f'/messages/{message_id}/delete')
            user = User.query.get(self.testuser.id)
            self.assertEqual(res.status_code, 302)
            self.assertEqual(res.location, f'http://localhost/users/{self.testuser.id}')
            self.assertEqual(len(user.messages), 0)
    
    def test_delete_message_no_auth(self):
        with self.client as c:
            res = c.post(f'/messages/{self.test_message.id}/delete', follow_redirects=True)
            html = res.get_data(as_text=True)
            self.assertIn("Access unauthorized", html)
            