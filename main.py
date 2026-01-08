import os
import requests
import json
import client
import prompts
from database.database import db
from langchain_text_splitters import RecursiveCharacterTextSplitter
import numpy as np


db.construct_db() #construct schema
db.user_setup() #hardcoded for test
db.course_setup() #hardcoded for test
#cursor = connect.cursor() #activate cursor to modify SQL tables in main

def chat():
    

    conversation_id = db.start_conversation(1)
    while True:
        user_input = input("Chat here: \n ")
        if user_input.lower() == "exit":
            print("Have a nice day. \n")
            break

        db.save_message(conversation_id, "user", user_input)
        context = db.load_memory(1) #hard coded user id
        context_string = "\n\n--- SOURCE MESSAGE ---\n".join([message['message_text'] for message in context])
        system_context = str(context) #primitive, change later and parse through commas brackets
        input_embedding_list = client.embed(user_input) #embed user input
        input_embedding = input_embedding_list[0]
        all_embeddings = db.load_embeddings(1) #load db embeddings for hardcoded user id
        similar_chunk_ids = k_similar_chunks(input_embedding, all_embeddings, 7)
        similar_chunks = db.load_similar_chunks(1, similar_chunk_ids)
        similar_chunk_string = "\n\n--- SOURCE CHUNK ---\n".join([chunk['chunk_text'] for chunk in similar_chunks])

        prompt = context_string + similar_chunk_string
        

        response = client.run("chat", prompt)
        db.save_message(conversation_id, "system", response)
        print(response)



def add_source(source):
    document_id = db.create_document(1, source, 'syllabus')
    chunks = chunk_text(source)
    print(f"Type of first chunk is {type(chunks[0])}")
    chunk_id_list = db.save_chunk(document_id, chunks)
    embeddings = client.embed(chunks)
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




def chunk_text(file): #takes in document and returns list of chunks
    with open(file) as f:
        unchunked = f.read()
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=100,
        chunk_overlap=20,
        length_function=len,
        is_separator_regex=False,
    )
    chunks = text_splitter.split_text(unchunked)
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

#chat()
add_source('data/syllabus.txt')
add_source('data/lecture_notes.txt')
chat()

