from LLMs import DouBao_LLM
from AgentTools import Plus,Sub,Mul,Div

'''
Given 4 example in this file, also, I will call llm as agent.

- 1st, example of create an agent with calculate tools. It will return the proper tool's name, otherwise return <None_tool>
If agent return the proper tool's name, it will also return the parameters in their proper type.
- 2nd, example of chatting-only agent.
- 3rd, example of reviewing the chatting history.
- 4th, example of chatting agent with json/csv file tackle ability.

Because these 4 examples are using DouBao LLM, there web site is 'https://console.volcengine.com'
make sure you have their API key! Don't forget to create a bot on that platform so that we can call the tool-use agent!
It's easy-used! Starting your customized agent with this simple framework!
'''


if __name__ == '__main__':
    ##############################    Task 1     ####################################
    # task 1 & 2 setting
    user_input1 = "calculate 4 * 31 "
    user_input2 = "If there are catastrophes on my way home, will you love me forever?"

    # the max of the number of sessions
    maxSessionNumber = 5
    # the max of the number of chat history recording
    maxHistoryNumber = 6
    # LLM's output temperature
    temperature = 0.5

    # llm setting
    api_key = "6ddd5fce-e59c-49bc-a80c-28539c1f95e8"
    llm_model_version = "bot-20250312204525-5lpp5"
    base_url = "https://ark.cn-beijing.volces.com/api/v3/bots"

    # task 4 setting
    file = 'test_str_File/testFile_self_introduction.json'

    # specialize the agent
    llm = DouBao_LLM(
        temperature,
        llm_model_version=llm_model_version,
        api_key=api_key,
        agent_name="doubaoAI",
        agent_identity="AI_assistant",
        max_session_number=maxSessionNumber,
        max_history_number=maxHistoryNumber,
        llm_base_url=base_url
    )

    print("########## round 1 ###########")
    # store the tools in list, the tool must
    tool_list = [Plus(), Sub(), Mul(), Div()]
    # load the tool_list to agent and get the tool list reference(str)
    reference = llm.loadTools(tool_list)
    # put the user_input and reference to agent, get the proper tool name and parameters
    suitable_tool_info = llm.chatStream_2Buffer(input=user_input1,reference=reference)
    # call the tool and put the parameters in tool.
    # PS: I am proud of this design, because you can put the parameters which are getting from different agent when u need,
    # This design broaden the usage of agent's tool and tool's design!
    if suitable_tool_info is not None and isinstance(suitable_tool_info,tuple):
        suitable_tool_name, suitable_tool_parameters = suitable_tool_info[0], suitable_tool_info[1]
        r = llm.executionTool(tool_name=suitable_tool_name,
                              tool_args_dict=suitable_tool_parameters)
        print('\033[32m' +'tool_use_result:' + str(r)+'\033[0m')

    #-----------------------------------------------------------------------------------------------#
    ####################################### Task 2 & 3 ##############################################
    # Here I recreate a new agent to finish two task
    llm = DouBao_LLM(
        temperature,
        llm_model_version=llm_model_version,
        api_key=api_key,
        agent_name="doubaoAI",
        agent_identity="AI_lover",
        max_session_number=maxSessionNumber,
        max_history_number=maxHistoryNumber,
        llm_base_url=base_url
    )

    print("session_id:",llm.session_id)
    print("########## round 2 ###########")
    llm.chatStream_2Terminal(user_input2)
    llm.chatStream_2Terminal("What I have had asked you a moment ago?")
    llm.chatStream_2Terminal(input="小明爱吃什么？",file=file)

    # create new session to avoid new session is affected by old session
    llm.createNewSession()
    print("session_id:",llm.session_id)
    llm.chatStream_2Terminal("What I have had asked you a moment ago?")
    # It's odd that Kimi, ZhiPu and Qwen will forget the former session,
    # but DouBao will remember, I suppose that DouBao's api isn't the true LLM api,
    # they may just setting an interface layer to block some bad input.