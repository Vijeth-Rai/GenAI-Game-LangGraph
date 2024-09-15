from agents.chatbot import setup_graph
from utils.imports import *

def main():
    graph = setup_graph()

    while True:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break

        for event in graph.stream({"messages": [HumanMessage(content=user_input)]}):
            for value in event.values():
                if isinstance(value["messages"][-1], BaseMessage):
                    print("Assistant:", value["messages"][-1].content)

if __name__ == "__main__":
    main()