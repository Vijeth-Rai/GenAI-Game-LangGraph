from agents.graph import *
from utils.imports import *
config = {"configurable": {"thread_id": 1, "checkpointer_id": 1}}


def main():
    graph = setup_graph()

    while True:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break
        
        for event in graph.stream({"messages": [HumanMessage(content=user_input)]}, stream_mode="values"):
            if "messages" in event and not isinstance(event["messages"][-1], HumanMessage):
                print("Assistant:", event["messages"][-1].content)
            if "short_memory" in event:
                print("Short Memory:", event["short_memory"])
            if "long_memory" in event:
                print("Long Memory:", event["long_memory"])

if __name__ == "__main__":
    main()