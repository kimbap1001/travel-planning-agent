from langchain_openai import ChatOpenAI
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.agents import create_agent as create_react_agent
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
주어진 도시에 대해 다음 정보를 수집하세요:
1. 주요 공항 이름
2. 공항에서 도심까지 교통수단, 소요시간, 비용
3. 도심이 어디인지 (예: 뉴욕의 경우 맨해튼)
4. 대중교통 현황 (지하철/버스 발달 여부)
5. 교통 패스 종류 및 가격

반드시 검색을 통해 정확한 정보를 수집하세요."""
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