from agents.graph import *
from utils.imports import *
from configs.ConfigEnv import *
from configs.MongoSaver import MongoDBSaver

config = {"configurable": {"thread_id": "1"}}

def main():
    with MongoDBSaver.from_conn_info(host=host, port=27017, db_name="checkpoints") as checkpointer:
        graph = setup_graph()
        app = graph.compile(checkpointer=checkpointer)
        config = {"configurable": {"thread_id": "1"}}

        while True:
            user_input = input("User: ")
            if user_input.lower() in ["quit", "exit", "q"]:
                print("Goodbye!")
                break

            for step in app.stream({"messages": [HumanMessage(content=user_input)]}, config):
                #print(step)
                if "messages" in step and not isinstance(step["messages"][-1], HumanMessage) and step["next"] == "__end__":
                    print("Assistant: ", step["messages"][-1].content)
                    #break



if __name__ == "__main__":
    main()