import os
import streamlit as st
from chatbot.harassment_bot import process_message
from collections import Counter
from langchain import hub
from langchain_groq import ChatGroq
from langchain_core.prompts import MessagesPlaceholder
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage,SystemMessage
from dotenv import load_dotenv
load_dotenv()
groq_api = os.getenv('GROQ_API_KEY')

prompt = ChatPromptTemplate.from_messages(
    [
        ('system','You are a helpful Asistant'),
        MessagesPlaceholder('chat_history'),
        ('human','{input}'),
        MessagesPlaceholder('agent_scratchpad')
    ]
)
llm = ChatGroq(model_name='Llama-3.3-70b-Versatile',groq_api_key = groq_api)


chat_history = [("System", "Hello! Welcome to the Grievance Chatbot. Your safety and well-being are our utmost priority. How may I help you?")]
context = ""
grievance_stage = 1 

st.title("Griveance Bot")


if 'chat_history' not in st.session_state:
    st.session_state.chat_history = chat_history

if 'context' not in st.session_state:
    st.session_state.context = context

if 'grievance_stage' not in st.session_state:
    st.session_state.grievance_stage = grievance_stage

def submit_message():
    user_input = st.session_state.input_message
    if user_input:
       
        st.session_state.chat_history.append(("User", user_input))
        
        response, updated_history, updated_context, updated_stage, final_response = process_message(
            user_input, st.session_state.chat_history, st.session_state.context, st.session_state.grievance_stage, llm, prompt)
        
        st.session_state.chat_history = updated_history
        st.session_state.context = updated_context
        st.session_state.grievance_stage = updated_stage

        if updated_stage == 0:
            st.session_state.admin_display = st.markdown(final_response)
        
        st.session_state.input_message = ""

for i, (sender, message) in enumerate(st.session_state.chat_history):
    if sender == "System":
        if i == 0:
            st.chat_message("assistant").write(message)  
        else:
            st.chat_message("user").write(message)
    else:
        if not i%2 : 
            st.chat_message("assistant").write(message)
        else:
            st.chat_message("user").write(message)
       
# for i, (sender, message) in enumerate(st.session_state.chat_history):
#     if sender == "System":
#         if i == 0:
#             st.chat_message("assistant").write(message) 
#         else:
#             st.chat_message("assistant").write(message)
#     else:
#         st.chat_message("user").write(message)     


st.text_input("Enter your message", key="input_message", on_change=submit_message)


rate_limit = 60 
api_calls_counter = Counter()  
