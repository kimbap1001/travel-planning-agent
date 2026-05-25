import warnings
warnings.filterwarnings("ignore")

from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from typing import TypedDict, Optional
from agents.city_agent import get_city_info
from agents.places_agent import get_places
from agents.schedule_agent import create_schedule
from agents.input_agent import analyze_input
from agents.flight_agent import search_flight_price
from agents.cities_agent import find_cities
from dotenv import load_dotenv
import os

load_dotenv()

llm = ChatOpenAI(
    model="gpt-4o-mini",
    api_key=os.getenv("OPENAI_API_KEY")
)

# State 정의
class TravelState(TypedDict):
    user_input: str
    input_type: str
    destination: str
    month: str
    days: int
    budget: int
    candidate_cities: str
    flight_info: str
    city: str
    city_info: str
    places: str
    schedule: str
    validation: str
    retry_count: int

# 입력 분석 노드
def node_analyze_input(state: TravelState):
    print(f"\n🔍 입력 분석 중...")
    result = analyze_input(state["user_input"])
    
    # 파싱
    lines = result.split(" / ")
    parsed = {}
    for line in lines:
        key, val = line.split(":")
        parsed[key.strip()] = val.strip()
    
    input_type = parsed.get("TYPE", "CITY")
    destination = parsed.get("DESTINATION", "")
    month = parsed.get("MONTH", "NONE")
    days = parsed.get("DAYS", "NONE")
    budget = parsed.get("BUDGET", "NONE")

    print(f"  → 유형: {input_type}, 목적지: {destination}, 월: {month}, 기간: {days}일, 예산: {budget}원")

    return {
        "input_type": input_type,
        "destination": destination,
        "month": month,
        "days": int(days) if days != "NONE" else 0,
        "budget": int(budget) if budget != "NONE" else 0,
        "city": destination if input_type == "CITY" else ""
    }

# 도시 목록 찾기 노드 (COUNTRY/REGION일 때)
def node_find_cities(state: TravelState):
    print(f"\n🌍 {state['destination']} 인기 도시 검색 중...")
    result = find_cities(state["destination"])
    print(result)
    return {"candidate_cities": result}

# 항공권 검색 노드
def node_flight_search(state: TravelState):
    city = state["city"] if state["city"] else state["destination"]
    month = state["month"] if state["month"] != "NONE" else "전체"
    budget = state["budget"]
    
    print(f"\n✈️ {city} 항공권 가격 검색 중... (월: {month})")
    result = search_flight_price(city, budget)
    print(result)
    return {"flight_info": result}

# 예산 검증 노드
def node_check_budget(state: TravelState):
    if state["budget"] == 0:
        print(f"\n💰 예산 미설정 → 가격 안내 후 플래닝 시작")
        return {"validation": "NO_BUDGET"}
    
    print(f"\n💰 예산 {state['budget']:,}원 검증 중...")
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """항공권 가격 정보와 예산을 비교하세요.
예산 내에서 가능하면 OK, 불가능하면 OVER라고만 답하세요."""),
        ("user", f"""예산: {state['budget']:,}원
항공권 정보: {state['flight_info'][:200]}

예산 내 가능한가요? OK 또는 OVER로만 답하세요.""")
    ])
    
    chain = prompt | llm | StrOutputParser()
    result = chain.invoke({})
    
    if "OVER" in result:
        print(f"  → 예산 초과!")
        return {"validation": "OVER"}
    
    print(f"  → 예산 내 가능!")
    return {"validation": "OK"}

# 도시 정보 수집 노드
def node_city_info(state: TravelState):
    print(f"\n🏙️ {state['city']} 도시 정보 수집 중...")
    result = get_city_info(state["city"])
    return {"city_info": result}

# 장소 수집 노드
def node_places(state: TravelState):
    print(f"\n📍 {state['city']} 장소 수집 중...")
    result = get_places(state["city"])
    return {"places": result}

# 일정 생성 노드
def node_schedule(state: TravelState):
    retry = state.get("retry_count", 0)
    days = state["days"] if state["days"] > 0 else 5
    if retry > 0:
        print(f"\n📅 일정 재생성 중... (시도 {retry+1}회)")
    else:
        print(f"\n📅 {days}일 일정 생성 중...")
    result = create_schedule(state["city"], days, state["places"])
    return {"schedule": result}

