import streamlit as st
import random
import string
import hashlib
import smtplib
import sqlite3
def hash_password(password):
    '''이 함수는 사용자 암호를 해싱하여 저장하는 함수로, 개인정보법에 의해 유져 데이터를 보호하기 위함이다. 해싱된 비밀번호를 return한다.'''
    sha256 = hashlib.sha256()
    sha256.update(password.encode('utf-8'))
    return sha256.hexdigest()

def send_verification_email(email, code):
    '''이 함수는 회원가입 시 smtp서버를 이용하여 사용자에게 인증 메일을 보내는 역할을 한다. 이메일 정송에 성공했는지 실패했는지 RETURN 한다.'''
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587) #gmail사용
        server.starttls()
        server.login('dshsbamboo@gmail.com', 'ighe goyy grfl isnb')  # 발신자 이메일, 비밀번호
        message = f"Subject: BAMBOO code\n\ncode: {code}" # 인증 코드 발송 내용
        server.sendmail('dshsbamboo@gmail.com', email, message)  # 발신자 이메일, 수신자 이메일, 메세지
        server.quit() # 이메일 서버 닫기
        return True
    except Exception as e:
        st.error(f"이메일 보내기 실패: {e}")
        return False

def generate_random_username():
    '''이 함수는 익명성을 보장하기 위해 사용자가 회원가입을 할 때 임의의 사용자이름을 지정해 준다. 생성된 사용자이름을 return 한다.'''
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

def login():
    '''이 함수는 데이터베이스의 사용자 정보와 대조하여 로그인 정보가 올바른지 알려준다.'''
    st.header('로그인')
    with st.form("login_form"):
        email = st.text_input("이메일을 입력하세요:")
        password = st.text_input("비밀번호를 입력해 주세요:", type='password')
        form_submitted = st.form_submit_button("완료")

    if form_submitted:
        if email and password:
            hashed_password = hash_password(password)
            conn = sqlite3.connect('bamboo.db')
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, hashed_password)) # 원래 있던 유저인지 대조
            user = c.fetchone()
            conn.close()

            if user:
                st.success("로그인 성공!")
                st.session_state.username = user[3]
                st.session_state.email = email
                st.session_state.logged_in = True

            else:
                st.error("이메일 또는 비밀번호가 잘못되었습니다.")


def toggle_privacy_policy():
    st.session_state.show_privacy = not st.session_state.show_privacy
def sign_in():
    '''회원가입을 위한 코드이며, 사용자가 이메일을 입력하면 그 이메일로 인증 메일을 보내 확인한 후 회원 가입을 진행한다.'''
    if 'show_privacy' not in st.session_state:
        st.session_state.show_privacy = False
    st.header('회원가입')
    st.session_state.email_sent = True

    with st.form("user_input_form"):
        email = st.text_input("이메일을 입력하세요:")
        password = st.text_input("비밀번호를 입력해 주세요:", type='password')
        consent_given = st.checkbox("약관 및 개인정보 활용방침에 동의합니다.", key="consent_given")
        form_submitted = st.form_submit_button("완료")

    if form_submitted:
        if email and password and consent_given:
            conn = sqlite3.connect('bamboo.db')
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE email = ?", (email,))
            user = c.fetchone()

            if user:
                st.error("이미 가입되어있습니다.")
                conn.close()
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
                conn.close()
        elif not consent_given:
            st.error("약관 및 개인정보 활용방침에 동의해야 합니다.")
        else:
            st.error("이메일과 비밀번호를 입력하세요.")

    if st.session_state.email_sent:
        user_code = st.text_input("이메일로 전송된 인증 코드를 입력하세요:")
        verify_code_submitted = st.button("인증 코드 확인")
        if verify_code_submitted and 'verification_code' in st.session_state:
            if user_code == st.session_state.verification_code :
                st.success("Email 인증 완료!")
                st.session_state.username = generate_random_username()
                st.success(f"생성된 username은 : {st.session_state.username} 입니다!")

                conn = sqlite3.connect('bamboo.db')
                c = conn.cursor()
                #
                c.execute("INSERT INTO users (email, password, username) VALUES (?, ?, ?)",
                          (st.session_state.email, st.session_state.password, st.session_state.username))
                conn.commit()
                conn.close()

                st.session_state.logged_in = True

    st.button("개인정보 활용방침 및 약관", on_click=toggle_privacy_policy)
    if st.session_state.show_privacy:
        show_privacy_policy()


