import streamlit as st
import datetime
from supabase import create_client, Client
from cleanengine import nametest, goodbad

# Initialize Supabase client
SUPABASE_URL = "https://kwucjttxdmtntzrvaucm.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imt3dWNqdHR4ZG10bnR6cnZhdWNtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mjk5MDg4MTQsImV4cCI6MjA0NTQ4NDgxNH0.ST0-QIovKBVIFzKATRM-nDgyNkeQyMJo097P5iccCFo"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
BUCKET_NAME = "Bamboo-files"  # Name of your Supabase Storage bucket

def board():
    '''Displays posts from the database in chronological order or uploads user-created posts with file storage support.'''
    st.header('게시판')
    if 'title' not in st.session_state:
        st.session_state.title = ''
    if 'content' not in st.session_state:
        st.session_state.content = ''
    if 'file' not in st.session_state:
        st.session_state.file = None

    # Post Creation
    if st.session_state.get('logged_in'):
        st.subheader('새 게시글 작성')

        with st.form("post_form"):
            st.session_state.title = st.text_input("제목을 입력하세요:", value=st.session_state.title)
            st.session_state.content = st.text_area("내용을 입력하세요:", value=st.session_state.content)
            st.session_state.file = st.file_uploader("파일을 업로드하세요:",
                                                     type=["jpg", "jpeg", "png", "pdf", "docx", "xlsx", "hwp", "hwpx", "cap"])
            submit_button = st.form_submit_button("게시")

        if submit_button:
            if st.session_state.title and st.session_state.content:
                # Content filtering
                test = st.session_state.title + ' ' + st.session_state.content
                goodbad_result = goodbad(test)
                if goodbad_result > 0.9 or (nametest(test) and goodbad_result > 0.6):
                    st.error("cleanengine에 의하여 게시가 제한되었습니다. 타인을 비난 및 비방하는 글은 삼가주시기 바랍니다.")
                else:
                    # Prepare metadata and file data
                    file_url, file_name = None, None
                    if st.session_state.file:
                        file_name = st.session_state.file.name
                        # Upload file to Supabase Storage
                        response = supabase.storage.from_(BUCKET_NAME).upload(
                            f"{st.session_state.username}/{file_name}", st.session_state.file
                        )
                        if response.get("error"):
                            st.error("파일 업로드에 실패했습니다.")
                        else:
                            # Retrieve public URL
                            file_url = supabase.storage.from_(BUCKET_NAME).get_public_url(
                                f"{st.session_state.username}/{file_name}"
                            )["publicURL"]

                    # Save post data in Supabase
                    now_utc = datetime.datetime.utcnow()
                    kst_time = now_utc + datetime.timedelta(hours=9)  # Convert to Korean time (UTC + 9)
                    timestamp = kst_time.strftime("%Y-%m-%d %H:%M:%S")
                    name = st.session_state.username

                    post_data = {
                        "username": name,
                        "title": st.session_state.title,
                        "content": st.session_state.content,
                        "file_name": file_name,
                        "file_url": file_url,
                        "timestamp": timestamp,
                        "is_deleted": False
                    }

                    # Insert post data into Supabase
                    supabase.table("posts").insert(post_data).execute()

                    # Reset form inputs
                    st.session_state.title = ''
                    st.session_state.content = ''
                    st.session_state.file = None
                    st.success("게시글이 성공적으로 게시되었습니다.")
            else:
                st.error("제목과 내용을 입력하세요.")

    # Display Posts
    st.subheader('게시글 목록')
    response = supabase.table("posts").select("*").order("timestamp", desc=True).execute()
    posts = response.data

    current_user = st.session_state.get('username')
    if 'delete_post_id' not in st.session_state:
        st.session_state['delete_post_id'] = None

    for post_data in posts:
        if post_data['is_deleted']:
            st.write("삭제된 글입니다.")
        else:
            st.write(f"### {post_data['title']}")
            st.write(f"작성자: {post_data['username']}")
            st.write(f"작성 시간: {post_data['timestamp']}")
            st.write(post_data['content'])

            # Show delete button for post owner
            if post_data['username'] == current_user:
                if st.session_state['delete_post_id'] is None:
                    if st.button(f"{post_data['id']}번 글 삭제", key=f"delete_button_{post_data['id']}"):
                        st.session_state['delete_post_id'] = post_data['id']
                        st.rerun()

                if st.session_state['delete_post_id'] == post_data['id']:
                    st.warning("이 글을 삭제하시겠습니까?", icon="⚠️")
                    if st.button("예, 삭제합니다", key=f"confirm_delete_{post_data['id']}"):
                        supabase.table("posts").update({"is_deleted": True}).eq("id", post_data['id']).execute()
                        st.success("게시글이 삭제되었습니다.")
                        st.session_state['delete_post_id'] = None
                        st.rerun()
                    elif st.button("취소", key=f"cancel_delete_{post_data['id']}"):
                        st.session_state['delete_post_id'] = None
                        st.rerun()

            # Display file if available and not deleted
            if post_data['file_url'] and not post_data['is_deleted']:
                if post_data['file_name'].lower().endswith(('jpg', 'jpeg', 'png')):
                    st.image(post_data['file_url'], use_column_width=True)
                else:
                    st.write(f"[{post_data['file_name']} 다운로드]({post_data['file_url']})", unsafe_allow_html=True)

        st.divider()
