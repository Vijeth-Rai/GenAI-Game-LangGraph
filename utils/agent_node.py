from langchain_core.messages import HumanMessage

def agent_node(state, agent, name):
    result = agent.invoke(state)
    #print("result: ", result)
    #print("state: ", state)
    if result:
        return {"messages": [HumanMessage(content=result["messages"][-1].content, name=name)]}
    else:
        pass
    