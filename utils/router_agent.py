from langchain.agents import create_agent
from langchain_core.output_parsers import PydanticOutputParser
from utils.routing_schema import RoutingDecision



def create_router_agent(llm):
    parser = PydanticOutputParser(pydantic_object=RoutingDecision)
    
    system_prompt = f"""
You are a routing agent.
Your job is to decide which agent should handle the task.

Agents:
- filesystem → creating files, folders, reading/writing files
- admin → system operations, setup, configuration
- general → anything else

Respond ONLY in the required JSON format.

{parser.get_format_instructions()}"""

    return create_agent(
        model=llm.client,
        tools=[],
        system_prompt=system_prompt,
        response_format=RoutingDecision
    )