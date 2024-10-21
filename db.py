import sqlite3

def init_db():
    '''이 함수는 데이터베이스를 생성하는데 사용된다. 사용자 정보와 게시판 글을 생성하는 데 사용된다.'''
    conn = sqlite3.connect('bamboo.db')
    c = conn.cursor()

    # 유저 테이블 생성
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 email TEXT UNIQUE,
                 password TEXT,
                 username TEXT)''')

    # 게시글 테이블 생성
    c.execute('''CREATE TABLE IF NOT EXISTS posts (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 username TEXT,
                 title TEXT,
                 content TEXT,
                 file_name TEXT,
                 file_data BLOB,
                 timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                 is_deleted BOOLEAN DEFAULT 0)''')  # 삭제 여부를 추가한 필드

    conn.commit()
    conn.close()
