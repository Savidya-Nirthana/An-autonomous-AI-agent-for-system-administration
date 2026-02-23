from langchain_core.runnables import RunnableConfig
from utils.token_utils import token_guard
from src.agents.router_agent import create_router_agent
from src.agents import AgentClient
from utils.memory_store import save_chat_memory, load_chat_memory
from cli.networking import show_default_gateway_ui
from core.tool_parser import extract_tool_ui
from core.tool_router_ui import render_ui
from src.infrastructure.llm import get_router_llm, get_chat_llm

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



router_llm = get_router_llm()
chat_llm = get_chat_llm()

with pending_message("Initializing..."):
    router = create_router_agent(router_llm)


set_pending = False
tool_ui = {}
while True:
    prompt = get_requests(session_id)
    
    if prompt == "":  
        print("Please enter a valid request")
        continue
    elif not prompt: break

    with pending_message("Routing..."):
        if set_pending:
            pending_prompt = f"""
                CONTEXT: You previously paused to ask the user a question.
                YOUR QUESTION: "{tool_ui[0].get("question", "")}"
                USER ANSWER: "{prompt}"

                INSTRUCTION: Proceed with the task using this new information.
            """
            decision = router.invoke({"messages": [{"role": "user", "content": pending_prompt}]})
        else:
            decision = router.invoke({ "input": prompt})
    


    with pending_message("Loading Memory..."):
        messages = load_chat_memory(session_id, prompt)


    agent = decision.agent
    reason = decision.reason

    agent_client = AgentClient(chat_llm, agent)
    agent = agent_client.create_agent()


    guarded_agent = token_guard(
        agent,
        provider="google",
        model_name="gemini-2.5-flash",
        hard_prompt_cap=4096
    )



    config = RunnableConfig(
        max_retries=3,
        configurable={
        "session_id": session_id,
        }
    )

    if not messages:
        messages = [{"role": "user", "content": prompt}]
    else:
        messages.append({"role": "user", "content": prompt})    
    
    response = guarded_agent.invoke({"messages": messages}, config=config)


    tool_ui = extract_tool_ui(response["messages"])

    if tool_ui:
        render_ui(tool_ui)

    if isinstance(tool_ui, list) and tool_ui:
        if tool_ui[0].get("pending", False):
            set_pending = True
        else:
            set_pending = False
    else:
        set_pending = False

    response = response["messages"][-1].content
    print(response)
    messages.append({"role": "assistant", "content": response})
    user_message = prompt
    assistant_message = response
    save_chat_memory(session_id, user_message, assistant_message)



