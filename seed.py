from models import *
from app import app

# Create all tables
db.drop_all()
db.create_all()

# If table isn't empty, empty it
User.query.delete()
Feedback.query.delete()



# Seed users
first = User(username = 'first',
             password = 'first',
             email = 'first@gmail.com',
             first_name = 'first',
             last_name = 'name')


second = User(username = 'second',
             password = 'second',
             email = 'second@gmail.com',
             first_name = 'second',
             last_name = 'name')


third = User(username = 'third',
             password = 'third',
             email = 'third@gmail.com',
             first_name = 'third',
             last_name = 'name')


db.session.add_all([first, second, third])
db.session.commit()


# Seed user feedback
feedback1 = Feedback(
             title = 'First Post',
             content = 'I am the first post',
             username = 'first' )


feedback2 = Feedback(
             title = 'Second Post',
             content = 'I am the second post',
             username = 'second' )


feedback3 = Feedback(
             title = 'Third Post',
             content = 'I am the third post',
             username = 'third' )


db.session.add_all([feedback1, feedback2, feedback3])
db.session.commit()