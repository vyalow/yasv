yasv — Yet Another Simple Validator
===================================

yasv is a simple python library for data validation.

Why yasv?
---------

* it has simple schema definition syntax similar to django or SQLAlchemy models;
* Python 2.7, 3.0 support;
* simple and minimalistic, no html form overhead;

Installation
------------

Just ::

    pip install yasv

QuickStart
----------

For example we have a scheme with couple of fields. ::

    from yasv import Schema, Field, is_in, required


    class UserSchema(Schema):
        name = Field('Name', required)
        sex = Field('Sex', is_in(['male', 'female']))


Then we create instance of User() and set one parameter 'name'. ::

    user = User(name='George')

Now we can validate user's data: ::

    s = UserSchema(user)
    s.is_valid()

Here is_valid() returns True because user has required field 'name'. There isn't
field 'sex' but it's optional.
