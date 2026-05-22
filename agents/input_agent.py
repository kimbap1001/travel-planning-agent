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

TYPE: CITY, COUNTRY, REGION 중 하나
DESTINATION: 목적지 이름
BUDGET: 예산 (숫자만, 없으면 NONE)

예시:
- "도쿄 50만원으로 가고싶어" → TYPE:CITY / DESTINATION:도쿄 / BUDGET:500000
- "일본 여행 80만원" → TYPE:COUNTRY / DESTINATION:일본 / BUDGET:800000
- "동남아 여행" → TYPE:REGION / DESTINATION:동남아 / BUDGET:NONE
- "파리 가고싶어" → TYPE:CITY / DESTINATION:파리 / BUDGET:NONE

반드시 위 형식으로만 답하세요."""),
        ("user", user_input)
    ])
    
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({})

if __name__ == "__main__":
    tests = [
    "도쿄 50만원으로 가고싶어",
    "일본 여행 80만원",
    "동남아 여행",
    "파리 가고싶어"
    ]
    for t in tests:
        result = analyze_input(t)
        print(f"입력: {t} → {result}")