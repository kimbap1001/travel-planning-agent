from langchain_openai import ChatOpenAI
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import os

load_dotenv()

llm = ChatOpenAI(
    model="gpt-4o-mini",
    api_key=os.getenv("OPENAI_API_KEY")
)

search = DuckDuckGoSearchRun()

def search_and_summarize(city: str):
    search_result = search.run(f"{city} 여행 정보 관광지 최적시기 대중교통")
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "당신은 여행 전문가입니다. 검색 결과를 바탕으로 여행 정보를 요약해주세요."),
        ("user", f"도시: {city}\n\n검색 결과:\n{search_result}\n\n위 정보를 바탕으로 여행 정보를 정리해주세요.")
    ])
    
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({})

result = search_and_summarize("보스턴")
print(result)