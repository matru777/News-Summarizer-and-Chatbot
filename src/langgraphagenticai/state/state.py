from typing_extensions import TypedDict,List,NotRequired
from langgraph.graph.message import add_messages
from typing import Annotated



class State(TypedDict, total=False):
    messages: Annotated[List, add_messages]
    genre: NotRequired[str]