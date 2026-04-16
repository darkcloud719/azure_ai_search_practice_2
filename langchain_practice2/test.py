import os
from dotenv import load_dotenv

from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain.agents import create_agent
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_core.messages import HumanMessage

load_dotenv()

llm = AzureChatOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_API_ENDPOINT"),
    deployment_name=os.getenv("AZURE_OPENAI_API_DEPLOYMENT_4O"),
    openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    openai_api_key=os.getenv("AZURE_OPENAI_API_KEY")
)

@tool
def get_weather(city: str) -> str:
    """Get current weather of a city."""
    fake_weather = {
        "Taipei": "Rainy, 25°C",
        "Tokyo": "Sunny, 28°C",
        "London": "Cloudy, 18°C"
    }
    return fake_weather.get(city, f"No weather data for {city}.")


@tool
def calculator(expression: str) -> str:
    """Evaluate math expression like 12*8"""
    try:
        return str(eval(expression))
    
    except:
        return "Invalid expression"
    
tools = [get_weather, calculator]


agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt="""
You are a helpful assistant.

Rules:
- Use get_weather when user asks about weather.
- Use calculator when user asks math.
- Use chat history to understand context.
"""
)

def get_session_history(session_id: str):
    return SQLChatMessageHistory(
        session_id=session_id,
        connection_string="sqlite:///chat_memory4.db"
    )


agent_with_memory = RunnableWithMessageHistory(
    agent,
    get_session_history,
    input_messages_key="messages",
    history_messages_key="history"
)


def chat():
    session_id = "user-1"

    print("🤖 AI Agent ready! Type 'exit' to quit.\n")

    while True:

        user_input = input("You: ")

        if user_input.lower() in ["exit", "quit"]:
            print("Bye 👋")
            break

        result = agent_with_memory.invoke(
            {"messages": [HumanMessage(content=user_input)]},
            config={"configurable": {"session_id": session_id}}
        )

        answer = result["messages"][-1].content
        print("AI:",answer)
        print()

if __name__ == "__main__":
    chat()
