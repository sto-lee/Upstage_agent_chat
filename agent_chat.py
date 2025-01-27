import os
from dotenv import load_dotenv
import streamlit as st
import chromadb.api
chromadb.api.client.SharedSystemClient.clear_system_cache()
from langchain import hub
from langchain_chroma import Chroma
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_community.utilities import SerpAPIWrapper
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import Tool
from langchain_upstage import ChatUpstage, UpstageEmbeddings, UpstageGroundednessCheck
from langchain.tools.retriever import create_retriever_tool
import time

# 환경 변수 로드
load_dotenv()

os.environ["SERPAPI_API_KEY"] = os.getenv("SERPAPI_API_KEY") # 구글, 네이버, 유튜브와 같은 검색 엔진을 호출 할 수 있음음
os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY") # LLM에 특화된 검색 엔진

# 문서 로드 및 벡터화
def load_and_vectorize_documents(file_path):
    pdf_loader = PyPDFLoader(file_path)
    documents = pdf_loader.load()
    vector_store = Chroma.from_documents(documents, UpstageEmbeddings(model="solar-embedding-1-large"))
    return vector_store

# 검색 엔진 설정
def setup_search_engines():
    params = {
        "engine": "google",
        "q": "Coffee",
        "hl": "ko",
    }
    serp_api = SerpAPIWrapper(params=params)
    tavily_search = TavilySearchResults()
    google_tool = Tool(
        name="google_search",
        description="Use google search engine",
        func=serp_api.run,
    )
    return serp_api, tavily_search, google_tool

# 에이전트 및 도구 생성
def create_agent(vector_store, serp_api, tavily_search, google_tool):
    retriever = vector_store.as_retriever(k=2)
    retriever_tool = create_retriever_tool(
        retriever,
        "paper_review",
        "If you read the content of the paper and ask questions related to the paper, search for it!",
    )
    chat = ChatUpstage(upstage_api_key=os.getenv("UPSTAGE_API_KEY"))
    tools = [tavily_search, retriever_tool, google_tool]
    prompt = hub.pull("hwchase17/openai-functions-agent")
    agent = create_tool_calling_agent(chat, tools, prompt)
    executor = AgentExecutor(agent=agent, tools=tools)
    return executor

# Streamlit을 통한 웹 인터페이스
def setup_streamlit_interface(executor):
    st.title("AI Chatbot with Tools")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
    if prompt := st.chat_input("Ask a question!"):
        st.chat_message("user").markdown(prompt)  # 사용자 입력 표시
        response = executor.invoke({"input": prompt, "chat_history": st.session_state.get('messages', [])})
        st.chat_message("assistant").markdown(response["output"])  # AI 응답 표시
        return prompt, response["output"]
    return None, None

# 대화 기록 관리
def manage_chat_history(prompt, response):
    MAX_MESSAGES_BEFORE_DELETION = 4
    new_session_state_messages = []

    st.session_state['messages'].append({"role": "user", "content": prompt})
    st.session_state['messages'].append({"role": "assistant", "content": response})

    # MAX_MESSAGES_BEFORE_DELETION에 맞춰 대화 기록을 유지
    if len(st.session_state['messages']) <= MAX_MESSAGES_BEFORE_DELETION:
        new_session_state_messages = st.session_state['messages']
    elif len(st.session_state['messages']) > MAX_MESSAGES_BEFORE_DELETION:
        new_session_state_messages = st.session_state['messages'][-MAX_MESSAGES_BEFORE_DELETION:]
    
    return new_session_state_messages

# Groundedness Check
def check_groundedness(new_session_state_messages):
    groundedness_checker = UpstageGroundednessCheck()
    
    # new_session_state_messages를 사용하여 context와 answer를 설정
    messages = {
        "context": new_session_state_messages[0]['content'] if len(new_session_state_messages) > 0 else "",
        "answer": new_session_state_messages[1]['content'] if len(new_session_state_messages) > 1 else ""
    }
    
    result = groundedness_checker.invoke(messages)
    print(result)
    if result == "grounded":
        st.caption('LLM이 생성한 답변은 Groundedness Check를 :blue[통과했습니다.]')
    else:
        st.caption('LLM이 생성한 답변은 Groundedness Check를 :red[통과하지 못했습니다.]')

def main():
    file_path = 'C:/Users/Playdata/Desktop/paper/solar.pdf'
    vector_store = load_and_vectorize_documents(file_path)
    serp_api, tavily_search, google_tool = setup_search_engines()
    executor = create_agent(vector_store, serp_api, tavily_search, google_tool)

    prompt, response = setup_streamlit_interface(executor)

    if prompt and response:
        new_session_state_messages =manage_chat_history(prompt, response)

        check_groundedness(new_session_state_messages)

if __name__ == "__main__":
    main()