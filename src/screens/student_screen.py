import streamlit as st
from src.ui.base_layout import style_background_dashboard,style_base_layout
from src.components.header import header_dashboard
from src.components.footer import footer_dashboard
from src.pipelines.face_pipeline import predict_attendance,get_face_embeddings,train_classifier
from src.pipelines.voice_pipeline import get_voice_embedding
from src.database.db import get_all_students,create_student,get_student_subjects,get_student_attendance,unenroll_student_to_subject
from src.components.dialog_enroll import enroll_dialog
from src.components.subject_card import subject_card
from PIL import Image
import numpy as np
import time

def student_dashboard():
    student_data=st.session_state.student_data
    student_id=student_data['student_id']
    col1,col2 = st.columns(2, vertical_alignment='center',gap='xxlarge')
    with col1:
        header_dashboard()
    with col2:
        
        if st.button("Logout", type='primary',key="loginbackbtn", shortcut="control+backspace"):
            st.session_state['is_logged_in']=False
            del st.session_state.student_data
            st.rerun()
    st.divider()


    st.markdown(
        f'<h2 style="text-align: center;">Welcome {student_data["name"]} !</h2>', 
        unsafe_allow_html=True
    )

    st.divider()

    col1,col2=st.columns(2,vertical_alignment="center")
    with col1:
        st.header("Your Enrolled Subjects")
    with col2:
        
        if st.button("Enroll in Subject", type='primary',width="stretch"):
            enroll_dialog()

    st.space()

    with st.spinner('Loading your enrolled subjects...'):
        subjects=get_student_subjects(student_id)
        logs=get_student_attendance(student_id)
    
    stats_map={}

    for log in logs:
        sid=log['subject_id']

        if sid not in stats_map:
            stats_map[sid]={'total':0,'attended':0}

        stats_map[sid]['total']+=1

        if log.get('is_present'):
            stats_map[sid]['attended']+=1

    cols=st.columns(2)
    for i,sub_node in enumerate(subjects):
        sub=sub_node['subjects']
        sid=sub['subject_id']


        stats=stats_map.get(sid,{'total':0,'attended':0})
        def unenroll_button():
            if st.button("Unenroll from this Course",type="secondary",width="stretch",icon=":material/delete_forever:",key=f"unenroll_{sub["subject_code"]}"):
                unenroll_student_to_subject(student_id,sid)
                st.toast(f"Unenrolled from {sub['name']} successfully")
                st.rerun()
        with cols[i%2]:
            subject_card(
                name=sub['name'],
                code=sub['subject_code'],
                section=sub['section'],
                stats=[
                    ('📆','Total',stats['total']),
                    ('✅','Attended',stats['attended'])
                ],
                footer_callback= unenroll_button
            )






    footer_dashboard()
    
def student_screen():
    style_background_dashboard()
    style_base_layout()

    if "student_data" in st.session_state:
        student_dashboard()
        return
    col1,col2 = st.columns(2, vertical_alignment='center',gap='xxlarge')
    with col1:
        header_dashboard()
    with col2:
        if st.button("Go back to Home", type='primary',key="loginbackbtn", shortcut="control+backspace"):
            st.session_state['login_type']=None
            st.rerun()
    
    st.divider()

    st.header("Login using Face ID",text_alignment='center')
    st.space()

    show_registration=False
    photo_source = st.camera_input(
        """📸 Capture Photo
            Center your face • Look at the camera • Use good lighting
            """
                )

    if photo_source:
        img=np.array(Image.open(photo_source))

        with st.spinner("AI is scanning..."):
            detected, all_ids, num_faces=predict_attendance(img)

            if num_faces==0:
                st.warning("Face not found!")
            elif num_faces>1:
                st.warning("Multiple faces detected!")
            else:
                if detected:
                    student_id=list(detected.keys())[0]
                    all_students=get_all_students()
                    student=next((s for s in all_students if s["student_id"]==student_id),None)

                    if student:
                        st.session_state.is_logged_in=True
                        st.session_state.user_role="student"
                        st.session_state.student_data=student
                        st.toast(f"Welcome Back {student["name"]}")
                        time.sleep(1)
                        st.rerun()
                else:
                    st.info("Face not recognised, You might be a new student")
                    show_registration=True
    if show_registration:
        with st.container(border=True):
             st.header("Register New Profile")
             new_name=st.text_input("Enter your name", placeholder="e.g. Alden D'Souza")

             st.subheader("Optional: Voice Enrollment")
             st.info("Enroll your voice for attendance")

             audio_data=None

             try:
                 audio_data=st.audio_input("Record a short phrase,e.g. I am Present")
             except Exception:
                 st.error("Audio Data Failed!")

             if st.button("Create Account", type="primary"):
                 if new_name:
                     with st.spinner("Creating Profile ..."):
                         img=np.array(Image.open(photo_source))
                         encodings=get_face_embeddings(img)
                         if encodings:
                             face_emb=encodings[0].tolist()
                             voice_emb=None
                             if audio_data:
                                 voice_emb=get_voice_embedding(audio_data.read())

                             response_data=create_student(new_name, face_embedding=face_emb, voice_embedding=voice_emb)

                             if response_data:
                                 train_classifier()
                                 st.session_state.is_logged_in=True
                                 st.session_state.user_role="student"
                                 st.session_state.student_data=response_data[0]
                                 st.toast(f"Profile Created! Welcome {new_name}")
                                 time.sleep(1)
                                 st.rerun()
                         else:
                             st.error("Couldn't capture your facial feature for recognition!")

                 else:
                     st.warning("Please enter your name!")

                 

    footer_dashboard()