import sqlite3
import os
class db:
    def __init__():
        return
    def construct_db():
        conn = sqlite3.connect('ai_prof.db')
        cursor = conn.cursor()
        try:
            with conn:
                current_dir = os.path.dirname(os.path.abspath(__file__))
                schema_path = os.path.join(current_dir, 'schema.sql')
               
                with open(schema_path, 'r') as f:
                    sql_script = f.read()
                cursor.executescript(sql_script)
                return conn
        finally:
            conn.close()
    
    #hardcoded user setup for testing TEMPORARY
    def user_setup():
        conn = sqlite3.connect('ai_prof.db')
        cursor = conn.cursor()
        try:
            with conn:
                cursor.execute('''INSERT OR IGNORE INTO User (user_id, first_name,
                               last_name, email) VALUES (?, ?, ?, ?)''',
                               (1, "Max", "Brooks", "maxwellwbrooksgmail.com"))
        finally:
            conn.close()



    def course_setup(): #hardcoded course setup for testing
        conn = sqlite3.connect('ai_prof.db')
        cursor = conn.cursor()
        try:
            with conn:
                cursor.execute('''INSERT OR IGNORE INTO Course (course_id, user_id, name, start_date, end_date) VALUES (?, ?, ?, ?, ?)''',
                               (1, 1, "Physics 101", "2025-01-07 07:10:00", "2026-01-07 07:10:00"))
        finally:
            conn.close()

    


    
    
    def start_conversation(user_id):
        conn = sqlite3.connect('ai_prof.db')
        cursor = conn.cursor()
        try:
            with conn:
                cursor.execute('''INSERT INTO Conversation (user_id)
                            VALUES (?)
                            ''',
                            (user_id, ))
                cursor.execute('''SELECT conversation_id FROM Conversation
                               WHERE (user_id = ?)''',
                               (user_id, ))
                conversation_id_tuple = cursor.fetchone()
                return conversation_id_tuple[0]
        finally:
            conn.close()
    

    def save_message(conversation_id, message_role,  message_text): #saves most recent message into messages db
        conn = sqlite3.connect('ai_prof.db')
        cursor = conn.cursor()
        try:
            with conn: 
                cursor.execute("INSERT INTO Message (message_text, message_role, conversation_id) VALUES (?, ?, ?)",
                        (message_text, message_role, conversation_id))
        finally:
            conn.close()



    def load_memory(user_id):
        conn = sqlite3.connect('ai_prof.db')
        conn.row_factory = sqlite3.Row #allows dictionary access columns by col name
        cursor = conn.cursor()
        try:
            with conn:
                cursor.execute('''SELECT message_text, message_role FROM Message
                INNER JOIN Conversation ON Message.conversation_id = Conversation.conversation_id
                INNER JOIN User ON Conversation.user_id = User.user_id
                WHERE USER.user_id = ? 
                ORDER BY message_id DESC LIMIT 8 ''',
                (user_id,))
                mem = cursor.fetchall()
                mem = mem[::-1] #reverse to feed it the most recent queries/responses first
                
                return [dict(row) for row in mem]
        finally:
            conn.close()



    def create_document(course_id, document_name, source_type):
        conn = sqlite3.connect('ai_prof.db')
        cursor = conn.cursor()
        try:
            with conn:
                cursor.execute('''INSERT INTO Document (course_id, name, source_type) VALUES (?, ?, ?)''',
                               (course_id, document_name, source_type))        
                return cursor.lastrowid                    
        finally:
            conn.close()



    def save_chunk(document_id, chunks_list, document_name):
        conn = sqlite3.connect('ai_prof.db')
        cursor = conn.cursor()
        try:
            with conn:
                chunk_id_list = []
                for index,chunk in enumerate(chunks_list):
                    cursor.execute('''INSERT INTO Chunk (document_id, chunk_index, chunk_text, document_name)
                                VALUES (?, ?, ?, ?)''',
                                (document_id, index, chunk, document_name))
                    chunk_id_list.append(cursor.lastrowid)
                return chunk_id_list                     
        finally:
            conn.close()


    def save_embedding(chunk_id, embedding_vector):
        conn = sqlite3.connect('ai_prof.db')
        cursor = conn.cursor()
        try:
            with conn:
                cursor.execute('''INSERT INTO Embedding (chunk_id, vector) VALUES (?, ?)''',
                               (chunk_id, embedding_vector))
        finally:
            conn.close()

    def load_embeddings(user_id): #loads all embeddings for a given user
        conn = sqlite3.connect('ai_prof.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            with conn:
                cursor.execute('''SELECT Embedding.embedding_id, Embedding.chunk_id, Embedding.vector FROM Embedding
                               INNER JOIN Chunk ON Embedding.chunk_id = Chunk.chunk_id
                               INNER JOIN Document ON Chunk.document_id = Document.document_id
                               INNER JOIN Course ON Document.course_id = Course.course_id
                               WHERE (Course.user_id = ?)''',
                               (user_id,))
                embeddings = cursor.fetchall()
                return [dict(embedding) for embedding in embeddings]
        finally:
            cursor.close()
                               

    def load_similar_chunks(user_id, chunk_ids): #chunk_ids is list output from k_similar chunks
        conn = sqlite3.connect('ai_prof.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            with conn:
                
                placeholders = ", ".join(['?'] * len(chunk_ids))
                cursor.execute(f'''SELECT Chunk.chunk_id, Chunk.document_id, Chunk.chunk_index,
                                Chunk.chunk_text, Chunk.document_name FROM Chunk INNER JOIN Document
                                ON Chunk.document_id = Document.document_id
                                INNER JOIN Course ON Document.course_id = Course.course_id
                                WHERE (Course.user_id = ?)
                                AND Chunk.chunk_id IN ({placeholders})''',
                                [user_id] + list(chunk_ids))
                similar_chunks = cursor.fetchall()
                return [dict(similar_chunk) for similar_chunk in similar_chunks]
                    
        finally:
            conn.close()

    def clear_database():
        conn = sqlite3.connect('ai_prof.db')
        cursor = conn.cursor()
        # This deletes all current embeddings so you can start fresh
        cursor.execute("DELETE FROM Embedding")
        cursor.execute("DELETE FROM Course")
        cursor.execute("DELETE FROM Chunk")
        cursor.execute("DELETE FROM Document")
        cursor.execute("DELETE FROM Message")
        cursor.execute("DELETE FROM Conversation")
        conn.commit()
        conn.close()
        print("Database purged. Ready for fresh data.")

    # Authentication methods
    def create_user(first_name, last_name, email, password):
        """Create a new user account with password."""
        conn = sqlite3.connect('ai_prof.db')
        cursor = conn.cursor()
        try:
            with conn:
                cursor.execute('''INSERT INTO User (first_name, last_name, email, password)
                               VALUES (?, ?, ?, ?)''',
                               (first_name, last_name, email, password))
                return cursor.lastrowid
        finally:
            conn.close()

    def get_user_by_email(email):
        """Lookup user by email address."""
        conn = sqlite3.connect('ai_prof.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            with conn:
                cursor.execute('''SELECT user_id, first_name, last_name, email, password
                               FROM User WHERE email = ?''', (email,))
                user = cursor.fetchone()
                return dict(user) if user else None
        finally:
            conn.close()

    def verify_password(email, password):
        """Verify user password for login."""
        user = db.get_user_by_email(email)
        if not user or user['password'] is None:
            return False
        return user['password'] == password

    def create_token(user_id, token):
        """Generate and store new API token for user."""
        conn = sqlite3.connect('ai_prof.db')
        cursor = conn.cursor()
        try:
            with conn:
                cursor.execute('''INSERT INTO Token (user_id, token)
                               VALUES (?, ?)''',
                               (user_id, token))
                return cursor.lastrowid
        finally:
            conn.close()

    def get_user_by_token(token):
        """Validate token and return user information."""
        conn = sqlite3.connect('ai_prof.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            with conn:
                cursor.execute('''SELECT User.user_id, User.first_name, User.last_name, User.email
                               FROM User
                               INNER JOIN Token ON User.user_id = Token.user_id
                               WHERE Token.token = ?''', (token,))
                user = cursor.fetchone()
                return dict(user) if user else None
        finally:
            conn.close()

    def get_conversations(user_id):
        """List all conversations for a user with message counts."""
        conn = sqlite3.connect('ai_prof.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            with conn:
                cursor.execute('''SELECT
                                   Conversation.conversation_id,
                                   Conversation.conversation_time as created_at,
                                   COUNT(Message.message_id) as message_count
                               FROM Conversation
                               LEFT JOIN Message ON Conversation.conversation_id = Message.conversation_id
                               WHERE Conversation.user_id = ?
                               GROUP BY Conversation.conversation_id
                               ORDER BY Conversation.conversation_time DESC''',
                               (user_id,))
                conversations = cursor.fetchall()
                return [dict(conv) for conv in conversations]
        finally:
            conn.close()

    def get_conversation_messages(conversation_id):
        """Get all messages in a conversation."""
        conn = sqlite3.connect('ai_prof.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            with conn:
                cursor.execute('''SELECT
                                   message_id,
                                   message_role as role,
                                   message_text as content,
                                   conversation_id
                               FROM Message
                               WHERE conversation_id = ?
                               ORDER BY message_id ASC''',
                               (conversation_id,))
                messages = cursor.fetchall()
                return [dict(msg) for msg in messages]
        finally:
            conn.close()

    def get_user_documents(user_id):
        """List all uploaded documents for a user with chunk counts."""
        conn = sqlite3.connect('ai_prof.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            with conn:
                cursor.execute('''SELECT
                                   Document.document_id,
                                   Document.name,
                                   Document.source_type,
                                   Document.created_at as uploaded_at,
                                   COUNT(Chunk.chunk_id) as chunk_count
                               FROM Document
                               INNER JOIN Course ON Document.course_id = Course.course_id
                               LEFT JOIN Chunk ON Document.document_id = Chunk.document_id
                               WHERE Course.user_id = ?
                               GROUP BY Document.document_id
                               ORDER BY Document.created_at DESC''',
                               (user_id,))
                documents = cursor.fetchall()
                return [dict(doc) for doc in documents]
        finally:
            conn.close()

