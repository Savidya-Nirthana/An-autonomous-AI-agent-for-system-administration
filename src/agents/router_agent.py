from langchain_core.output_parsers import PydanticOutputParser
from schema.routing_schema import RoutingDecision
from src.agents.prompts.router_agent.router_agent import router_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage


def create_router_agent(llm):
    parser = PydanticOutputParser(pydantic_object=RoutingDecision)

    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content=router_agent + "\n\n" + parser.get_format_instructions()),
        ("user", "{input}")
    ])

    router_chain = prompt | llm | parser
    
    return router_chain