def my_id():
    '''내 id를 보거나 비밀번호 변경을 할 수 있다.'''
    if 'username' in st.session_state:
        username = st.session_state.username
        email = st.session_state.email
    else:
        username = 'Anonymous'
        email = None

    st.header(f'내 정보: 내 이름은: {username}')

    if username != 'Anonymous':
        st.subheader('비밀번호 변경')

        with st.form("password_change_form"):
            new_password = st.text_input("새로운 비밀번호를 입력하세요:", type='password')
            change_submitted = st.form_submit_button("비밀번호 변경")

        if change_submitted:
            if new_password:
                verification_code = ''.join(random.choices(string.digits, k=6))
                st.session_state.password_change_code = verification_code
                st.session_state.new_password = new_password

                if send_verification_email(email, verification_code):
                    st.success(f"{email}로 인증 코드가 전송되었습니다.")
                    st.session_state.email_sent = True
                else:
                    st.error("인증 코드 전송 실패. 이메일 주소를 확인하세요.")
            else:
                st.error("새로운 비밀번호를 입력하세요.")

        if st.session_state.get('email_sent'):
            user_code = st.text_input("이메일로 전송된 인증 코드를 입력하세요:")
            verify_code_submitted = st.button("인증 코드 확인")

            if verify_code_submitted and 'password_change_code' in st.session_state:
                if user_code == st.session_state.password_change_code:
                    hashed_new_password = hash_password(st.session_state.new_password)
                    conn = sqlite3.connect('bamboo.db')
                    c = conn.cursor()
                    c.execute("UPDATE users SET password = ? WHERE email = ?",
                              (hashed_new_password, email))
                    conn.commit()
                    conn.close()

                    st.success("비밀번호가 성공적으로 변경되었습니다.")
                    del st.session_state.password_change_code
                    del st.session_state.new_password
                    del st.session_state.email_sent
                else:
                    st.error("잘못된 인증 코드입니다.")
    else:
        st.error("로그인이 필요합니다.")


