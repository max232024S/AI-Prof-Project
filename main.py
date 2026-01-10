import os
import requests
import json
import client
import prompts
from database.database import db
from langchain_text_splitters import RecursiveCharacterTextSplitter
import numpy as np
import pymupdf



db.construct_db() #construct schema
db.user_setup() #hardcoded for test
db.course_setup() #hardcoded for test

def chat():
    

    conversation_id = db.start_conversation(1)
    while True:
        user_input = input("Chat here: \n ")
        if user_input.lower() == "exit":
            print("Have a nice day. \n")
            break

        db.save_message(conversation_id, "user", user_input)
        context = db.load_memory(1) #hard coded user id
        
        context_prompt = ""
        for message in context:
            role = message['message_role']
            content = message['message_text']
            context_prompt += role + ": " + content + " \n -- SOURCE MESSAGE -- \n "

            


        input_embedding_list = client.embed(user_input) #embed user input
        input_embedding = input_embedding_list[0]
        all_embeddings = db.load_embeddings(1) #load db embeddings for hardcoded user id
        similar_chunk_ids = k_similar_chunks(input_embedding, all_embeddings, 3)
        similar_chunks = db.load_similar_chunks(1, similar_chunk_ids)
        # IMPORTANT -> for document name citing also load in and format chunk['document_name'] and add to string
        similar_chunk_string = "\n\n--- SOURCE CHUNK ---\n ".join([f"Document: {chunk['document_name']} Chunk: {chunk['chunk_text']}" for chunk in similar_chunks])
        #print(f"DEBUG: {similar_chunk_string}")

        prompt = context_prompt + similar_chunk_string
        

        response = client.run("chat", prompt)
        db.save_message(conversation_id, "system", response)
        print(response)



def add_source(source):
    print(type(source))
    if source is None:
        raise ValueError("Must enter source file")
    
    if not isinstance(source, str):
        raise TypeError("File not in string format") #checks if source file is a string
    
    if not source.strip(' ').endswith('.pdf'): #checks if file is pdf
        raise ValueError("Must be pdf file")

    document_id = db.create_document(1, source, 'syllabus')
    raw_text = pdf_to_txt(source)
    
    chunks = chunk_text(raw_text)

    chunk_id_list = db.save_chunk(document_id, chunks, source) #save chunk ids to db
    embeddings = client.embed(chunks) #embed all chunks in source
    for embedding,chunk_id in zip(embeddings, chunk_id_list):
        np_embedding = np.array(embedding).astype(np.float32)
        vector_blob = np_embedding.tobytes()
        db.save_embedding(chunk_id, vector_blob)
    print("Source successfully added!")



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
    document = pymupdf.open(pdf_file)
    full_text = ""
    for page in document:
        raw_text = page.get_text()
        clean_text = raw_text.replace("\u200b", "").replace("\n\n", "\n").strip()
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


    






def quiz(prompt): #temporary functional quiz feature
    raw = client.run("quiz", prompt)
    data = json.loads(raw)
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
            percent = numCorrect // count
            print("Score: " + percent + "%\n")








#flashcards("generate me five flashcards about math")
#quiz("Generate a three question quiz on math")


#add_source('data/syllabus.txt')
#add_source('data/lecture_notes.txt')

#add_source('data/Langan.pdf')

#db.clear_database()
#add_source('data/Max Brooks Resume 2025 CS.pdf')
#add_source('data/Lecture10_Lasso.pdf')
add_source('data/STAT 4105 Homework 3 (1).pdf')
chat()

