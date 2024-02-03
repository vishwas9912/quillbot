import streamlit as st
from openai import OpenAI
import langchain
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

hashed_passwords = stauth.Hasher(['au1234', 'au12345']).generate()
with open (Path(__file__).parent/"config.yaml") as file:
    config = yaml.load(file, Loader=SafeLoader)
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)
name,authentication_status,username = authenticator.login("main")
if authentication_status == False:
    st.error("username/password entered is wrong")
if authentication_status == None:
    st.error("please enter the valid details")
if authentication_status:
    embeddings = OpenAIEmbeddings()
    
    client = OpenAI(api_key=st.secrets.get("OPENAI_API_KEY"))
    
    subject_paths = {
        'Python': './data/python',
        'Software Engineering': './data/se',
        'Cryptography and inforrmation security': './data/cis',
        'Java': './data/java',
        'Cloud omputing': './data/fcc'
    }
    
    def get_completion(prompt, model="gpt-3.5-turbo-0613"):
        messages = [{"role": "user", "content": prompt}]
        response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0,
            )
        return response.choices[0].message.content
    
    marks_relevance = {
        2: 2,
        5: 4,
        10: 5
    }
    
    
    with st.sidebar:
        st.title("Quill Bot")
        subject_choice = st.selectbox(label="Subject", options=subject_paths.keys(), placeholder="Subject")
        marks_choice = st.selectbox(label="Marks", options=marks_relevance.keys())
    
    question = st.chat_input("Your Question")
    
    if question:
        st.chat_message("human").write(question)
    
        new_db = Chroma(persist_directory=subject_paths[subject_choice],embedding_function=embeddings)
    
        result = new_db.similarity_search(question, marks_relevance[marks_choice])
        prompt = f"""
        You are an AI assistant that helps the students to get the answers to there questions based on the textbook knowledge that you are\
        provided with.\
        your task is to provide the answer in a student friendly manner but you should not alter the data in the response and make sure all the data is covered thouroughly\
        add any relevant data to the reponse which can be helpfull to the user\
        marks are delimeted by ``,
        if it is for 2 marks then make sure that the response has atleast 100 words with no plaigairism\
        if it is for 5 marks then make sure that the response has atleast 300 words with no plaigairism\
        if it is for 10 marks then make sure that the response has atleast 500 words with no plaigairism\
        if the response is smaller then add extra data from our knowledge\
        given the response generated by the llm is delimeted by ```,
        response:```{result}```
        marks:``{marks_relevance[marks_choice]}``
        """
        response = get_completion(prompt)
    
        st.chat_message("AI").write(str(response))
       
    
