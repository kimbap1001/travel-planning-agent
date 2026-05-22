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
    prompt="""당신은 여행 도시 추천 전문가입니다.
나라 또는 지역이 입력되면 한국인 여행자들에게 인기 있는 도시들을 찾아주세요.
각 도시에 대해 다음 정보를 포함하세요:
1. 도시 이름
2. 해당 도시의 주요 공항 코드 (예: TYO, BKK)
3. 도시의 특징 한 줄 설명

가격 정보는 포함하지 마세요."""
)

def find_cities(location: str):
    result = agent.invoke({
        "messages": [("user", f"{location}의 한국인 여행자들에게 인기 있는 도시 5곳을 알려주세요.")]
    })
    return result["messages"][-1].content

if __name__ == "__main__":
    print("\n=== 일본 인기 도시 ===")
    print(find_cities("미국"))
    
    print("\n=== 동남아 인기 도시 ===")
    print(find_cities("유럽"))