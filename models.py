from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, user_id, email, social_id, first_name, last_name, gender, location, age_range, likes, picture):
        self.id         = user_id
        self.email      = email
        self.social_id  = social_id
        self.first_name = first_name
        self.last_name  = last_name
        self.gender     = gender
        self.location   = location
        self.age_range  = age_range
        self.likes      = likes 
        self.picture    = picture

#    social_id: a string that defines a unique identifier from the third party authentication service used to login.
#    nickname: a nickname for the user. Must be defined for all users, and does not need to be unique.
#    email: the email address of the user. This column is optional.
