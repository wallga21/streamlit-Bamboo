import hashlib
import random
import string
import smtplib
import streamlit as st

def hash_password(password):
    sha256 = hashlib.sha256()
    sha256.update(password.encode('utf-8'))
    return sha256.hexdigest()

def send_verification_email(email, code):
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login('dshsbamboo@gmail.com', 'ighe goyy grfl isnb')  # 발신자 이메일과 비밀번호
        message = f"Subject: BAMBOO code\n\ncode: {code}"
        server.sendmail('dshsbamboo@gmail.com', email, message)  # 발신자 이메일, 수신자 이메일, 메세지
        server.quit()
        return True
    except Exception as e:
        st.error(f"이메일 보내기 실패: {e}")
        return False

def generate_random_username():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))
