import streamlit as st
import random
import string
import hashlib
import smtplib
from supabase import create_client, Client

# Initialize Supabase client
SUPABASE_URL = "https://kwucjttxdmtntzrvaucm.supabase.co"
SUPABASE_KEY = "YOUR_SUPABASE_ANON_KEY"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Helper function for hashing
def hash_password(password):
    sha256 = hashlib.sha256()
    sha256.update(password.encode('utf-8'))
    return sha256.hexdigest()

# Function to handle Google login and set session state
def check_user_session():
    user = supabase.auth.get_user()
    if user:
        st.session_state.logged_in = True
        st.session_state.username = user.user_metadata.get("username", "GoogleUser")
        st.session_state.email = user.email
        st.success("Google 인증을 통해 로그인되었습니다.")
    else:
        st.session_state.logged_in = False

# Google Login Redirect
def google_auth_redirect():
    auth_url = f"{SUPABASE_URL}/auth/v1/authorize?provider=google&redirect_to=https://bamboo.streamlit.app/"
    st.markdown(f"[Google로 로그인]({auth_url})", unsafe_allow_html=True)
    st.write("Google 인증 후, 자동으로 돌아옵니다.")
def my_id():
    '''Displays user ID and allows password changes.'''
    # Ensure the user is logged in
    if not st.session_state.get('logged_in'):
        st.error("로그인이 필요합니다.")
        return

    # Retrieve username and email from session state
    username = st.session_state.get('username', 'Anonymous')
    email = st.session_state.get('email', None)

    st.header(f'내 정보: 내 이름은: {username}')

    # Password change form if user is logged in
    if username != 'Anonymous' and email:
        st.subheader('비밀번호 변경')

        # Password change form
        with st.form("password_change_form"):
            new_password = st.text_input("새로운 비밀번호를 입력하세요:", type='password')
            change_submitted = st.form_submit_button("비밀번호 변경")

        if change_submitted:
            if new_password:
                # Generate and send verification code
                verification_code = ''.join(random.choices(string.digits, k=6))
                st.session_state.password_change_code = verification_code
                st.session_state.new_password = new_password

                # Send email verification code
                if send_verification_email(email, verification_code):
                    st.success(f"{email}로 인증 코드가 전송되었습니다.")
                    st.session_state.email_sent = True
                else:
                    st.error("인증 코드 전송 실패. 이메일 주소를 확인하세요.")
            else:
                st.error("새로운 비밀번호를 입력하세요.")

        # Code verification and password update
        if st.session_state.get('email_sent'):
            user_code = st.text_input("이메일로 전송된 인증 코드를 입력하세요:")
            verify_code_submitted = st.button("인증 코드 확인")

            if verify_code_submitted and 'password_change_code' in st.session_state:
                if user_code == st.session_state.password_change_code:
                    # Hash the new password
                    hashed_new_password = hash_password(st.session_state.new_password)

                    # Update password in Supabase
                    response = supabase.table("users").update({"password": hashed_new_password}).eq("email", email).execute()

                    if response.status_code == 200:
                        st.success("비밀번호가 성공적으로 변경되었습니다.")
                        # Clear temporary session variables
                        del st.session_state.password_change_code
                        del st.session_state.new_password
                        del st.session_state.email_sent
                    else:
                        st.error("비밀번호 업데이트 중 문제가 발생했습니다.")
                else:
                    st.error("잘못된 인증 코드입니다.")

# Main Login Function
def login():
    # Check if user is already logged in through Google
    if not st.session_state.get("logged_in"):
        check_user_session()
    
    if st.session_state.get("logged_in"):
        st.write("이미 로그인되었습니다.")
        st.write(f"Welcome, {st.session_state.username}")
    else:
        st.header('로그인')
        google_auth_redirect()

        # Standard Login Form for email and password
        with st.form("login_form"):
            email = st.text_input("이메일을 입력하세요:")
            password = st.text_input("비밀번호를 입력해 주세요:", type='password')
            form_submitted = st.form_submit_button("완료")

        if form_submitted and email and password:
            hashed_password = hash_password(password)
            response = supabase.table("users").select("*").eq("email", email).eq("password", hashed_password).execute()

            if response.data:
                user = response.data[0]
                st.session_state.logged_in = True
                st.session_state.username = user["username"]
                st.session_state.email = email
                st.success("로그인 성공!")
            else:
                st.error("이메일 또는 비밀번호가 잘못되었습니다.")

# Sign-Up Function
def sign_in():
    if 'show_privacy' not in st.session_state:
        st.session_state.show_privacy = False
    st.header('회원가입')

    google_auth_redirect()

    # Standard Sign-Up Form
    with st.form("user_input_form"):
        email = st.text_input("이메일을 입력하세요:")
        password = st.text_input("비밀번호를 입력해 주세요:", type='password')
        consent_given = st.checkbox("약관 및 개인정보 활용방침에 동의합니다.", key="consent_given")
        form_submitted = st.form_submit_button("완료")

    if form_submitted:
        if email and password and consent_given:
            response = supabase.table("users").select("*").eq("email", email).execute()
            if response.data:
                st.error("이미 가입되어있습니다.")
            else:
                verification_code = ''.join(random.choices(string.digits, k=6))
                st.session_state.verification_code = verification_code
                if send_verification_email(email, verification_code):
                    st.session_state.email_sent = True
                    st.success(f"{email}로 인증 코드가 전송되었습니다.")
                    st.session_state.email = email
                    st.session_state.password = hash_password(password)
                else:
                    st.error("인증 코드 전송에 실패했습니다.")
        elif not consent_given:
            st.error("약관 및 개인정보 활용방침에 동의해야 합니다.")
        else:
            st.error("이메일과 비밀번호를 입력하세요.")

    if st.session_state.email_sent:
        user_code = st.text_input("이메일로 전송된 인증 코드를 입력하세요:")
        verify_code_submitted = st.button("인증 코드 확인")
        if verify_code_submitted and 'verification_code' in st.session_state:
            if user_code == st.session_state.verification_code:
                st.success("Email 인증 완료!")
                st.session_state.username = generate_random_username()
                st.success(f"생성된 username은 : {st.session_state.username} 입니다!")

                # Store new user in Supabase
                supabase.table("users").insert({
                    "email": st.session_state.email,
                    "password": st.session_state.password,
                    "username": st.session_state.username
                }).execute()
                st.session_state.logged_in = True

    st.button("개인정보 활용방침 및 약관", on_click=toggle_privacy_policy)
    if st.session_state.show_privacy:
        show_privacy_policy()
