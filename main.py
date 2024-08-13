import streamlit as st
import openai
from time import sleep
import os
import pyperclip
from prompts import dc_instructions_prompt, report1, report2, system_prompt


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
disclaimer = """**Disclaimer:** This is a tool for educational use only! \n 
Never submit any personally identifiable content. \n    
    """
openai.api_key = st.secrets["OPENAI_API_KEY"]   
if check_password():    

    with st.expander('About Patient Reporting Assistant - Important Information'):
        st.write("Author: David Liebovitz, MD, Northwestern University")
        st.info(disclaimer)
        # selected_model = st.selectbox("Modify the GPT model:", ("GPT-3.5 ($)", "GPT-3.5 16k ($$)", "GPT-4 ($$$$)"))
    st.warning("Do not enter any PHI. No dates, names, or other identifying information.")   
     
    
    # if selected_model == "GPT-3.5 ($)":
    #     model = "gpt-3.5-turbo"
    # elif selected_model == "GPT-4 ($$$$)":
    #     model = "gpt-4"
    # elif selected_model == "GPT-3.5 16k ($$)":
    #     model = "gpt-3.5-turbo-16k"
    col1, col2 = st.columns(2)
    with col2:
        health_literacy_level = st.radio("Output optimized for:", ("Low Health Literacy", "High Health Literacy"))
    






    with col1:
        task = st.radio("What do you want to do?", ("Generate discharge instructions", "Annotate a patient result"))

    if task == "Generate discharge instructions":
        
        surg_procedure = st.text_area("Please enter the procedure performed and any special concerns.")
        dc_meds = st.text_area("Please enter the discharge medications.")
        dc_instructions_context = f'Generate discharge instructions for a patient as if it is authored by a physician for her patient with {health_literacy_level} with this {surg_procedure} on {dc_meds}'
        if st.button("Generate Patient Information"):
            with st.spinner("Generating..."):
                try:
                    response= openai.ChatCompletion.create(
                    model= "gpt-4o",
                    messages=[
                        {"role": "system", "content": dc_instructions_prompt},
                        {"role": "user", "content": dc_instructions_context}
                    ],
                    temperature = 0, 
                    top_p=1,
                    frequency_penalty=0,
                    presence_penalty=0
                    )
                    
                    our_summary = response.choices[0].message.content
                    st.write(response.choices[0].message.content)
                    # pyperclip.copy(our_summary)
                    # st.success("Summary copied to clipboard.")
                except:

                    st.write("API busy. Try again - better error handling coming. :) ")
                    st.stop()

    if task == "Annotate a patient result":
        sample_report1 = st.sidebar.radio("Try a sample report:", ("Text box for your own content", "Sample 1 (lung CT)", "Sample 2 (ECG)", ))
        if sample_report1 == "Sample 1 (lung CT)":
            submitted_result = report1
            with col1:
                st.write(report1)
        elif sample_report1 == "Sample 2 (ECG)":
            submitted_result = report2
            with col1:
                st.write(report2)
        elif sample_report1 == "Text box for your own content":           
            with col1:                
                submitted_result = st.text_area("Paste your result content here without PHI.", height=600)
           
        
        user_prompt = f'Generate a brief reassuring summary as if it is authored by a physician for her patient with {health_literacy_level} with this {submitted_result}. When appropriate emphasize that the findings are not urgent and you are happy to answer any questions at the next visit. '

        with col1:
            if st.button("Generate Patient Summary"):
                with st.spinner("Generating..."):
                    try:
                        response= openai.ChatCompletion.create(
                        model= "gpt-4o",
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
                            # pyperclip.copy(our_summary)
                            # st.success("Summary copied to clipboard.")
                    except:

                        st.write("API busy. Try again - better error handling coming. :) ")
                        st.stop()
        