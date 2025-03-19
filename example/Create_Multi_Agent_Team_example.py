from MultiAgentComponents import AgentNode
from LLMs import Kimi_LLM, ZhiPu_LLM, Qwen_LLM, DouBao_LLM
from AgentTools import Plus,Sub,Mul,Div

'''
AgentNode is also easy-used.
create llm, put llm into AgentNode class, load tool_list into AgentNode, and call the agent.
It will execute the tool automatically.

The AgentNode is only a node but not in any graph,
because I hope the AgentNode is the same friendly-used as the numpy.ndarray and torch.Tensor
So that you can use the python's key word 'if', 'while', 'for' and so on to construct complex workflow. 

use this AgentNode
- you can input something from your keyboard to communicate to AI when the workflow is working
- you can input other agent's output to AI when the workflow is working
Details see the original code in 'MultiAgentComponents.py'

I think the best program-friendly module design is to only provide preliminary module having short code but strong ability, 
hide the trivial API call details, keep the raw python programming style   
and simplify the use of module without losing the way for other programmer to change the module.

"never gauss what the user will do, only give them the LOGO and stimulating their creativity!"

'''


if __name__ == '__main__':
    temperature = 0.5

    file = 'example/test_str_File/testFile_self_introduction.json'

    # initiate the llm 1 as agent 1
    llm1 = Kimi_LLM(
        temperature,
        llm_model_version='moonshot-v1-32k',
        api_key='sk-qLRDFWbDyOLXs9XUchQ2lsNiKegguW4nWxV8Jq8ohfOMCaEV',
        agent_name="John",
        agent_identity="a romantic man",
    )

    # initiate the llm 2 as agent 2
    llm2 = ZhiPu_LLM(
        temperature,
        llm_model_version='glm-4',
        api_key='38f65f59c6164d92b79ba64891557439.gSjelejfFaagMHAm',
        agent_name="Alice",
        agent_identity="a beautiful gril",
    )

    llm3 = Qwen_LLM(
        temperature,
        llm_model_version='qwen-omni-turbo',
        api_key='sk-0a613206ad9f404593f23d16bdeb4ede',
        agent_name="Steve",
        agent_identity="a smart boy",
    )

    llm4 = DouBao_LLM(
        temperature,
        llm_model_version="bot-20250312204525-5lpp5",
        api_key="6ddd5fce-e59c-49bc-a80c-28539c1f95e8",
        agent_name="doubaoAI",
        agent_identity="AI_assistant",
        llm_base_url="https://ark.cn-beijing.volces.com/api/v3/bots",
    )

    tool_list = [Plus(),Sub(),Mul(),Div()]

    # case: a chatting-only agent
    # put the agent 1 into AgentNode
    agent_1 = AgentNode(
        llm=llm1,
        print_agent_execute_result=True,
    )

    # case: an agent can respond your question from outer reference
    # put the agent 2 into AgentNode
    agent_2 = AgentNode(
        llm=llm2,
        print_agent_execute_result=True,
    )

    # case: an agent can read file
    # put the agent 3 into AgentNode
    agent_3 = AgentNode(
        llm = llm3,
        print_agent_execute_result=True,
    )

    # case: an agent can do file reading, tool using at the same time
    # put the agent 4 into AgentNode
    agent_4 = AgentNode(
        llm=llm4,
        tool_list=tool_list,
        max_waiting_time=5,
        sleep_time=1,
        print_agent_execute_result=True,
        require_graph=True
    )


    # call AgentNode
    agent_1("What is your name and what is your identity?")

    agent_2("小明喜欢吃什么？", file_path='test_str_File/testFile_self_introduction.json')

    response = agent_3("What is the color I wear today?", reference="I wear yellow today.")
    print(response) # we also can get response from chatting-bot

    response2 = agent_4("Calculate 3*444")
    print(response2)  # agent with tool wouldn't print the result to screem automatically, so we need print function