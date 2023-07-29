import streamlit as st
import openai
from time import sleep
import os
import pyperclip

if "openai_api_key" not in st.session_state:
    st.session_state.openai_api_key = ''
    
if 'message_history' not in st.session_state:
    st.session_state.message_history = []

def check_password():

    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == os.getenv("password"):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.write("*Please contact David Liebovitz, MD if you need an updated password for access.*")
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Password incorrect")
        return False
    else:
        # Password correct.
        # fetch_api_key()
        return True
    
def gen_response(prefix, history, model):
    history.append({"role": "system", "content": prefix})
    sleep(1)
    response = openai.ChatCompletion.create(
        model=st.session_state.model,
        messages = history,
        temperature=0.9,
    )
    # summary = response['choices'][0]['message']['content']
    # st.session_state.message_history.append(summary)
    # st.write(f'Here is the input summary: {summary}')
    return response



st.set_page_config(page_title='Patient Reporting Assistant', layout = 'centered', page_icon = ':stethoscope:', initial_sidebar_state = 'auto')

st.title("Patient Reporting Assistant")
st.write("ALPHA version 0.2")
disclaimer = """**Disclaimer:** This is a tool for educational use only! \n 
Never submit any personally identifiable content. \n    
    """
openai.api_key = st.secrets["OPENAI_API_KEY"]   
if check_password():    

    with st.expander('About Patient Reporting Assistant - Important Disclaimer'):
        st.write("Author: David Liebovitz, MD, Northwestern University")
        st.info(disclaimer)
        st.write("Last updated 7/27/23")
        
    selected_model = st.selectbox("Pick your GPT model:", ("GPT-3.5 ($)", "GPT-3.5 16k ($$)", "GPT-4 ($$$$)"))
    if selected_model == "GPT-3.5 ($)":
        model = "gpt-3.5-turbo"
    elif selected_model == "GPT-4 ($$$$)":
        model = "gpt-4"
    elif selected_model == "GPT-3.5 16k ($$)":
        model = "gpt-3.5-turbo-16k"
 
    health_literacy_level = st.radio("Output optimized for:", ("Low Health Literacy", "High Health Literacy"))
    st.warning("Do not enter any PHI. No dates, names, or other identifying information.")
    system_prompt = """You are an expert physician who sees very complex patients. There are often many 
    abnormal findings in reports for your patients. You always provide accurate information and strive to reassure patients when immediate next steps are not needed.
    You know that many tests, e.g., ECGs, often contain false positive findings and that many findings are not clinically significant. 
    If there is any ambiguity in the findings, you offer to discuss in more detail at the patient's next visit.
    You receive a test result as input and generate the patient friendly summary (explaining any jargon) in keeping with the health literacy level requested. 
    
    Format your response as if you are speaking to a patient:
    
    ``` Dear ***,
    
    I have reviewed your test results.
    ...
    
    Kind regards,
    
    ***  
    
    """
    col1, col2 = st.columns(2)
    with col1:
        submitted_result = st.text_area("Paste your result content here without PHI.", height=600)
    
    user_prompt = f'Generate a reassuring summary as if it is authored by a physician for her patient with {health_literacy_level} with this {submitted_result}'
    if st.button("Generate Patient Summary"):
        try:
            response= openai.ChatCompletion.create(
            model= model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature = 0, 
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
            )
            with col2:
                our_summary = response.choices[0].message.content
                st.write(response.choices[0].message.content)
                pyperclip.copy(our_summary)
                st.success("Summary copied to clipboard.")
        except:

            st.write("API busy. Try again - better error handling coming. :) ")
            st.stop()
    