import os
import requests
import json
import client
import prompts
from database.database import db
from langchain_text_splitters import RecursiveCharacterTextSplitter
import numpy as np
import pymupdf



# Database initialization moved to app.py startup
# db.construct_db() #construct schema
# db.user_setup() #hardcoded for test
# db.course_setup() #hardcoded for test

def chat_api(user_id, message, conversation_id=None):
    """
    API-friendly chat function that returns a dictionary instead of printing.

    Args:
        user_id: ID of the user
        message: User's chat message
        conversation_id: Optional existing conversation ID

    Returns:
        dict with 'response', 'conversation_id', and 'sources' keys
    """
    # Start new conversation if not provided
    if conversation_id is None:
        conversation_id = db.start_conversation(user_id)

    # Load conversation context BEFORE saving current message
    context = db.load_memory(user_id)

    # Save user message AFTER loading context
    db.save_message(conversation_id, "user", message)

    # Format previous conversation history
    if context:
        context_prompt = "PREVIOUS CONVERSATION:\n"
        for msg in context:
            role = "User" if msg['message_role'] == 'user' else "Assistant"
            context_prompt += f"{role}: {msg['message_text']}\n\n"
    else:
        context_prompt = ""

    # Embed user input and find similar chunks
    input_embedding_list = client.embed(message)
    input_embedding = input_embedding_list[0]
    all_embeddings = db.load_embeddings(user_id)
    similar_chunk_ids = k_similar_chunks(input_embedding, all_embeddings, 3)
    similar_chunks = db.load_similar_chunks(user_id, similar_chunk_ids)

    # Format similar chunks with document names
    if similar_chunks:
        similar_chunk_string = "\n\nRELEVANT COURSE MATERIAL:\n"
        for chunk in similar_chunks:
            similar_chunk_string += f"[From {chunk['document_name']}]\n{chunk['chunk_text']}\n\n"
    else:
        similar_chunk_string = ""

    # Build prompt: context + chunks + current question
    prompt = f"{context_prompt}{similar_chunk_string}CURRENT QUESTION:\n{message}"
    response = client.run("chat", prompt)

    # Save system response
    db.save_message(conversation_id, "system", response)

    # Extract source document names
    sources = list(set([chunk['document_name'] for chunk in similar_chunks]))

    return {
        'response': response,
        'conversation_id': conversation_id,
        'sources': sources,
        'similar_chunks' : similar_chunk_string,
        'context' : context_prompt
    }


def chat():
    """CLI chat function (original behavior preserved)."""
    conversation_id = db.start_conversation(1)
    while True:
        user_input = input("Chat here: \n ")
        if user_input.lower() == "exit":
            print("Have a nice day. \n")
            break

        result = chat_api(1, user_input, conversation_id)
        conversation_id = result['conversation_id']
        print(result['response'])



def add_source_api(course_id, file_path, source_type='syllabus'):
    """
    API-friendly function to add a PDF source document.

    Args:
        user_id: ID of the user (used to get course_id)
        file_path: Path to the PDF file
        source_type: Type of document (default: 'syllabus')

    Returns:
        dict with 'success', 'message', 'document_id', and 'filename' keys

    Raises:
        ValueError: If file is not a PDF or doesn't exist
        TypeError: If file_path is not a string
    """
    if file_path is None:
        raise ValueError("Must enter source file")

    if not isinstance(file_path, str):
        raise TypeError("File not in string format")

    if not file_path.strip(' ').endswith('.pdf'):
        raise ValueError("Must be pdf file")

    # Create document (hardcoded course_id=1 for MVP)
    document_id = db.create_document(course_id, file_path, source_type)

    # Extract text from PDF
    raw_text = pdf_to_txt(file_path)

    # Chunk the text
    chunks = chunk_text(raw_text)

    # Save chunks and embeddings
    chunk_id_list = db.save_chunk(document_id, chunks, file_path)
    embeddings = client.embed(chunks)

    for embedding, chunk_id in zip(embeddings, chunk_id_list):
        np_embedding = np.array(embedding).astype(np.float32)
        vector_blob = np_embedding.tobytes()
        db.save_embedding(chunk_id, vector_blob)

    # Extract just the filename
    filename = os.path.basename(file_path)

    return {
        'success': True,
        'message': 'File uploaded successfully',
        'document_id': document_id,
        'filename': filename
    }


