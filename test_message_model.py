import os
from unittest import TestCase

from models import User, Message, Follows, db

os.environ['DATABASE_URI'] = 'postgresql:///warbler-test'

from app import app

db.create_all()

class MessageModelTestCase(TestCase):
    """Test views for messages"""
    
    def setUp(self):
        """Create test client, add sample data."""
        
        User.query.delete()
        Message.query.delete()
        Follows.query.delete()
        
        self.client = app.test_client()
        
    def test_message_model(self):
        """Does basic model work?"""
        
        u = User.signup('testuser', 'test@test.com', 'test123', '')
        db.session.commit()
        
        m = Message(
            text="""Hello hello hello
            """
            )
        
        try:
            u.messages.append(m)
            db.session.commit()
        except:
            self.assertIsNone(m.id)
            
        self.assertIsNotNone(m.id)
        self.assertEqual(len(u.messages), 1)
        
        m = Message(
            text="""
            Lorem ipsum dolor sit amet consectetur adipisicing elit. 
            Quibusdam, sed odio. Laudantium, commodi? Dicta saepe 
            accusantium ratione necessitatibus quaerat molestiae non 
            exercitationem repellendus nemo? Vitae, sit consequatur!
            Quis, qui iure! Lorem ipsum, dolor sit amet consectetur 
            adipisicing elit. Reprehenderit, obcaecati inventore
            illum unde accusantium non porro omnis quidem 
            temporibus labore? Ut officia commodi obcaecati rem 
            distinctio id quas maiores veniam! Yeehaw"""
        )
        
        try:
            u.messages.append(m)
            db.session.commit()
        except:
            db.session.rollback()
            self.assertIsNone(m.id)
            
        self.assertEqual(len(u.messages), 1)
        
    