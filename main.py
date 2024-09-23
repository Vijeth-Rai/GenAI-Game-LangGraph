from agents.graph import *
from utils.imports import *
from configs.ConfigEnv import *
from configs.MongoSaver import MongoDBSaver

config = {"configurable": {"thread_id": "1"}}

def main():
    with MongoDBSaver.from_conn_info(host=host, port=27017, db_name="checkpoints") as checkpointer:
        graph = setup_graph()
        graph = graph.compile(checkpointer=checkpointer)
        config = {"configurable": {"thread_id": "1"}}

        while True:
            user_input = input("User: ")
            if user_input.lower() in ["quit", "exit", "q"]:
                print("Goodbye!")
                break

            res = graph.stream({"messages": [HumanMessage(content=user_input)]}, config, stream_mode="values")
            for event in res:
                if "messages" in event and not isinstance(event["messages"][-1], HumanMessage) and event["next"] == "__end__":
                    print("Assistant: ", event["messages"][-1].content)
                    #break

if __name__ == "__main__":
    main()