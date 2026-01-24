from langchain.agents import create_agent
from langchain_core.output_parsers import PydanticOutputParser
from schema.routing_schema import RoutingDecision
from prompts.router_agent.router_agent import router_agent



def create_router_agent(llm):
    parser = PydanticOutputParser(pydantic_object=RoutingDecision)
    
    system_prompt = f"""{router_agent}

{parser.get_format_instructions()}
"""

    return create_agent(
        model=llm.client,
        tools=[],
        system_prompt=system_prompt,
        response_format=RoutingDecision
    )