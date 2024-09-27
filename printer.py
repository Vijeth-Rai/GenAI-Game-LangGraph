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
            
            state_name = "__start__"
            next_step = "Master"
            print(f"Current State: {state_name} | Next Step: {next_step}")
            for step in app.stream({"messages": [HumanMessage(content=user_input)]}, config, stream_mode="updates"):
                try:
                    state_name = list(step.keys())[0]
                    next_step = step[state_name].get('next', 'Master')
                except:
                    state_name = next_step
                    next_step = "Master"
                
                print(state_name)
                print(next_step)
                

                if state_name == "ChatAgent":
                    print(step["ChatAgent"]["messages"][-1].content)

                else:
                    print("wait")

if __name__ == "__main__":
    main()