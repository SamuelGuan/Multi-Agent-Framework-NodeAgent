import typing as tp
from abc import ABC, abstractmethod

class BaseToolProtocol(ABC):

    '''
    Design idea:

        In my design idea, I think we should give the tool-special agent a list of tools as prompt,
    so that agent can choose one to return the information about which tool to use.
    In short, we give the agent a task and a tool list, then agent return the name of the useful tool.
    then, ergodic tool list to match the function(tool), and run the function locally.
        I regulate this framework, the way we communicate with the agent, is all by the "Prompt"

    Prompt format:
        {
            'system': your identity is {identity} and context reference {reference}
            'history': BaseChatMessageHistory
            'humanMessage': {user_input}
        }

    Any 'reference' should be provided before chat to agent with some special format.
    Here is the example with the symbol '-' for emphasizing:
        "
        - you should answer me in short word
        - you should answer me in long word
        - and so on
        "
    If you don't like above design, you can modify it in BaseAgent.py class BaseAgent.

        If call the llm.loadTools() function which will call the function 'getToolInfo' defined in your tool,
    it will generate a str format tool-list containing the property 'tool_name', 'purposes' and 'args_dict'.
    This str variable is joined with special prompt as {reference}
    for agent identifying those tools conveniently and returning the tool_name, so that we can run the tool!
    '''

    name:str            # describe the tool name
    purposes:str        # describe when to use this tool, recommend use short words
    args_dict:dict      # describe what parameters this tool have, especially for an agent who can choose many tools, should follow this input rule'''
    output_format:str   # describe the format of output, if it is a file, please follow your protocol

    '''
    the entry of the tool
    '''
    @abstractmethod
    def run(self, *args, **kwargs):
        pass

    '''
    Return a dict which describes the tool information 
    including name, purposes, args_list, output_format and so on.
    So that the function 'loadTools()' in XXX_LLM can get the information of this tool.
    '''
    @abstractmethod
    def getToolInfo(self)->dict:
        pass

