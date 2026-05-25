from langchain_openai import ChatOpenAI
from langchain_community.tools import DuckDuckGoSearchRun
from langgraph.prebuilt import create_react_agent
from dotenv import load_dotenv
import os

load_dotenv()

llm = ChatOpenAI(
    model="gpt-4o-mini",
    api_key=os.getenv("OPENAI_API_KEY")
)

tools = [DuckDuckGoSearchRun()]

agent = create_react_agent(
    model=llm,
    tools=tools,
    prompt="""당신은 여행 전문가 AI입니다.
도시 여행 정보를 간결하게 수집하세요:
- 주요 공항명 및 도심까지 교통/소요시간/비용
- 도심 위치, 대중교통 현황, 교통패스 및 가격
검색 1회로 모든 정보를 한번에 수집하세요."""
)

def get_city_info(city: str):
    result = agent.invoke({
        "messages": [("user", f"{city}의 공항, 도심, 대중교통 정보를 알려주세요.")]
    })
    return result["messages"][-1].content

if __name__ == "__main__":
    result = get_city_info("도쿄")
    print("\n=== 최종 결과 ===")
    print(result)