def add_source(source):
    """CLI function to add source (original behavior preserved)."""
    print(type(source))
    result = add_source_api(1, source, 'syllabus')
    print(result['message'])



def k_similar_chunks(input_vector, embeddings, k): #embeddings is taken in from load embeddings
    chunk_ids = {} #chunkid -> similarity score with inputted vector
    query_vector = np.array(input_vector).flatten().astype(np.float32) #shift down to one dimension and cast as float 32 (standard float)
    query_mag = np.linalg.norm(query_vector)
    for embedding in embeddings:
        vector = embedding['vector']
        vector = np.frombuffer(buffer=vector, dtype=np.float32) #convert back to float

        dot = np.dot(query_vector, vector)


        mag2 = np.linalg.norm(vector)

        similarity = (dot) / (query_mag * mag2)
        
        chunk_ids[embedding['chunk_id']] = similarity
        
        
    sorted_scores = sorted(chunk_ids.items(), key=lambda score: score[1]) #sort by values(scores) in ascending
    sorted_id_dict = dict(sorted_scores)
    similar_ids = list(sorted_id_dict.keys())
    
    return similar_ids[:-k-1:-1] #return most to least similar in top k similar chunks



def pdf_to_txt(pdf_file):
    #first handle OCR text extraction
    #determine if page is filled with an image
    #convert to OCR  TextPage object
    #extract plaintext

    #we also need to handle table text extraction


    document = pymupdf.open(pdf_file)
    full_text = ""
    for page in document:
        
        tabs = page.find_tables() #locate any tables and extrac them
        if tabs.tables:
            for table in tabs.tables:
                full_text += table.to_markdown() + "\n\n"
        
        
        raw_text = page.get_text()
        clean_text = raw_text.replace("\u200b", "").replace("\n\n", "\n").strip()

        if (len(clean_text.strip()) < 10) and len(page.get_images()) > 0: #barely any raw text on given page
            #OCR condition
            full_text += page.get_text("text", ocr=True) + "\n "
        else:
            full_text += clean_text + "\n "

    return full_text

    


def chunk_text(text_string): #takes in document and returns list of chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=650,
        chunk_overlap=100,
        length_function=len,
        is_separator_regex=False,
    )
    chunks = text_splitter.split_text(text_string)
    chunks = list(chunks)
    return chunks


    






def quiz_api(user_id, prompt, num_questions=5):
    """
    API-friendly quiz generation function.

    Args:
        user_id: ID of the user (for future use)
        prompt: Quiz generation prompt
        num_questions: Number of questions to generate (default: 5)

    Returns:
        dict with 'questions' key containing list of question dicts
    """
    # Generate quiz using LLM
    raw = client.run("quiz", prompt)
    data = json.loads(raw)

    # Return structured quiz data
    return {
        'questions': data['questions']
    }


def quiz(prompt):
    """CLI quiz function (original behavior preserved)."""
    result = quiz_api(1, prompt)
    data = result

    count = 0
    numCorrect = 0
    for question in data["questions"]:
        choices = question["choices"]
        joined = " ".join(choices)
        answer = input(question["question"] + "\n" + joined + "\n")
        correct = question["answer"]
        if answer not in question["choices"]:
            print("Invalid Guess.\n")
            continue
        if answer != correct:
            print(f"Incorrect, the answer was {correct} \n")
        else:
            print("Correct!\n")
            numCorrect += 1
        count += 1
        length = len(data["questions"])
        if (count == length):
            percent = (numCorrect / count) * 100
            print(f"Score: {percent:.1f}%\n")








#flashcards("generate me five flashcards about math")
#quiz("Generate a three question quiz on math")


#add_source('data/syllabus.txt')
#add_source('data/lecture_notes.txt')

#add_source('data/Langan.pdf')

#db.clear_database()
#add_source('data/Max Brooks Resume 2025 CS.pdf')
#add_source('data/Lecture10_Lasso.pdf')
#add_source('data/STAT 4105 Homework 3 (1).pdf')

if __name__ == "__main__":
    add_source('data/Langan.pdf')
    chat()
