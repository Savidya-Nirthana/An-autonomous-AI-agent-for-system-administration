from utils.llm_client import LLMClient
from langchain_core.runnables import RunnableConfig
from utils.token_utils import token_guard
from utils.router_agent import create_router_agent
from utils.agents_client import AgentClient
from utils.memory_store import save_chat_memory, load_chat_memory

from cli.cli_functions import (
    # check_packages,
    welcome_banner,
    login_form,
    welcome_msg,
    get_requests,
    logout_message,
    session_info
)

from auth.auth_manager import AuthManager

# Check and install required packages
# check_packages()

# Initialize authentication manager
auth_manager = AuthManager()

# Initialize database tables (first time setup)
try:
    auth_manager.initialize()
except Exception as e:
    print(f"Database initialization error: {e}")

# Display welcome banner
welcome_banner()

# Login and create session
session_id = login_form(auth_manager)

if not session_id:
    print("Login failed. Exiting...")
    exit()

# Display welcome message
welcome_msg()

# Initialize LLM
llm = LLMClient(
    provider="google",
    model="gemini-2.0-flash-exp",
    max_retries=3,
    backoff_base=1.2,
    backoff_jitter=0.2,
    hard_prompt_cap=1024
)

# Create router agent
router = create_router_agent(llm)

# Main interaction loop
try:
    while True:
        # Validate session is still active
        if not auth_manager.validate_session(session_id):
            print("\n[Session expired. Please login again.]")
            break
        
        prompt = get_requests()
        
        # Handle exit/logout
        if not prompt:
            logout_message(auth_manager, session_id)
            break
        
        # Handle special commands
        if isinstance(prompt, bool):
            continue
        
        # Handle session info command
        if prompt.lower() == "session":
            session_info(auth_manager, session_id)
            continue
        
        # Load chat memory for this session (empty on fresh login)
        messages = load_chat_memory(session_id)
        
        # Route to appropriate agent
        decision = router.invoke({
            "messages": [{"role": "user", "content": prompt}], 
            "session_id": session_id
        })
        
        decision = decision["structured_response"]
        agent = decision.agent
        reason = decision.reason
        
        # Create and configure agent
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
        
        # Process request
        messages.append({"role": "user", "content": prompt})
        response = guarded_agent.invoke({
            "messages": messages, 
            "session_id": session_id
        }, config=config)
        
        response = response["messages"][-1].content
        print(response)
        
        # Save conversation to session memory
        messages.append({"role": "assistant", "content": response})
        save_chat_memory(session_id, messages)

except KeyboardInterrupt:
    print("\n\n[Session interrupted by user]")
    logout_message(auth_manager, session_id)
except Exception as e:
    print(f"\n[Error: {e}]")
    logout_message(auth_manager, session_id)
finally:
    # Cleanup
    auth_manager.close()