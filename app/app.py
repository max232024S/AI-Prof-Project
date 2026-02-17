from fastapi import FastAPI, HTTPException, Depends, Header, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import uvicorn
import main as m
from schemas import AddSourcePost, ChatPost, RegisterPost, LoginPost, CoursePost
from database.database import db
from pwdlib import PasswordHash
from jose import jwt, JWTError
from datetime import datetime, timedelta
import os
SECRET_KEY = os.getenv("ENCODING_KEY")

app = FastAPI()
security = HTTPBearer()

# Initialize database on startup
db.construct_db() #construct schema
#db.user_setup() #hardcoded for test
#db.course_setup() #hardcoded for test


user_ids = []
documents = []

def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
    token = credentials.credentials

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload["user_id"]
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/register")
def register(p : RegisterPost):
    try:
        password_hash = PasswordHash.recommended()
        hashedPassword = password_hash.hash(p.password)
        db.create_user(p.first_name, p.last_name, p.email)
        db.storeHashedPassword(p.email, hashedPassword)
        return {"message": "User successfully registered", "email": p.email}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

        



@app.post("/login")
def login(p : LoginPost):
    try:
        #hashing and verification with db
        password_hash = PasswordHash.recommended()
        dbHashed = db.getHashedPassword(p.email) #get hashed password
        if not dbHashed:
            raise HTTPException(status_code=401, detail="Incorrect email or password")

        try:
            verified = password_hash.verify(p.password, dbHashed)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Password verification failed: {str(e)}")

        if not verified:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Incorrect username or password")
        user = db.get_user_by_email(p.email) #get user_id

        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        token = jwt.encode({
            "user_id" : user['user_id'],
            "exp" : datetime.utcnow() + timedelta(days=7) #lets token expire in 7 days
        },
        SECRET_KEY,
        algorithm="HS256") #encoding algorithm
        return {
            "access_token" : token,
            "token_type" : "bearer"
        } #this will be sent to client
    except HTTPException:
        raise
    except Exception as e:
        print(f"Login error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}") 







@app.post("/add-source")
def add_source(p: AddSourcePost, user_id : int = Depends(get_current_user_id)): #use depends to inject current user_id into endpoint
    try:
        # Verify the course belongs to the authenticated user
        course = db.get_course_by_id(p.course_id)
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        if course['user_id'] != user_id:
            raise HTTPException(status_code=403, detail="You don't have permission to add sources to this course")

        return m.add_source_api(p.course_id, p.file_path, p.source_type)
    except HTTPException:
        raise
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid value type")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Source not found")


@app.post("/chat")
def chat(p: ChatPost, user_id : int = Depends(get_current_user_id)):
    try:
        response =  m.chat_api(user_id, p.message, p.conversation_id)
        return response
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid value type")
    

@app.post("/add-course")
def add_course(p : CoursePost, user_id : int = Depends(get_current_user_id)):
        course_id = db.create_course(user_id, p.name, p.start_date, p.end_date, p.course_code) #None is edge case
        return {
            "Success" : True,
            "Message" : "Course successfully added",
            "course" : course_id
        }

def get_courses_from_current_user(user_id : int=Depends(get_current_user_id)):
    try:
        courses = db.get_course_from_user_id(user_id)
        return courses
    except Exception as e:
        print(f"Exception details: {str(e)}")
        raise HTTPException(status_code=404, detail="Course not found")


#lets also make get requests for documents and courses
@app.get("/get-documents")
def get_documents(course_id : int, user_id : int=Depends(get_current_user_id)):
    courses = get_courses_from_current_user(user_id)
    if not courses:
        raise HTTPException(status_code=404, detail="Course not found.")
    #find the desired course
    selectedCourse = None
    for course in courses:
        if course['course_id'] == course_id:
            selectedCourse = course
            break
    if not selectedCourse:
        raise HTTPException(status_code=404, detail="Course not found.")
    if selectedCourse['user_id'] != user_id:
            raise HTTPException(status_code=403, detail="You don't have permission to view this course's documents.")
    documents = db.get_course_documents(selectedCourse['course_id'])
    return documents

#also add get courses endpoint
@app.get('/get-courses')
def get_courses(user_id : int=Depends(get_current_user_id)):
    courses = db.get_course_from_user_id(user_id)
    if not courses:
        raise HTTPException(status_code=404, detail="No courses found.")
    return courses


#get conversations routing
@app.get('/get-conversations')
def get_conversations(user_id : int=Depends(get_current_user_id)):
    conversations = db.get_conversations(user_id) #list of dictionaries
    if not conversations:
        raise HTTPException(status_code=404, detail="No conversations found")
    return conversations

#get messages in conversations routing
@app.get('/get-messages-in-conversation')
def get_messages_in_conversation(conversation_id : int, user_id : int=Depends(get_current_user_id)):
    conversations = db.get_conversations(user_id)
    selectedConversation = None
    for conversation in conversations:
        if conversation['conversation_id'] == conversation_id:
            selectedConversation = conversation
            break
    if not selectedConversation:
        raise HTTPException(status_code=404, detail="Conversation does not exist.")
    if selectedConversation['user_id'] != user_id:
        raise HTTPException(status_code=403, detail="You don't have access to this conversation.")
    
    #we have now found selected conversation, next extract the messages
    messages = db.get_conversation_messages(selectedConversation['conversation_id'])
    if not messages:
        raise HTTPException(status_code=404, detail="No messages found in conversation.")
    return messages
    



if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8080, reload=True)