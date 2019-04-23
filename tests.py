import unittest
from datetime import datetime, timedelta
from hashlib import md5
from app import app, db
from app.models import User, Post


class UserModelCase(unittest.TestCase):
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_password_hashing(self):
        nayan = User(username='nayan')
        nayan.set_password('zaveri')
        self.assertTrue(nayan.check_password('zaveri'))
        self.assertFalse(nayan.check_password('Zaveri'))

    def test_avatar(self):
        nayan = User(username='nayan', email='nayan@crazyideas.co.in')
        digest = md5(nayan.email.encode('UTF-8')).hexdigest()
        size = 128
        nayan_avatar = f'http://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'
        self.assertEqual(nayan.avatar(size), nayan_avatar)

    def test_follow(self):
        # Create two users
        nayan = User(username='nayan', email='nayan@crazyideas.co.in')
        nisha = User(username='nisha', email='nisha@crazyideas.co.in')
        db.session.add(nayan)
        db.session.add(nisha)
        db.session.commit()

        # Test No Relationship
        self.assertEqual(nayan.followed.all(), [])
        self.assertEqual(nisha.followed.all(), [])

        # Test One Way Follow
        nayan.follow(nisha)
        db.session.commit()
        self.assertTrue(nayan.is_following(nisha))
        self.assertEqual(nayan.followed.count(), 1)
        self.assertEqual(nayan.followed.first().username, 'nisha')
        self.assertEqual(nayan.followers.count(), 0)
        self.assertFalse(nisha.is_following(nayan))
        self.assertEqual(nisha.followers.count(), 1)
        self.assertEqual(nisha.followers.first().username, 'nayan')
        self.assertEqual(nisha.followed.count(), 0)

        # Test Both Way Follow
        nisha.follow(nayan)
        db.session.commit()
        self.assertTrue(nisha.is_following(nayan))
        self.assertEqual(nayan.followers.count(), 1)
        self.assertEqual(nayan.followers.first().username, 'nisha')
        self.assertEqual(nisha.followed.count(), 1)
        self.assertEqual(nisha.followed.first().username, 'nayan')

        # Test Unfollow
        nayan.unfollow(nisha)
        nisha.unfollow(nayan)
        db.session.commit()
        self.assertFalse(nayan.is_following(nisha))
        self.assertEqual(nayan.followed.count(), 0)
        self.assertEqual(nayan.followers.count(), 0)
        self.assertFalse(nisha.is_following(nayan))
        self.assertEqual(nisha.followed.count(), 0)
        self.assertEqual(nisha.followers.count(), 0)

    def test_follow_post(self):
        # Create 4 users
        nayan = User(username='nayan', email='nayan@crazyideas.co.in')
        nisha = User(username='nisha', email='nisha@crazyideas.co.in')
        pranay = User(username='pranay', email='pranay@crazyideas.co.in')
        raj = User(username='raj', email='raj@crazyideas.co.in')
        db.session.add_all([nayan, nisha, pranay, raj])

        # Create 4 posts that are posted in the order of nisha, pranay, raj, nayan (with the most recent first)
        now = datetime.utcnow()
        nisha_post = Post(author=nisha, body='Post from nisha', timestamp=now + timedelta(seconds=4))
        pranay_post = Post(author=pranay, body='Post from pranay', timestamp=now + timedelta(seconds=3))
        raj_post = Post(author=raj, body='Post from raj', timestamp=now + timedelta(seconds=2))
        nayan_post = Post(author=nayan, body='Post from nayan', timestamp=now + timedelta(seconds=1))
        db.session.add_all([nayan_post, nisha_post, pranay_post, raj_post])
        db.session.commit()

        # Setup the followers
        nayan.follow(nisha)
        nayan.follow(raj)
        nisha.follow(pranay)
        pranay.follow(raj)
        db.session.commit()

        # Check the wall of all 4 users
        nayan_wall = nayan.followed_post().all()
        self.assertEqual(nayan_wall, [nisha_post, raj_post, nayan_post])
        nisha_wall = nisha.followed_post().all()
        self.assertEqual(nisha_wall, [nisha_post, pranay_post])
        pranay_wall = pranay.followed_post().all()
        self.assertEqual(pranay_wall, [pranay_post, raj_post])
        raj_wall = raj.followed_post().all()
        self.assertEqual(raj_wall, [raj_post])


if __name__ == '__main__':
    unittest.main(verbosity=0)
