import streamlit as st
import sqlite3

def load_chat_history(username, other_user):
    '''이 함수는 채팅 내역을 데이터베이스에서 불러온다. 불러온 내역을 return 한다.'''
    conn = sqlite3.connect('bamboo.db')
    c = conn.cursor()
    # 유저 대화 내역을 현재 유저가 포함되었는지 여부로 판단하여 데이터를 데이터베이스에서 가져온다.
    c.execute("SELECT sender, message, timestamp FROM chat_history WHERE (user1 = ? AND user2 = ?) OR (user1 = ? AND user2 = ?) ORDER BY timestamp",
              (username, other_user, other_user, username))
    chat_history = c.fetchall()
    conn.close()
    return chat_history if chat_history else []

def save_chat_history(username, other_user, sender, message):
    '''이 함수는 채팅 내역을 데이터베이스에 저장한다.'''
    conn = sqlite3.connect('bamboo.db')
    c = conn.cursor()
    # 현재 유저, 상대 유저, 내역을 업로드한다.
    c.execute("INSERT INTO chat_history (user1, user2, sender, message) VALUES (?, ?, ?, ?)",
              (username, other_user, sender, message))
    conn.commit()
    conn.close()

def BAMBOO_chat():
    '''이 함수는 채팅을 할 상대 사용자를 추가하고, 데이터베이스에서 채팅 정보를 불러오거나 저장한 값을 유져에게 보여주는 역할을 한다.'''
    st.header(f'Chat! {st.session_state.username}')
    if 'chat_users' not in st.session_state:
        st.session_state['chat_users'] = []

    if 'current_user' not in st.session_state:
        st.session_state['current_user'] = None
    user_radio_container = st.container()
    with user_radio_container:
        # 라디오박스 가로로 배치
        st.write('<style>.st-c2{background-color: #f0f2f6; padding: 10px; border-radius: 10px;}</style>',
                 unsafe_allow_html=True)
        selected_user = st.radio("채팅을 시작할 유저를 선택하세요", st.session_state['chat_users'])

        if selected_user != st.session_state['current_user']:
            st.session_state['current_user'] = selected_user

    chat_container = st.empty()

    new_user_container = st.container()
    with new_user_container:
        st.write('<style>.st-c3{background-color: #f0f2f6; padding: 10px; border-radius: 10px;}</style>',
                 unsafe_allow_html=True)
        new_user = st.text_input("채팅할 사용자를 추가하세요:")
        if st.button("사용자 추가"):
            if new_user and new_user not in st.session_state['chat_users']:
                st.session_state['chat_users'].append(new_user)
    st.divider()

    if 'current_user' not in st.session_state or not st.session_state['current_user']:
        chat_container.error("채팅할 사용자를 추가하세요")

    other_user = st.session_state['current_user']
    if prompt := st.chat_input("메시지 입력"):
        with st.chat_message(st.session_state.username):
            save_chat_history(st.session_state.username, st.session_state['current_user'], st.session_state.username, prompt)

    chat_history = load_chat_history(st.session_state.username, other_user)

    chat_container = st.container()
    with chat_container:
        for role, message, timestamp in chat_history:
            with st.chat_message(role):
                st.markdown(f"{message} - {timestamp}")

    st.markdown( #이 문법은 스트림릿에서 직접 css를 조작하는 방법으로, 조금 더 이쁜 모양의 인터페이스를 만들 수 있습니다.
        """
        <style>
        .css-1v3fvcr {
            display: flex;
            flex-direction: column;
            height: 100vh;
            justify-content: flex-start;
        }
        .css-1v3fvcr > div:nth-child(1) {
            flex: 0 0 auto;
        }
        .css-1v3fvcr > div:nth-child(2) {
            flex: 1 1 auto;
            overflow: auto;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
