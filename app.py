import streamlit as st
import sqlite3
from pathlib import Path
from urllib.parse import quote_plus

from sqlalchemy import create_engine

from langchain_groq import ChatGroq
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import (
    SQLDatabaseToolkit,
    create_sql_agent,
)
from langchain_community.callbacks.streamlit import StreamlitCallbackHandler


# ------------------- Streamlit UI -------------------

st.set_page_config(
    page_title="LangChain SQL Chat",
    page_icon="🤖"
)

st.title("🤖 Chat with SQL Database")


LOCALDB = "USE_LOCALDB"
MYSQL = "USE_MYSQL"

options = [
    "Use SQLite Database (student.db)",
    "Connect to MySQL"
]

selected = st.sidebar.radio(
    "Choose Database",
    options
)

if selected == options[0]:
    db_uri = LOCALDB
else:
    db_uri = MYSQL
    mysql_host = st.sidebar.text_input("MySQL Host")
    mysql_user = st.sidebar.text_input("Username")
    mysql_password = st.sidebar.text_input(
        "Password",
        type="password"
    )
    mysql_db = st.sidebar.text_input("Database Name")

api_key = st.sidebar.text_input(
    "Groq API Key",
    type="password"
)

if not api_key:
    st.info("Enter your Groq API Key.")
    st.stop()


# ------------------- LLM -------------------

llm = ChatGroq(
    groq_api_key=api_key,
    model_name="llama-3.1-8b-instant",
    streaming=True,
)


# ------------------- Database -------------------

@st.cache_resource
def configure_db():

    if db_uri == LOCALDB:

        db_path = (
            Path(__file__).parent / "student.db"
        ).absolute()

        engine = create_engine(
            f"sqlite:///{db_path}"
        )

        return SQLDatabase(engine)

    else:

        if not (
            mysql_host
            and mysql_user
            and mysql_password
            and mysql_db
        ):
            st.error("Please enter all MySQL credentials.")
            st.stop()

        engine = create_engine(
            f"mysql+mysqlconnector://{mysql_user}:{quote_plus(mysql_password)}@{mysql_host}/{mysql_db}"
        )

        return SQLDatabase(engine)


db = configure_db()


# ------------------- Toolkit -------------------

toolkit = SQLDatabaseToolkit(
    db=db,
    llm=llm
)


agent = create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    verbose=True
)


# ------------------- Chat History -------------------

if (
    "messages" not in st.session_state
    or st.sidebar.button("Clear Chat")
):

    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hello 👋 Ask me anything about your SQL database."
        }
    ]


for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])


# ------------------- User Input -------------------

query = st.chat_input(
    "Ask a question..."
)


if query:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": query
        }
    )

    st.chat_message("user").write(query)

    with st.chat_message("assistant"):

        callback = StreamlitCallbackHandler(
            st.container()
        )

        try:

            response = agent.invoke(
                {"input": query},
                {"callbacks": [callback]}
            )

            answer = response["output"]

        except Exception as e:

            answer = str(e)

        st.write(answer)

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer
            }
        )
