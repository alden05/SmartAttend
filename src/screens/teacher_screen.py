import streamlit as st
from src.ui.base_layout import style_background_dashboard,style_base_layout
from src.components.header import header_dashboard
from src.components.footer import footer_dashboard
from src.database.db import check_teacher_exists,create_teacher,teacher_login
def teacher_screen():
    style_background_dashboard()
    style_base_layout()

    if "teacher_data" in st.session_state:
        teacher_dashboard()
    elif 'teacher_login_type' not in st.session_state or st.session_state.teacher_login_type=="login":
        teacher_screen_login()
    elif st.session_state.teacher_login_type=="register":
        teacher_screen_register()


def teacher_dashboard():
    teacher_data=st.session_state.teacher_data
    st.header(f"Welcome,{teacher_data["name"]}")
    
def login_teacher(username,password):
    if not username or not password:
        return False
    teacher=teacher_login(username,password)
    if teacher:
        st.session_state.teacher_data=teacher
        st.session_state.user_role="teacher"
        st.session_state.is_logged_in=True
        return True
    return False

def teacher_screen_login():
    col1,col2 = st.columns(2, vertical_alignment='center',gap='xxlarge')
    with col1:
        header_dashboard()
    with col2:
        if st.button("Go back to Home", type='primary',key="loginbackbtn", shortcut="control+backspace"):
            st.session_state['login_type']=None
            st.rerun()
    
    st.header('Login using password',text_alignment='center')
    st.space()
    teacher_username=st.text_input("Enter Username", placeholder='Pranjli Aggarwal')
    teacher_password=st.text_input("Enter Password",type='password',placeholder='Enter Password')
    st.divider()
    btnc1,btnc2=st.columns(2)
    with btnc1:
        if st.button('Login',type='primary',icon=':material/passkey:',shortcut='control+enter',width='stretch'):
            if login_teacher(teacher_username,teacher_password):
                st.toast("Welcome Back!",icon="👋")
                import time
                time.sleep(1)
                st.rerun()
            else:
                st.error("Invalid username or password combo!")

    with btnc2:
        if st.button('Register New User',type='secondary',icon=':material/passkey:',width='stretch'):
            st.session_state.teacher_login_type='register'
            st.rerun()


    
    footer_dashboard()

def register_teacher(teacher_username,teacher_name,teacher_password,teacher_password_confirm):
    if not teacher_username or not teacher_name or not teacher_password:
        return False,"All Fields are Required!"
    if check_teacher_exists(teacher_username):
        return False,"Username already taken!"
    if teacher_password!=teacher_password_confirm:
        return False,"Password doesn't match!"
    try:
        create_teacher(teacher_username,teacher_password,teacher_name)
        return True,"Successfully created! Login now"
    except Exception as e:
        return False,"Unexpected Error!"


def teacher_screen_register():
    col1,col2 = st.columns(2, vertical_alignment='center',gap='xxlarge')
    with col1:
        header_dashboard()
    with col2:
        if st.button("Go back to Home",type='primary', key="loginbackbtn", shortcut="control+backspace"):
            st.session_state['login_type']=None
            st.rerun()
    
    st.header('Register your Teacher Profile',text_alignment='center')

    st.space()
    st.space()
    teacher_username=st.text_input("Enter Username", placeholder='pranjli07')
    teacher_name=st.text_input("Enter Name", placeholder='Pranjli Aggarwal')
    teacher_password=st.text_input("Enter Password",type='password',placeholder='Enter Password')
    teacher_password_confirm=st.text_input("Confirm your Password",type='password',placeholder='Confirm Password')
    st.divider()
    btnc1,btnc2=st.columns(2)
    with btnc1:
        if st.button('Register Now',type='primary',icon=':material/passkey:',shortcut='control+enter',width='stretch'):
            success,message=register_teacher(teacher_username,teacher_name,teacher_password,teacher_password_confirm)
            if success:
                st.success(message)
                import time
                time.sleep(2)
                st.session_state.teacher_login_type="login"
                st.rerun()
            else:
                st.error(message)

    with btnc2:
        if st.button('Login Instead',type='secondary',icon=':material/passkey:',width='stretch'):
            st.session_state.teacher_login_type='login'
            st.rerun()


    
    footer_dashboard()

