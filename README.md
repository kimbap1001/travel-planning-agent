# ✈️ Travel Planning AI Agent

An AI-powered travel planning agent built with **LangChain** and **LangGraph** that automates the entire trip planning process — from flight price research to day-by-day itinerary generation.

> **Motivation**: I used to spend hours manually searching for flight prices, researching cities, and building itineraries on Google Maps. This agent automates that entire workflow.

---

## 🎯 What It Does

Give it a natural language input like:

```
"도쿄 10월말 5일 50만원으로 가고싶어"
```

And it will automatically:

1. **Analyze your input** — extract destination, travel month, duration, and budget
2. **Search flight prices** — find round-trip fares from Incheon (ICN)
3. **Check budget** — compare flight cost against your budget
4. **Collect city info** — airport, city center location, transit options, and travel passes
5. **Find places** — top attractions with location, transit access, indoor/outdoor, and reservation info
6. **Build an itinerary** — geographically clustered day-by-day schedule
7. **Validate the plan** — auto-regenerate if daily stops exceed 4 or locations are geographically spread out

---

## 🏗️ Architecture

```
User Input (natural language)
        ↓
   input_agent          → Extracts TYPE / DESTINATION / MONTH / DAYS / BUDGET
        ↓
  [Branch: CITY / COUNTRY / REGION]
        ↓                     ↓
  flight_agent         cities_agent → flight_agent
        ↓
  Budget Check
  ├─ Within budget → Travel Planning Pipeline
  └─ Over budget   → Notify user

Travel Planning Pipeline:
  city_agent → places_agent → schedule_agent → validate
                                                  ↓
                                          [Loop if invalid]
                                                  ↓
                                           Final Itinerary
```

---

## 🤖 Agents

| Agent | Type | Description |
|---|---|---|
| `input_agent` | LangChain Chain | Parses natural language input into structured fields |
| `cities_agent` | LangChain Chain | Finds popular cities for a given country or region |
| `flight_agent` | ReAct Agent | Searches round-trip flight prices from ICN via DuckDuckGo |
| `city_agent` | ReAct Agent | Collects airport, city center, and transit pass info |
| `places_agent` | ReAct Agent | Finds top attractions with transit/reservation/weather details |
| `schedule_agent` | ReAct Agent | Builds day-by-day itinerary with geographic clustering |

---

## 🔄 LangGraph Features Used

- **Multi-agent pipeline** — 6 specialized agents connected via shared state
- **Conditional edges** — branch by input type (city/country/region) and budget result
- **Validation loop** — schedule is auto-regenerated if it fails quality checks (max 3 retries)

---

## 🛠️ Tech Stack

- **LangChain** — Prompt templates, chains, ReAct agents
- **LangGraph** — Multi-agent workflow with conditional branching and loops
- **OpenAI GPT-4o-mini** — LLM backbone
- **DuckDuckGo Search** — Real-time web search (no API key required)
- **Python** — Core language

---

## 📁 Project Structure

```
travel-planning-agent/
├── agents/
│   ├── input_agent.py      # Natural language input parser
│   ├── cities_agent.py     # Country/region → popular cities
│   ├── flight_agent.py     # Flight price search
│   ├── city_agent.py       # City info collector
│   ├── places_agent.py     # Attractions finder
│   └── schedule_agent.py   # Itinerary builder
├── graph/
│   └── travel_graph.py     # LangGraph pipeline (full workflow)
├── .env                    # API keys (not committed)
├── .gitignore
└── README.md
```

---

## 🚀 Getting Started

**1. Clone the repo**
```bash
git clone https://github.com/kimbap1001/travel-planning-agent.git
cd travel-planning-agent
```

**2. Create virtual environment**
```bash
py -m venv venv
source venv/Scripts/activate  # Windows (Git Bash)
```

**3. Install dependencies**
```bash
pip install langchain langchain-openai langchain-community langgraph python-dotenv ddgs
```

**4. Set up API key**
```
# .env
OPENAI_API_KEY=your_openai_api_key
```

**5. Run**
```bash
py -m graph.travel_graph
```

**6. Type your travel plan — and grab a coffee! ☕**

The agent will ask you to enter your travel plan in natural language:
```bash
✈️  여행 플래닝 AI 에이전트
예시: 도쿄 10월말 5일 50만원으로 가고싶어
예시: 9월에 미국 가고싶은데 예산은 150만원, 10박이야
예시: 동남아 여행 가고싶어
여행 계획을 입력하세요:
```
The agent will then automatically search for flights, collect city information, find attractions, and build a full day-by-day itinerary. This takes 2–3 minutes, so sit back and relax!


---

## 🔮 Future Improvements

- [ ] Real-time flight prices via Tequila (Kiwi.com) API
- [ ] FastAPI backend + React frontend for web deployment
- [ ] Multi-city trip planning
- [ ] Hotel and accommodation search
- [ ] Weather-aware scheduling

---

## 👤 Author

**Cheonil Kim (Wayne)** — [github.com/kimbap1001](https://github.com/kimbap1001)