# 일정 검증 노드
def node_validate(state: TravelState):
    print(f"\n✅ 일정 검증 중...")
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """일정 검증: 하루4곳이하+지리적근접여부. RETRY또는OK로만답하세요."""),
        ("user", f"일정:\n{state['schedule']}")
    ])
    
    chain = prompt | llm | StrOutputParser()
    result = chain.invoke({})
    
    if "RETRY" in result:
        print("⚠️ 일정 검증 실패 → 재생성")
        return {"validation": "RETRY", "retry_count": state.get("retry_count", 0) + 1}
    
    print("✅ 일정 검증 통과!")
    return {"validation": "OK"}

# 예산 초과 안내 노드
def node_budget_exceeded(state: TravelState):
    print(f"\n❌ 예산 초과 안내")
    print(f"{state['destination']} 항공권이 예산 {state['budget']:,}원을 초과합니다.")
    print(f"항공권 정보: {state['flight_info']}")
    return {}

def node_merge(state: TravelState):
    # city_agent랑 places_agent 결과가 둘 다 모이면 통과
    return {}

# 분기 함수들
def route_by_type(state: TravelState):
    if state["input_type"] == "CITY":
        return "flight_search"
    else:
        return "find_cities"

def route_by_budget(state: TravelState):
    if state["validation"] in ("NO_BUDGET", "OK"):
        return ["city_info", "places"]  # 동시 실행
    else:
        return "budget_exceeded"

def route_validate(state: TravelState):
    if state["validation"] == "RETRY" and state.get("retry_count", 0) < 3:
        return "schedule"
    return END

# 그래프 구성
graph = StateGraph(TravelState)

# 노드 추가
graph.add_node("analyze_input", node_analyze_input)
graph.add_node("find_cities", node_find_cities)
graph.add_node("flight_search", node_flight_search)
graph.add_node("check_budget", node_check_budget)
graph.add_node("budget_exceeded", node_budget_exceeded)
graph.add_node("city_info", node_city_info)
graph.add_node("places", node_places)
graph.add_node("merge", node_merge)  # 추가
graph.add_node("schedule", node_schedule)
graph.add_node("validate", node_validate)

# 엣지 연결
graph.set_entry_point("analyze_input")
graph.add_conditional_edges("analyze_input", route_by_type, {
    "flight_search": "flight_search",
    "find_cities": "find_cities"
})
graph.add_edge("find_cities", "flight_search")
graph.add_edge("flight_search", "check_budget")
graph.add_conditional_edges("check_budget", route_by_budget, {
    "city_info": "city_info",
    "places": "places",
    "budget_exceeded": "budget_exceeded"
})
graph.add_edge("budget_exceeded", END)

# fan-in: 둘 다 끝나면 merge로 합류
graph.add_edge("city_info", "merge")
graph.add_edge("places", "merge")
graph.add_edge("merge", "schedule")

graph.add_edge("schedule", "validate")
graph.add_conditional_edges("validate", route_validate, {
    "schedule": "schedule",
    END: END
})

app = graph.compile()

def plan_travel(user_input: str):
    result = app.invoke({
        "user_input": user_input,
        "input_type": "",
        "destination": "",
        "month": "NONE",
        "days": 0,
        "budget": 0,
        "candidate_cities": "",
        "flight_info": "",
        "city": "",
        "city_info": "",
        "places": "",
        "schedule": "",
        "validation": "",
        "retry_count": 0
    })
    return result

if __name__ == "__main__":
    print("✈️  여행 플래닝 AI 에이전트")
    print("=" * 50)
    print("예시: 도쿄 10월말 5일 50만원으로 가고싶어")
    print("예시: 9월에 미국 가고싶은데 예산 150만원 10박이야")
    print("예시: 동남아 여행 가고싶어")
    print("=" * 50)
    
    user_input = input("\n여행 계획을 입력하세요: ")
    result = plan_travel(user_input)
    
    if result["schedule"]:
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