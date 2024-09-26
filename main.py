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

        user_input = input().strip()
        
        for step in app.stream({"messages": [HumanMessage(content=user_input)]}, config, stream_mode="updates"):
            try:
                state_name = list(step.keys())[0]
                next_step = step[state_name].get('next', 'Master')
            except:
                state_name = next_step
                next_step = "Master"
            
            if state_name == "ChatAgent":
                print(step["ChatAgent"]["messages"][-1].content)

if __name__ == "__main__":
    main()