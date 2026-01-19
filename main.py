from utils.llm_client import LLMClient
from langchain_core.runnables import RunnableConfig
from utils.token_utils import token_guard
from utils.router_agent import create_router_agent
from utils.agents_client import AgentClient
from utils.memory_store import save_chat_memory, load_chat_memory
from cli.networking import show_default_gateway_ui
from core.tool_parser import extract_tool_ui
from core.tool_router_ui import render_ui

from cli.cli_functions import (
    welcome_banner,
    login_form,
    welcome_msg,
    get_requests,
    pending_message

)

welcome_banner()
session_id = login_form()

if not session_id:
    exit()


welcome_msg()

llm = LLMClient(
    provider="google",
    model="gemini-2.0-flash-exp",
    max_retries=3,
    backoff_base=1.2,
    backoff_jitter=0.2,
    hard_prompt_cap=1024
)


with pending_message("Initializing..."):
    router = create_router_agent(llm)


while True:
    prompt = get_requests()
    
    if prompt == "":  
        print("Please enter a valid request")
        continue
    elif not prompt: break

    messages = load_chat_memory(session_id)

    with pending_message("Routing..."):
        decision = router.invoke({"messages": [{"role": "user", "content": prompt}], "session_id" : session_id})

    decision = decision["structured_response"]
    agent = decision.agent
    reason = decision.reason

    agent_client = AgentClient(llm, agent)
    agent = agent_client.create_agent()


    guarded_agent = token_guard(
        agent,
        provider=llm.provider,
        model_name=llm.model,
        hard_prompt_cap=llm.hard_prompt_cap
    )



    config = RunnableConfig(
        max_retries=llm.max_retries,
    )
    messages.append({"role": "user", "content": prompt})

    response = guarded_agent.invoke({"messages": messages, "session_id" : session_id}, config=config)


    tool_ui = extract_tool_ui(response["messages"])

    if tool_ui:
        render_ui(tool_ui)

    response = response["messages"][-1].content
    print(response)
    messages.append({"role": "assistant", "content": response})
    save_chat_memory(session_id, messages)



