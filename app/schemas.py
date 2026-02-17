from pydantic import BaseModel
from fastapi import Depends
from datetime import date
from typing import Optional
class AddSourcePost(BaseModel):
    file_path : str
    source_type : str
    course_id : int

class ChatPost(BaseModel):
    message : str
    conversation_id : Optional[int] = None

class RegisterPost(BaseModel):
    first_name : str
    last_name : str
    email : str #later we will ensure this is valid email format
    password : str

class LoginPost(BaseModel):
    email : str
    password : str

class CoursePost(BaseModel):
    name : str
    start_date : Optional[date]
    end_date : Optional[date]
    course_code : str