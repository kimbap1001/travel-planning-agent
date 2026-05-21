from langgraph.graph import StateGraph, END
from typing import TypedDict
from agents.city_agent import get_city_info
from agents.places_agent import get_places
from agents.schedule_agent import create_schedule

# 상태 정의 (에이전트들이 공유하는 데이터)
class TravelState(TypedDict):
    city: str          # 여행 도시
    days: int          # 여행 기간
    city_info: str     # city_agent 결과
    places: str        # places_agent 결과
    schedule: str      # schedule_agent 결과

# 각 노드 (에이전트) 정의
def node_city_info(state: TravelState):
    print(f"\n🏙️ [1/3] {state['city']} 도시 정보 수집 중...")
    result = get_city_info(state["city"])
    return {"city_info": result}

def node_places(state: TravelState):
    print(f"\n📍 [2/3] {state['city']} 장소 수집 중...")
    result = get_places(state["city"])
    return {"places": result}

def node_schedule(state: TravelState):
    print(f"\n📅 [3/3] {state['days']}일 일정 생성 중...")
    result = create_schedule(state["city"], state["days"], state["places"])
    return {"schedule": result}

# 그래프 구성
graph = StateGraph(TravelState)

# 노드 추가
graph.add_node("city_info", node_city_info)
graph.add_node("places", node_places)
graph.add_node("schedule", node_schedule)

# 엣지 연결 (흐름 정의)
graph.set_entry_point("city_info")
graph.add_edge("city_info", "places")
graph.add_edge("places", "schedule")
graph.add_edge("schedule", END)

# 그래프 컴파일
app = graph.compile()

def plan_travel(city: str, days: int):
    result = app.invoke({
        "city": city,
        "days": days,
        "city_info": "",
        "places": "",
        "schedule": ""
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