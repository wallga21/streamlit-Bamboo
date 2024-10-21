import streamlit as st
from streamlit_option_menu import option_menu
import sqlite3
from db import init_db
from auth import login, sign_in, my_id, show_privacy_policy
from board import board
from chat import BAMBOO_chat

def show_about_app():
    '''이 함수는 가장 먼져 나타나는 화면이며, 이 서비스를 소개하는 역할을 합니다.'''
    st.header("BAMBOO에 오신 것을 환영합니다!")
    st.write("""
        ## [앱 소개]
        BAMBOO는 모든 대곽인들을 위한 의견 교환의 장이며, 표현의 자유를 중시하는 곳입니다.
        """)



def show_sidebar():
    '''이 함수는 여러 페이지를 탐색하기 위한 탭이며, 사용자가 로그인되어있는지 아닌지를 판단하여 그에 맞는 페이지를 불러옵니다.'''
    with st.sidebar:
        if 'username' in st.session_state:
            username = st.session_state.username
        else:
            username = 'Anonymous'
        choice = option_menu(username, ['Welcome', "내 정보/로그인", '회원가입', "게시판",  "약관 및 개인정보 활용방침"],
                             icons=['bi bi-house-door', 'bi bi-person', 'bi bi-check-square', 'bi bi-file-text', 'bi bi-info-circle'], key="kind_of_motion",
                             menu_icon="bi bi-person-circle", default_index=0,
                             styles={
                                 "container": {"padding": "4!important", "background-color": "#fafafa"},
                                 "icon": {"color": "black", "font-size": "25px"},
                                 "nav-link": {"font-size": "16px", "text-align": "left", "margin": "0px", "--hover-color": "#fafafa"},
                                 "nav-link-selected": {"background-color": "#08c7b4"},
                             }
                             )

    if st.session_state["kind_of_motion"] == "Welcome":
        show_about_app()
    elif st.session_state["kind_of_motion"] == "내 정보/로그인":
        if 'logged_in' in st.session_state and st.session_state.logged_in:
            my_id()
        else:
            login()
    elif st.session_state["kind_of_motion"] == "회원가입":
        if 'logged_in' in st.session_state and st.session_state.logged_in:
            st.error('이미 로그인되어 있습니다.')
        else:
            sign_in()

    elif st.session_state["kind_of_motion"] == "게시판":
        if 'logged_in' in st.session_state and st.session_state.logged_in:
            board()
        else:
            st.error("게시판을 이용하려면 로그인이 필요합니다.")
    elif st.session_state["kind_of_motion"] == "약관 및 개인정보 활용방침":
        show_privacy_policy()
    else:
        show_about_app()
html = """
<head>
  <meta charset="UTF-9">
  <meta name="description" content="Bamboo">
  <meta name="keywords" content="DSHS, 대곽,Bamboo,밤부">
  <meta name="author" content="STATIC">
    <title>Bamboo</title>
</head> 
"""
st.markdown(html, unsafe_allow_html=True)
init_db()
show_sidebar()
