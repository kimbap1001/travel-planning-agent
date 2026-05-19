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
    prompt="""당신은 여행 장소 전문가 AI입니다.
주어진 도시에서 방문할만한 장소들을 수집하세요.
각 장소에 대해 다음 정보를 포함하세요:
1. 장소 이름
2. 어떤 곳인지 간단한 설명
3. 도심에서의 위치/거리
4. 대중교통 접근 가능 여부
5. 예약 필요 여부
6. 실내/야외 여부 (날씨 영향 받는지)

반드시 검색을 통해 정확한 정보를 수집하세요."""
)

def get_places(city: str):
    result = agent.invoke({
        "messages": [("user", f"{city}에서 방문할만한 장소 10곳을 알려주세요.")]
    })
    return result["messages"][-1].content

if __name__ == "__main__":
    result = get_places("도쿄")
    print("\n=== 추천 장소 ===")
    print(result)