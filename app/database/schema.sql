CREATE TABLE IF NOT EXISTS User (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT,
    email TEXT UNIQUE NOT NULL,
    password TEXT,
    hashed_password TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Conversation(
    conversation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    conversation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES User (user_id)

);

CREATE TABLE IF NOT EXISTS Message(
    message_id INTEGER PRIMARY KEY AUTOINCREMENT,
    message_text TEXT NOT NULL,
    conversation_id INTEGER NOT NULL,
    message_role TEXT NOT NULL CHECK (message_role IN ('system', 'user')),
    FOREIGN KEY (conversation_id) REFERENCES Conversation (conversation_id)



);

CREATE TABLE IF NOT EXISTS Course (
    course_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    course_code TEXT,
    FOREIGN KEY (user_id) REFERENCES User (user_id)
);

CREATE TABLE IF NOT EXISTS Document (
    document_id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    media_folder_path TEXT,
    source_type TEXT NOT NULL
        CHECK (source_type IN ('syllabus', 'lecture_notes', 'student_notes', 'textbook', 'video')),
    presentation_sytle TEXT CHECK (presentation_sytle IN ('slides', 'board', 'mixed')) DEFAULT 'slides',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (course_id) REFERENCES Course (course_id)
);

CREATE TABLE IF NOT EXISTS Chunk (
    chunk_id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL,
    document_name TEXT,
    chunk_index INTEGER NOT NULL,
    chunk_text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    start_time REAL,
    end_time REAL,
    FOREIGN KEY (document_id) REFERENCES Document (document_id)
);
CREATE TABLE IF NOT EXISTS Embedding (
    embedding_id INTEGER PRIMARY KEY AUTOINCREMENT,
    chunk_id INTEGER NOT NULL,
    vector BLOB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (chunk_id) REFERENCES Chunk (chunk_id)
);