def show_privacy_policy():
    '''개인정보법에 의한 서비스 이용약관 및 개인정보 처리방침이다. 유저는 반드시 이 약관에 동의해야 한다.'''
    st.header("이용약관")
    st.write("""
            
제1조 (목적)

BAMBOO 및 BAMBOO 관련 제반 서비스(이하 "서비스"라 합니다)의 이용과 관련하여 BAMBOO와 회원과의 권리, 의무 및 책임사항, 기타 필요한 사항을 규정함을 목적으로 합니다.

제2조 (회원의 정의)

① 회원이란 BAMBOO가 제공하는 서비스에 접속하여 본 약관에 따라 BAMBOO의 이용절차에 동의하고 BAMBOO가 제공하는 서비스를 이용하는 이용자를 말합니다.

제3조 (회원 가입)

① 회원이 되고자 하는 자는 BAMBOO가 정한 가입 양식에 따라 회원정보를 기입하고 "동의", "확인" 등의 버튼을 누르는 방법으로 회원 가입을 신청합니다.\n
② BAMBOO는 제1항과 같이 회원으로 가입할 것을 신청한 자가 다음 각 호에 해당하지 않는 한 신청한 자를 회원으로 등록합니다.\n

    1. 등록 내용에 허위, 기재누락, 오기가 있는 경우
    2. 제6조 제2항에 해당하는 회원 자격 제한 및 정지, 상실을 한 경험이 있었던 경우
    3. 기타 회원으로 등록하는 것이 BAMBOO의 서비스 운영 및 기술상 현저히 지장이 있다고 판단되는 경우

③ 회원가입계약의 성립시기는 BAMBOO의 승낙이 가입신청자에게 도달한 시점으로 합니다.\n
④ 회원은 제1항의 회원정보 기재 내용에 변경이 발생한 경우, 즉시 변경사항을 정정하여 기재하여야 합니다.

제4조 (서비스의 제공 및 변경)

① BAMBOO는 회원에게 아래와 같은 서비스를 제공합니다.

    1. 커뮤니티 서비스 (게시판 등)
    2. 채팅 서비스
    3. 기타 BAMBOO가 자체 개발하거나 다른 BAMBOO와의 협력계약 등을 통해 회원들에게 제공할 일체의 서비스

② BAMBOO는 서비스의 내용 및 제공일자를 제7조 제2항에서 정한 방법으로 회원에게 통지하고, 제1항에 정한 서비스를 변경하여 제공할 수 있습니다.

제5조 (서비스의 중단)

① BAMBOO는 컴퓨터 등 정보통신설비의 보수점검·교체 및 고장, 통신의 두절 등의 사유가 발생한 경우에는 서비스의 제공을 일시적으로 중단할 수 있고, 새로운 서비스로의 교체, 기타 BAMBOO가 적절하다고 판단하는 사유에 기하여 현재 제공되는 서비스를 완전히 중단할 수 있습니다.\n
② 제1항에 의한 서비스 중단의 경우에 BAMBOO는 제7조 제2항에서 정한 방법으로 회원에게 통지합니다. 다만, BAMBOO가 통제할 수 없는 사유로 인한 서비스의 중단(시스템 관리자의 고의, 과실이 없는 디스크 장애, 시스템 다운 등)으로 인하여 사전 통지가 불가능한 경우에는 그러하지 아니합니다.\n

제6조 (회원 탈퇴 및 자격 상실 등)

① 회원은 BAMBOO에 언제든지 자신의 회원 등록 말소(회원 탈퇴)를 요청할 수 있으며 BAMBOO는 위 요청을 받은 즉시 해당 회원의 회원 등록 말소를 위한 절차를 밟습니다.\n
② 회원 탈퇴가 이루어진 경우 회원의 게시물 중 개인 영역(채팅 등)에 등록된 게시물 일체는 삭제됩니다. 다만, 커뮤니티 서비스 등에 등록된 게시물은 삭제되지 않습니다.\n
③ 회원이 다음 각 호의 사유에 해당하는 경우, BAMBOO는 회원의 회원자격을 적절한 방법으로 제한 및 정지, 상실시킬 수 있습니다.

    1. 가입 신청 시에 허위 내용을 등록한 경우
    2. 다른 사람의 서비스 이용을 방해하거나 그 정보를 도용하는 등 전자거래질서를 위협하는 경우
    3. 서비스를 이용하여 법령과 본 약관이 금지하거나 공서양속에 반하는 행위를 하는 경우

④ BAMBOO가 회원의 회원자격을 상실시키기로 결정한 경우에는 회원등록을 말소합니다.\n
⑤ 이용자가 본 약관에 의해서 회원 가입 후 서비스를 이용하는 도중, 연속하여 1년 동안 서비스를 이용하기 위해 로그인 기록이 없는 경우, BAMBOO는 회원의 회원자격을 상실시킬 수 있습니다.

제7조 (회원에 대한 통지)

① BAMBOO가 특정 회원에게 서비스에 관한 통지를 하는 경우 회원정보에 등록된 메일주소를 사용할 수 있습니다.\n
② BAMBOO가 불특정다수 회원에 대한 통지를 하는 경우 7일 이상 공지사항 게시판에 게시함으로써 개별 통지에 갈음할 수 있습니다.

제8조 (회원의 개인정보)

BAMBOO는 서비스를 제공하기 위하여 관련 법령의 규정에 따라 회원으로부터 필요한 개인정보를 수집합니다. (개인정보에 대한 개별 항목은 개인정보처리방침에서 고지)

제9조 (BAMBOO의 의무)

① BAMBOO는 법령과 본 약관이 금지하거나 공서양속에 반하는 행위를 하지 않으며 본 약관이 정하는 바에 따라 지속적이고, 안정적으로 서비스를 제공하기 위해서 노력합니다.\n
② BAMBOO는 회원이 안전하고 편리하게 서비스를 이용할 수 있도록 시스템을 구축합니다.\n
③ BAMBOO는 회원이 원하지 않는 영리목적의 광고성 전자우편을 발송하지 않습니다. 

제10조 (회원의 ID 및 비밀번호에 대한 의무)

① BAMBOO가 관계법령, "개인정보보호정책"에 의해서 그 책임을 지는 경우를 제외하고, 자신의 ID와 비밀번호에 관한 관리책임은 각 회원에게 있습니다.\n
② 회원은 자신의 ID 및 비밀번호를 제3자에게 이용하게 해서는 안됩니다.\n
③ 회원은 자신의 ID 및 비밀번호를 도난당하거나 제3자가 사용하고 있음을 인지한 경우에는 바로 BAMBOO에 통보하고 BAMBOO의 안내가 있는 경우에는 그에 따라야 합니다. 

제11조 (회원의 의무)

① 회원은 다음 각 호의 행위를 하여서는 안됩니다. 

    1. 회원가입신청 또는 변경시 허위내용을 등록하는 행위 
    2. BAMBOO 및 제3자의 지적재산권을 침해하거나 BAMBOO의 권리와 업무 또는 제3자의 권리와 활동를 방해하는 행위 
    3. 다른 회원의 ID를 도용하는 행위
    4. 관련 법령에 의하여 전송 또는 게시가 금지되는 정보(컴퓨터 프로그램 등)의 게시 또는 전송하는 행위
    5. BAMBOO의 직원 또는 서비스의 관리자를 가장하거나 타인의 명의를 도용하여 정보를 게시, 전송하는 행위 
    6. 컴퓨터 소프트웨어, 하드웨어, 전기통신 장비의 정상적인 가동을 방해, 파괴할 목적으로 고안된 소프트웨어 바이러스, 기타 다른 컴퓨터 코드, 파일, 프로그램을 
    포함하고 있는 자료를 게시하거나 전송하는 행위 
    7. 스토킹(stalking) 등 다른 회원을 괴롭히는 행위 
    8. 다른 회원에 대한 개인정보를 그 동의 없이 수집, 저장, 공개하는 행위 
    9. 불특정 다수의 자를 대상으로 하여 광고 또는 선전을 게시하거나 음란물을 게시하는 행위 
    10. BAMBOO가 제공하는 갤로그 및 관련 서비스에 게시된 공지사항 규정을 위반하는 행위

② 제1항에 해당하는 행위를 한 회원이 있을 경우 BAMBOO는 본 약관 제6조 제2, 3항에서 정한 바에 따라 회원의 회원자격을 적절한 방법으로 제한 및 정지, 상실시킬 수 있습니다.\n
③ 회원은 그 귀책사유로 인하여 BAMBOO나 다른 회원이 입은 손해를 배상할 책임이 있습니다.

제12조 (공개게시물의 삭제 또는 이용제한)

① 회원의 공개게시물의 내용이 다음 각 호에 해당하는 경우 BAMBOO는 해당 공개게시물에 대한 접근을 임시적으로 차단하는 조치를 취할 수 있고, 7일 이내에 각 호의 동일 사례가 2회 이상 반복되는 경우 해당 게시물을 삭제 또는 해당 회원의 회원 자격을 제한, 정지 또는 상실시킬 수 있습니다.

    1. 다른 회원 또는 제3자를 비방하거나 중상 모략으로 명예를 손상시키는 내용
    2. 음란물, 욕설 등 공서양속에 위반되는 내용의 정보, 문장, 도형 등을 유포하는 내용
    3. 범죄행위와 관련이 있다고 판단되는 내용
    4. 다른 회원 또는 제3자의 저작권 등 기타 권리를 침해하는 내용
    5. 종교적, 정치적 분쟁을 야기하는 내용으로서, 이러한 분쟁으로 인하여 BAMBOO의 업무가 방해되거나 방해되리라고 판단되는 경우
    6. 타인의 개인정보, 사생활을 침해하거나 명예를 손상시키는 경우
    7. 동일한 내용을 중복하여 다수 게시하는 등 게시의 목적에 어긋나는 경우
    8. 불필요하거나 승인되지 않은 광고, 판촉물을 게재하는 경우

② 회원의 공개게시물로 인한 법률상 이익 침해를 근거로, 다른 회원 또는 제3자가 회원 또는 BAMBOO를 대상으로 하여 민형사상의 법적 조치(예:고소, 가처분신청, 손해배상청구소송)를 취하는 동시에 법적 조치와 관련된 게시물의 삭제를 요청해오는 경우, BAMBOO는 동 법적 조치의 결과(예: 검찰의 기소, 법원의 가처분결정, 손해배상판결)가 있을 때까지 관련 게시물에 대한 접근을 잠정적으로 제한할 수 있습니다. 

제13조 (저작권의 귀속 및 게시물의 이용)

① BAMBOO가 작성한 저작물에 대한 저작권, 기타 지적재산권은 BAMBOO에 귀속합니다.\n
② 회원은 BAMBOO가 제공하는 서비스를 이용함으로써 얻은 정보를 BAMBOO의 사전승낙 없이 복제, 전송, 출판, 배포, 방송, 기타 방법에 의하여 영리목적으로 이용하거나 제3자에게 이용하게 하여서는 안됩니다.\n
③ 회원이 서비스 내에 게시한 게시물의 저작권은 게시한 회원에게 귀속됩니다. 단, BAMBOO는 서비스의 운영, 전시, 전송, 배포, 홍보의 목적으로 회원의 별도의 허락 없이 무상으로 저작권법에 규정하는 공정한 관행에 합치되게 합리적인 범위 내에서 다음과 같이 회원이 등록한 게시물을 사용할 수 있습니다.

    1. 서비스 내에서 회원 게시물의 복제, 수정, 개조, 전시, 전송, 배포 및 저작물성을 해치지 않는 범위 내에서의 편집 저작물 작성
    2. 미디어, 통신사 등 서비스 제휴 파트너에게 회원의 게시물 내용을 제공, 전시 혹은 홍보하게 하는 것. 단, 이 경우 BAMBOO는 별도의 동의 없이 회원의 이용자ID 외에
    회원의 개인정보를 제공하지 않습니다.
    3. BAMBOO는 전항 이외의 방법으로 회원의 게시물을 이용하고자 하는 경우, 전화, 팩스, 전자우편 등의 방법을 통해 사전에 회원의 동의를 얻어야 합니다.

제14조 (광고게재 및 광고주와의 거래)

① BAMBOO가 회원에게 서비스를 제공할 수 있는 서비스 투자기반의 일부는 광고게재를 통한 수익으로부터 나옵니다. 회원은 회원이 등록한 게시물의 내용을 활용한 광고게재 및 기타 서비스상에 노출되는 광고게재에 대해 동의합니다.\n
② BAMBOO는 서비스상에 게재되어 있거나 서비스를 통한 광고주의 판촉활동에 회원이 참여하거나 교신 또는 거래를 함으로써 발생하는 손실과 손해에 대해 책임을 지지 않습니다\n

제15조 (약관의 개정)

① BAMBOO는 약관의규제등에관한법률, 전자거래기본법, 전자서명법, 정보통신망이용촉진등에관한법률 등 관련법을 위배하지 않는 범위에서 본 약관을 개정할 수 있습니다.\n
② 다만, 개정 내용이 회원에게 불리할 경우에는 적용일자 30일 이전부터 적용일자 전일까지 공지합니다. \n
③ 회원은 변경된 약관에 대해 거부할 권리가 있습니다. 회원은 변경된 약관이 공지된 후 15일 이내에 거부의사를 표명할 수 있습니다. 회원이 거부하는 경우 BAMBOO는 당해 회원과의 계약을 해지할 수 있습니다. 만약 회원이 변경된 약관이 공지된 후 15일 이내에 거부의사를 표시하지 않는 경우에는 동의하는 것으로 간주합니다. 

제16조 (재판관할)

BAMBOO와 회원간에 발생한 서비스 이용에 관한 분쟁에 대하여는 대한민국 법을 적용하며, 본 분쟁으로 인한 소는 민사소송법상의 관할을 가지는 대한민국의 법원에 제기합니다. \n
본 약관은 2024년 6월 8일부터 적용합니다.
        """)

    st.header("개인정보 활용방침")
    st.write("""
        BAMBOO는 사용자의 개인정보를 중요하게 생각하며, 아래와 같이 개인정보를 활용합니다.
        「BAMBOO」 개인정보 처리 방침
본 개인정보처리방침은 대구과학고등학교의 교원, 학생이 대상이며, 「BAMBOO」 서비스에 한정합니다.

「BAMBOO」(밤부)는 정보주체의 자유와 권리 보호를 위해 「개인정보 보호법」 및 관계 법령이 정한 바를 준수하여, 적법하게 개인정보를 처리하고 안전하게 관리하고 있습니다.

이에 「개인정보 보호법」 제30조에 따라 정보주체에게 개인정보 처리에 관한 절차 및 기준을 안내하고, 이와 관련한 고충을 신속하고 원활하게 처리할 수 있도록 하기 위하여 다음과 같이 개인정보 처리방침을 수립·공개합니다.

1. 개인정보의 수집항목 및 이용목적
BAMBOO는 다음 목적을 위하여 개인정보를 처리합니다.
처리하고 있는 개인정보는 다음 목적 이외의 용도로 이용하지 않으며, 이용 목적이 변경되는 경우 별도 동의를 받는 등 필요한 조치를 이행할 예정입니다.
구분	항목	목적
서비스 이용	이메일주소	서비스 이용을 위한 기본 정보
2. 개인정보의 수집 및 처리 동의
BAMBOO 서비스에 필요한 개인정보는 정보주체를 통해 직접 수집됩니다.
처리하고 있는 개인정보는 제3자에게 제공되거나 외부 공개되지 않습니다.
3. 개인정보의 처리 및 보유기간
BAMBOO는 교원 및 학생이 학교 이메일을 사용하는 동안 BAMBOO를 통해 수집된 수집된 개인정보를 보유 및 이용합니다.
단, 별도 동의를 받거나 관계 법령에 따라 보존해야하는 경우에는 해당 기간까지 보유·이용할 수 있습니다.
4. 개인정보의 파기 절차 및 방법에 관한 사항
BAMBOO는 개인정보가 불필요하게 되었을 때에 지체없이 해당 개인정보를 파기합니다.

    ① 종이에 출력된 개인정보는 분쇄하여 파기합니다.
    
    ② 전자적 파일형태로 저장된 개인정보는 기록을 재생할 수 없는 기술적 방법을 사용하여 삭제합니다.

5. 개인정보 보호책임자에 관한 사항
BAMBOO는 개인정보를 보호하고 개인정보와 관련한 고충처리를 위하여 아래와 같이 개인정보 보호책임자를 지정하고 있습니다.

    책임자: 전지훈
    """)
