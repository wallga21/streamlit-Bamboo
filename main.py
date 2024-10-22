import streamlit as st
from streamlit_option_menu import option_menu
import sqlite3
from db import init_db
from auth import login, sign_in, my_id, show_privacy_policy
from board import board
from chat import BAMBOO_chat
st.set_page_config(
        page_title="Bamboo",
        page_icon="🎋",
        layout="wide",
        initial_sidebar_state="expanded"
    )
def show_about_app():
    # 페이지 설정
    

    

    # 페이지 제목 및 소개 문구
    

    # 페이지 제목 및 소개 문구
    st.title("환영합니다! 함께하는 지속 가능한 미래를 위한 커뮤니티")

    st.write(
        """
        우리 커뮤니티는 **지속 가능한 발전과 평화로운 공존**을 목표로 하는 글로벌 플랫폼입니다.  
        **비난과 비방은 없습니다.** 오직 존중과 협력으로 가득한 공간에서, 우리는 서로를 격려하며 성장해 나갑니다.
        """
    )

    st.markdown("### 🛡️ 이 커뮤니티는 익명성을 보장합니다.")
    st.write(
        """
        우리 커뮤니티는 **익명성을 보장**하여, 누구나 자신의 생각을 자유롭게 표현할 수 있는 공간을 제공합니다.  
        여러분은 개인적인 고민, 의견, 아이디어를 **자유롭게 공유**할 수 있으며, 서로에게 진솔하게 다가갈 수 있는 안전한 환경을 마련하고 있습니다.  
        익명성을 통해 서로를 **존중하고 격려**하며, 함께 성장하는 커뮤니티입니다.
        """
    )

    # 중간 구분선
    st.markdown("---")
    
    # 커뮤니티의 강점 강조
    st.header("커뮤니티의 강점")
    st.write(
        """
        - **다양성과 포용**: 다양한 배경을 가진 사람들과 함께, 각자의 목소리가 존중받고 가치가 인정되는 커뮤니티입니다.
        - **지식의 허브**: 지속가능발전 목표(SDG)를 위한 최신 지식과 교육 자료를 공유하고, 서로 배우며 성장하는 환경을 제공합니다.
        - **비폭력적 소통**: 갈등이 아닌 **협력**을, 비판이 아닌 **격려**를 중심으로 한 소통 문화를 만들어갑니다.
        - **실질적 영향력**: 우리 커뮤니티의 구성원들은 전 세계적으로 **긍정적인 변화를 일으키는 리더**로 성장하고 있으며, 
          **지속 가능한 미래**를 함께 설계하고 실현해 나갑니다.
        """
    )
    col1, col2 = st.columns([1, 2])  # 가운데 열이 2배 더 넓은 3개 열 구성
    with col1:  # 가운데 열에 이미지를 배치
        st.image("1.jpg", caption="평화롭고 포용적인 사회를 위한 교육", width=400)  # 이미지 크기 조정 (400px)
    with col2:  # 가운데 열에 이미지를 배치
        st.title("지속가능발전을 위한 교육 - SDG 4.7")

    st.write(
        """
        **SDG 4.7**은 2030년까지 모든 학습자들에게 지속가능발전, 지속가능한 생활 방식, 인권, 성평등, 
        평화와 비폭력 문화 확산, 세계시민의식, 문화 다양성 존중 및 지속가능발전을 위한 문화의 기여 등에 대한 
        교육을 통해 지속가능발전 증진을 위한 지식과 기술의 습득을 보장합니다.
        """
    )
    # 또 다른 구분선
    st.markdown("---")
    
    # 커뮤니티 참여 유도
    st.header("당신이 꿈꾸는 세상을 함께 만들어보세요!")
    st.write(
        """
        우리의 목표는 단순한 교육을 넘어 **세상을 바꾸는 실천**에 있습니다.  
        **지속가능발전(SDG) 4.7**의 비전을 실현하기 위해, 우리는 모두가 참여할 수 있는 열린 공간을 제공합니다.

        이제 **여러분**이 이 변화의 일부가 될 차례입니다.  
        우리 커뮤니티와 함께 **더 나은 내일**을 만들어 가세요!
        """
    )

    # 페이지 하단 마무리
    st.markdown("---")
    st.write(
        """
        이러한 교육은 타인을 향한 비난 및 비방이 금지된 커뮤니티와 결합될 때, 
        사회적으로 더욱 큰 영향력을 발휘하며 지속 가능한 평화로운 사회로의 전환을 이끌어냅니다.
        """
    )



def show_sidebar():
    '''이 함수는 여러 페이지를 탐색하기 위한 탭이며, 사용자가 로그인되어있는지 아닌지를 판단하여 그에 맞는 페이지를 불러옵니다.'''
    with st.sidebar:
        if 'logged_in' in st.session_state and st.session_state.logged_in:
            username = st.session_state.username
        else:
            username = 'Anonymous'
        choice = option_menu(username, ['Welcome', "내 정보/로그인", '회원가입', "게시판",  "약관 및 개인정보 활용방침"],
                             icons=['bi bi-house-door', 'bi bi-person', 'bi bi-check-square', 'bi bi-file-text', 'bi bi-info-circle'], key="kind_of_motion",
                             menu_icon="bi bi-person-circle", default_index=0,
                             styles={
                                 "container": {"padding": "4!important", "background-color": "#C9E8C9"},
                                 "icon": {"color": "black", "font-size": "25px"},
                                 "nav-link": {"font-size": "16px", "text-align": "left", "margin": "0px", "--hover-color": "#DFF2D8"},
                                 "nav-link-selected": {"background-color": "#228B22"},
                             }
                             )
        if 'logged_in' in st.session_state and st.session_state.logged_in:
            if st.button('로그아웃'):
                # 로그아웃 처리: 세션 상태 초기화
                st.session_state.logged_in = False
                st.session_state.username = 'Anonymous'
                st.success("로그아웃되었습니다.")

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
