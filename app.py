import streamlit as st
import sqlite3
from urllib.parse import quote_plus

from pathlib import Path
from langchain_community.agent_toolkits import create_sql_agent
from langchain_community.utilities import SQLDatabase
from langchain.agents.agent_types import AgentType
from langchain.callbacks import StreamlitCallbackHandler  
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from sqlalchemy import create_engine
from langchain_groq import ChatGroq


st.set_page_config(page_title="Langchain: chat with SQL DB", page_icon=":robot:")
st.title("Langchain: chat with SQL DB")


LOCALDB="USE_LOCALDB"
MYSQL="USE_MYSQL"

radio_option=["Use SQLitee 3 Database - Student.db","Connect to your MySQL Database"]

selected_opt=st.sidebar.radio(label="Choose the DB whivh you want to chat", options=radio_option)

if radio_option.index(selected_opt)==1:
  db_uri=MYSQL
  mysql_host=st.sidebar.text_input("Provide MySQL host")
  mysql_user=st.sidebar.text_input("Provide MySQL user")
  mysql_password=st.sidebar.text_input("Provide MySQL password")
  mysql_db=st.sidebar.text_input("Provide MySQL database name") 
else:
  db_uri=LOCALDB

api_key=st.sidebar.text_input("Groq API key",type='password')

if not db_uri:
  st.info("please enter the database information and uri")
  
if not api_key:
  st.info("please enter the Groq API key to proceed")
  st.stop()

## LLM model
llm=ChatGroq(groq_api_key=api_key,model_name="llama-3.1-8b-instant",streaming=True)

@st.cache_resource(ttl="2h")
def configure_db(db_uri,mysql_host=None,mysql_user=None,mysql_password=None,mysql_db=None): 
  if db_uri==LOCALDB:
    dbfilepath=(Path(__file__).parent/"student.db").absolute()
    print(dbfilepath)
    creator= lambda: sqlite3.connect(f"file:{dbfilepath}?mode=ro",uri=True)
    return SQLDatabase(create_engine("sqlite:///student.db",creator=creator))
  elif db_uri==MYSQL:
    if not (mysql_host and mysql_user and mysql_password and mysql_db):
      st.info("please enter all MySQL database information")
      st.stop()
    return SQLDatabase(create_engine(f"mysql+mysqlconnector://{mysql_user}:{quote_plus(mysql_password)}@{mysql_host}/{mysql_db}"))
  
if db_uri==LOCALDB:
  db=configure_db(db_uri)
elif db_uri==MYSQL:
  db=configure_db(db_uri,mysql_host=mysql_host,mysql_user=mysql_user,mysql_password=mysql_password,mysql_db=mysql_db)
  
  
  
  
##toolkit

toolkit=SQLDatabaseToolkit(db=db,llm=llm)

agent=create_sql_agent(
  llm=llm,
  toolkit=toolkit,
  verbose=True,
  agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
  system_message="""
    You are a SQL expert.
Rules:
1. Immediately convert the user question into a SINGLE SQL SELECT query.
2. Execute the query ONCE.
3. DO NOT reason step-by-step in text.
4. DO NOT re-check table schemas repeatedly.
5. NEVER use INSERT, UPDATE, DELETE, DROP.
6. Return the final answer in natural language.
"""
)

if 'messages' not in st.session_state or st.sidebar.button("clear chat history"):
  st.session_state['messages']=[{'role':'assistant','content':"How can i help you?"}]

for msg in st.session_state.messages:
  st.chat_message(msg['role']).write(msg['content'])
  
user_query=st.chat_input(placeholder="Ask anything from the database")

if user_query:
  st.session_state.messages.append({'role':'user','content':user_query})
  st.chat_message('user').write(user_query)
  
  with st.chat_message('assistant'):
    streamlit_callback=StreamlitCallbackHandler(st.container())
    response=agent.run(user_query, callbacks=[streamlit_callback])
    st.session_state.messages.append({'role':'assistant','content':response})
    st.write(response)
