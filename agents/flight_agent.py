import warnings
warnings.filterwarnings("ignore")

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
    prompt="""당신은 항공권 가격 검색 전문가입니다.
인천공항(ICN)에서 출발하는 항공권 정보를 검색하세요.
다음 정보를 반드시 포함하세요:
1. 왕복 항공권 평균 가격 범위
2. 비수기/성수기 가격 차이
3. 저렴하게 구매하는 팁

검색할 때 "인천 출발 [도시] 왕복 항공권 가격" 형식으로 검색하세요."""
)

def search_flight_price(city: str, budget: int):
    result = agent.invoke({
        "messages": [("user", f"""
인천공항에서 {city}까지 왕복 항공권 가격을 검색해주세요.
예산: {budget:,}원
예산 내에서 갈 수 있는지 알려주세요.
        """)]
    })
    return result["messages"][-1].content

if __name__ == "__main__":
    result = search_flight_price("도쿄", 500000)
    print("\n=== 항공권 가격 정보 ===")
    print(result)