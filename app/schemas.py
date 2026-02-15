from pydantic import BaseModel
from fastapi import Depends
from datetime import date
class AddSourcePost(BaseModel):
    file_path : str
    source_type : str

class ChatPost(BaseModel):
    message : str
    conversation_id : int = None

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
    start_date : date
    end_date : date
    course_code : str