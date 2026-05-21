import warnings
warnings.filterwarnings("ignore")

from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from typing import TypedDict
from agents.city_agent import get_city_info
from agents.places_agent import get_places
from agents.schedule_agent import create_schedule
from dotenv import load_dotenv
import os

load_dotenv()

llm = ChatOpenAI(
    model="gpt-4o-mini",
    api_key=os.getenv("OPENAI_API_KEY")
)

class TravelState(TypedDict):
    city: str
    days: int
    city_info: str
    places: str
    schedule: str
    validation: str
    retry_count: int

def node_city_info(state: TravelState):
    print(f"\n🏙️ [1/4] {state['city']} 도시 정보 수집 중...")
    result = get_city_info(state["city"])
    return {"city_info": result}

def node_places(state: TravelState):
    print(f"\n📍 [2/4] {state['city']} 장소 수집 중...")
    result = get_places(state["city"])
    return {"places": result}

def node_schedule(state: TravelState):
    retry = state.get("retry_count", 0)
    if retry > 0:
        print(f"\n📅 [3/4] 일정 재생성 중... (시도 {retry+1}회)")
    else:
        print(f"\n📅 [3/4] {state['days']}일 일정 생성 중...")
    result = create_schedule(state["city"], state["days"], state["places"])
    return {"schedule": result}

def node_validate(state: TravelState):
    print(f"\n✅ [4/4] 일정 검증 중...")
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """당신은 여행 일정 검증 전문가입니다.
아래 기준으로 일정을 검증하세요:
1. 하루 최대 4곳 이내인가?
2. 지리적으로 가까운 장소들이 같은 날에 배치되어 있는가?

문제가 있으면 RETRY, 없으면 OK 중 하나만 답하세요."""),
        ("user", f"일정:\n{state['schedule']}")
    ])
    
    chain = prompt | llm | StrOutputParser()
    result = chain.invoke({})
    
    if "RETRY" in result:
        print("⚠️ 일정 검증 실패 → 재생성")
        return {"validation": "RETRY", "retry_count": state.get("retry_count", 0) + 1}
    
    print("✅ 일정 검증 통과!")
    return {"validation": "OK"}

def should_retry(state: TravelState):
    if state["validation"] == "RETRY" and state.get("retry_count", 0) < 3:
        return "schedule"
    return END

# 그래프 구성
graph = StateGraph(TravelState)

graph.add_node("city_info", node_city_info)
graph.add_node("places", node_places)
graph.add_node("schedule", node_schedule)
graph.add_node("validate", node_validate)

graph.set_entry_point("city_info")
graph.add_edge("city_info", "places")
graph.add_edge("places", "schedule")
graph.add_edge("schedule", "validate")
graph.add_conditional_edges(
    "validate",
    should_retry,
    {
        "schedule": "schedule",
        END: END
    }
)

app = graph.compile()

def plan_travel(city: str, days: int):
    result = app.invoke({
        "city": city,
        "days": days,
        "city_info": "",
        "places": "",
        "schedule": "",
        "validation": "",
        "retry_count": 0
    })
    return result

if __name__ == "__main__":
    result = plan_travel("도쿄", 5)
    
    print("\n" + "="*50)
    print("🏙️ 도시 정보")
    print("="*50)
    print(result["city_info"])
    
    print("\n" + "="*50)
    print("📍 추천 장소")
    print("="*50)
    print(result["places"])
    
    print("\n" + "="*50)
    print("📅 최종 여행 일정")
    print("="*50)
    print(result["schedule"])