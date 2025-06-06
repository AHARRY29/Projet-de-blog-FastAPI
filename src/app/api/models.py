from typing import Union, Optional
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, constr, HttpUrl

# create a "Pydantic Model" of the data we want to maintain in the database
# by inheriting from BaseModel. This inherits data parsing and validation 
# such that fields of the model are guaranteed to be these types when filled 
# with payloads for creating and updating things.

# here is a "note": something with a title, a description, and data 
class NoteSchema(BaseModel):
    title: str = Field(..., min_length=3, max_length=50)
    description: str = Field(..., min_length=3, max_length=50)
    data: str

# A "Note" in the database is simply an id plus our NoteSchema: 
class NoteDB(NoteSchema):
    id: int
    owner: int



# basic "blog post":
class BlogPostSchema(BaseModel):
    title: str = Field(..., min_length=3, max_length=80)
    description: str = Field(..., min_length=3, max_length=16384)
    tags: str = Field(..., min_length=3, max_length=80)

# A "BlogPost" in the database is simply an id plus our BlogPostSchema: 
class BlogPostDB(BlogPostSchema):
    id: int
    owner: int



# an access token used by authentication
class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str
    
# a user 
class User(BaseModel):
    username: str
    email: EmailStr
    roles: str
    commission_balance: float = 0.0
    last_login_at: Optional[datetime] = None
    # disabled: Union[bool, None] = None
    # email: Union[EmailStr, None] = None
    # roles: Union[str, None] = None

    
# a user in the dabase
class UserInDB(User):
    id: int
    verify_code: str
    hashed_password: str

# info for user registration
class UserReg(BaseModel):
    username: str
    password: constr(min_length=12)
    email: EmailStr
    # email: Union[EmailStr, None] = None
    
# info returned from a user query
class UserPublic(BaseModel):
    username: str
    id: int
    roles: str
    email: EmailStr
    # roles: Union[str, None] = None
    # email: Union[EmailStr, None] = None
    
 
# a user sending just a string:
class basicTextPayload(BaseModel):
    text: str
    
    
# info posted by a user as a Contact the website email message:
class ContactMsg(BaseModel):
    subject: str
    msg: str