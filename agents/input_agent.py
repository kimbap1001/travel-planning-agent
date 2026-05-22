import warnings
warnings.filterwarnings("ignore")

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import os

load_dotenv()

llm = ChatOpenAI(
    model="gpt-4o-mini",
    api_key=os.getenv("OPENAI_API_KEY")
)

def analyze_input(user_input: str):
    prompt = ChatPromptTemplate.from_messages([
        ("system", """사용자의 여행 입력을 분석해서 아래 형식으로만 답하세요.

입력이 특정 도시/공항이면: CITY:도시명
입력이 나라이면: COUNTRY:나라명
입력이 지역(동남아, 유럽, 미국 등)이면: REGION:지역명

예시:
- "도쿄 가고 싶어" → CITY:도쿄
- "일본 여행" → COUNTRY:일본
- "동남아 여행" → REGION:동남아
- "유럽 여행" → REGION:유럽
- "파리" → CITY:파리

반드시 위 형식 중 하나로만 답하세요."""),
        ("user", user_input)
    ])
    
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({})

if __name__ == "__main__":
    tests = ["도쿄 가고 싶어", "일본 여행", "동남아 여행", "파리"]
    for t in tests:
        result = analyze_input(t)
        print(f"입력: {t} → {result}")