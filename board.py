import streamlit as st
import sqlite3
import datetime
from cleanengine import nametest

def board():
    '''이 함수는 데이터베이스에서 게시물 파일을 불러와 시간 순서대로 이를 보여주거나 내가 입력한 게시물을 업로드하는 역할을 한다.'''
    st.header('게시판')
    if 'title' not in st.session_state:
        st.session_state.title = ''
    if 'content' not in st.session_state:
        st.session_state.content = ''
    if 'file' not in st.session_state:
        st.session_state.file = None
    # 게시글 작성
    if st.session_state.get('logged_in'):
        st.subheader('새 게시글 작성')

        with st.form("post_form"):
            st.session_state.title = st.text_input("제목을 입력하세요:", value=st.session_state.title)
            st.session_state.content = st.text_area("내용을 입력하세요:", value=st.session_state.content)
            st.session_state.file = st.file_uploader("파일을 업로드하세요:",
                                                     type=["jpg", "jpeg", "png", "pdf", "docx", "xlsx", "hwp", "hwpx",
                                                           "cap"])
            submit_button = st.form_submit_button("게시")

        if submit_button:
            if st.session_state.title and st.session_state.content:
                if nametest(st.session_state.title) or nametest(st.session_state.content):
                    st.error("cleanengine에 의하여 게시가 제한되었습니다. 타인을 비난 및 비방하는 글은 삼가주시기 바랍니다.")
                else:
                    conn = sqlite3.connect('bamboo.db')
                    c = conn.cursor()
                    file_data = st.session_state.file.read() if st.session_state.file else None
                    file_name = st.session_state.file.name if st.session_state.file else None
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    name = st.session_state.username

                    post_data = {
                        "username": name,
                        "title": st.session_state.title,
                        "content": st.session_state.content,
                        "file_name": file_name,
                        "file_data": file_data,
                        "timestamp": timestamp,
                        "is_deleted": False  # 삭제 여부를 위한 필드 추가
                    }
                    # 게시글 업로드 시 데이터베이스에 업로드 코드
                    c.execute(
                        "INSERT INTO posts (username, title, content, file_name, file_data, timestamp, is_deleted) VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (post_data["username"], post_data["title"], post_data["content"], post_data["file_name"],
                         post_data["file_data"], post_data["timestamp"], post_data["is_deleted"]))
                    conn.commit()
                    conn.close()

                    # 성공 후 입력 값을 초기화
                    st.session_state.title = ''
                    st.session_state.content = ''
                    st.session_state.file = None

                    st.success("게시글이 성공적으로 게시되었습니다.")
            else:
                st.error("제목과 내용을 입력하세요.")

    # 게시글 목록
    st.subheader('게시글 목록')

    conn = sqlite3.connect('bamboo.db')
    c = conn.cursor()
    # 게시글 목록 불러오는 코드
    c.execute(
        "SELECT rowid, username, title, content, file_name, file_data, timestamp, is_deleted FROM posts ORDER BY timestamp DESC")
    posts = c.fetchall()
    conn.close()

    post_list = []
    for post in posts:
        post_data = {
            "rowid": post[0],
            "username": post[1],
            "title": post[2],
            "content": post[3],
            "file_name": post[4],
            "file_data": post[5],
            "timestamp": post[6],
            "is_deleted": post[7]
        }
        post_list.append(post_data)

    current_user = st.session_state.get('username')

    # 삭제 확인용 상태 변수 생성
    if 'delete_post_id' not in st.session_state:
        st.session_state['delete_post_id'] = None

    for post_data in post_list:
        st.write(f"### {post_data['title']}")
        st.write(f"작성자: {post_data['username']}")
        st.write(f"작성 시간: {post_data['timestamp']}")

        # 게시글이 삭제되었는지 확인
        if post_data['is_deleted']:
            st.write("삭제된 글입니다.")
        else:
            # 작성자 본인이면 삭제 버튼 제공
            if post_data['username'] == current_user:
                st.write(post_data['content'])

                # 삭제 버튼 추가
                if st.session_state['delete_post_id'] is None:
                    if st.button(f"{post_data['rowid']}번 글 삭제", key=f"delete_button_{post_data['rowid']}"):
                        st.session_state['delete_post_id'] = post_data['rowid']
                        st.rerun()

                if st.session_state['delete_post_id'] == post_data['rowid']:
                    st.warning("이 글을 삭제하시겠습니까?", icon="⚠️")

                    if st.button("예, 삭제합니다", key=f"confirm_delete_{post_data['rowid']}"):
                        # 삭제 로직 수행
                        conn = sqlite3.connect('bamboo.db')
                        c = conn.cursor()
                        c.execute("UPDATE posts SET is_deleted = ? WHERE rowid = ?", (True, post_data['rowid']))
                        conn.commit()
                        conn.close()
                        st.success("게시글이 삭제되었습니다.")
                        st.session_state['delete_post_id'] = None
                        st.rerun()  # 화면 새로고침
                    elif st.button("취소", key=f"cancel_delete_{post_data['rowid']}"):
                        st.session_state['delete_post_id'] = None
                        st.rerun()

        # 파일이 있는 경우 파일 유지
        if post_data['file_name'] and post_data['file_data'] and not post_data['is_deleted']:
            if post_data['file_name'].lower().endswith(('jpg', 'jpeg', 'png')):
                st.image(post_data['file_data'], use_column_width=True)
            else:
                st.download_button(label=f"{post_data['file_name']} 다운로드", data=post_data['file_data'],
                                   file_name=post_data['file_name'])

        st.divider()
