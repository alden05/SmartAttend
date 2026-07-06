import streamlit as st
from src.database.db import create_subject
from src.database.config import supabase
from src.database.db import enroll_student_to_subject
from PIL import Image
import time

# Callback functions to change tabs smoothly without closing the dialog
def set_camera_tab():
    st.session_state.photo_tab = 'camera'

def set_upload_tab():
    st.session_state.photo_tab = 'upload'

@st.dialog("Capture or upload photos")
def add_photos_dialog():
    st.write("Add classroom photos to scan for attendance")

    if 'photo_tab' not in st.session_state:
        st.session_state.photo_tab = 'camera'

    t1, t2 = st.columns(2)

    with t1:
        type_camera = "primary" if st.session_state.photo_tab == 'camera' else "secondary"
        st.button('Camera', type=type_camera, use_container_width=True, on_click=set_camera_tab)

    with t2:
        type_upload = "primary" if st.session_state.photo_tab == 'upload' else "secondary"
        st.button('Upload Photos', type=type_upload, use_container_width=True, on_click=set_upload_tab)
    
    if st.session_state.photo_tab == 'camera':
        cam_photo = st.camera_input("Take Snapshot", key='dialog_cam')
        if cam_photo:
            st.session_state.attendance_images.append(Image.open(cam_photo))
            st.toast('Photo Captured!')
            st.rerun()
        
    if st.session_state.photo_tab == "upload":
        uploaded_files = st.file_uploader('choose image files', type=['jpg','png','jpeg'], accept_multiple_files=True, key='dialog_upload')
        if uploaded_files:
            for f in uploaded_files:
                st.session_state.attendance_images.append(Image.open(f))
            st.toast('Photo Captured!')
            st.rerun()

    st.divider()

    # This button closes the dialog properly
    if st.button('Done', type="primary", use_container_width=True):
        st.rerun()