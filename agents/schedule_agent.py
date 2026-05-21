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
    prompt="""당신은 여행 일정 전문가 AI입니다.
주어진 장소 목록을 지리적 위치 기준으로 묶어서 날짜별 일정을 짜세요.

규칙:
1. 지리적으로 가까운 장소들을 같은 날에 배치
2. 하루에 최대 4곳까지만 배치 (무리한 일정 금지)
3. 예약 필요한 장소는 일정 앞쪽에 배치
4. 야외 장소는 날씨 좋은 날 우선 배치, 실내는 유동적으로
5. 오전/오후/저녁으로 나눠서 동선 최적화

반드시 검색을 통해 각 장소의 실제 위치를 확인하세요."""
)

def create_schedule(city: str, days: int, places: str):
    result = agent.invoke({
        "messages": [("user", f"""
도시: {city}
여행 기간: {days}일
장소 목록:
{places}

위 장소들을 {days}일 일정으로 짜주세요.
각 날짜별로 오전/오후/저녁으로 나눠주세요.
예약 필요한 곳과 날씨에 따라 유동적으로 바꿀 수 있는 곳도 표시해주세요.
        """)]
    })
    return result["messages"][-1].content

if __name__ == "__main__":
    # 테스트용 장소 목록
    places = """
1. 센소지 사원 - 야외, 예약 불필요, 아사쿠사
2. 도쿄 스카이트리 - 실내/야외, 예약 가능, 아사쿠사 근처
3. 메이지 신궁 - 야외, 예약 불필요, 하라주쿠
4. 하라주쿠 - 야외, 예약 불필요, 하라주쿠
5. 우에노 공원 - 야외, 예약 불필요, 우에노
6. 도쿄 국립박물관 - 실내, 예약 가능, 우에노
7. 츠키지 수산시장 - 야외, 예약 불필요, 츠키지
8. 팀랩 보더리스 - 실내, 예약 필요, 오다이바
9. 롯폰기 힐스 - 실내/야외, 예약 가능, 롯폰기
10. 도쿄 타워 - 실내/야외, 예약 가능, 롯폰기 근처
    """
    
    result = create_schedule("도쿄", 5, places)
    print("\n=== 5일 여행 일정 ===")
    print(result)