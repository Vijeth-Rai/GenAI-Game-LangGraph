from agents.graph import *
from utils.imports import *
from configs.ConfigEnv import *
from configs.MongoSaver import MongoDBSaver
import sys

config = {"configurable": {"thread_id": "1"}}

def main():
    with MongoDBSaver.from_conn_info(host=host, port=27017, db_name="checkpoints") as checkpointer:
        graph = setup_graph()
        app = graph.compile(checkpointer=checkpointer)
        config = {"configurable": {"thread_id": "1"}}

        user_input = sys.stdin.readline().strip()
        
        state_name = "__start__"
        next_step = "Master"

        for step in app.stream({"messages": [HumanMessage(content=user_input)]}, config, stream_mode="updates"):
            print(state_name)
            print(next_step)
            
            try:
                state_name = list(step.keys())[0]
                next_step = step[state_name].get('next', 'Master')
            except:
                state_name = next_step
                next_step = "Master"
            
            if state_name == "ChatAgent":
                message = step["ChatAgent"]["messages"][-1].content
                message = message.replace("\n", "\n\n\n")
            else:
                message = "wait"


            
            print(message)
            sys.stdout.flush()

if __name__ == "__main__":
    main()