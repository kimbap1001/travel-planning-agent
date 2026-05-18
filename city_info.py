from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import os

load_dotenv()

llm = ChatOpenAI(
    model="gpt-4o-mini",
    api_key=os.getenv("OPENAI_API_KEY")
)

prompt = ChatPromptTemplate.from_messages([
    ("system", "당신은 여행 전문가입니다. 도시에 대한 정보를 친절하게 알려주세요."),
    ("user", "{city}에 대해 알려주세요. 최적 여행 시기, 주요 관광지, 여행 팁을 포함해주세요.")
])

chain = prompt | llm

response = chain.invoke({"city": "도쿄"})
print(response.content)