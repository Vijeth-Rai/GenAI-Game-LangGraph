from agents.graph import *
from utils.imports import *
from configs.ConfigEnv import *
from agents.MongoSaver import MongoDBSaver

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

            res = graph.stream({"messages": [("human", user_input)]}, config, stream_mode="values")
            if 'messages' in res:
                for message in res['messages']:
                    if isinstance(message, tuple) and message[0] == 'assistant':
                        print("Assistant:", message[1])


                # if "messages" in event and not isinstance(event["messages"][-1], HumanMessage):
                #     print("Assistant:", event["messages"][-1].content)
                # if "short_memory" in event:
                #     print("Short Memory:", event["short_memory"])
                # if "long_memory" in event:
                #     print("Long Memory:", event["long_memory"])
                

if __name__ == "__main__":
    main()