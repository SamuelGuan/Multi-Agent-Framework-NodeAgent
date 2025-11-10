'''
This py is an interface to connect LLMs from different platform\
Thus when developer create agents, they didn't need to care about what type of api they are using.
Driven them to concentrate on program development, shortening product productive time.
The only thing they need to do is that "from Agent import ZHiPu_LLM/Deepseek et al."
and instantiate agents with some properties.
'''
import re
import ast
import typing as tp
from Multi_Agent_Framework_NodeAgent_main.BaseAgent import BaseAgent

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.output_parsers import StrOutputParser

from Multi_Agent_Framework_NodeAgent_main.AgentTools import StrFileReadTool, Plus, Sub, Mul, Div
from Multi_Agent_Framework_NodeAgent_main.BaseTool import BaseToolProtocol

##################################################################################################
##################   ZhiPu @                                          ############################
##################################################################################################

class ZhiPu_LLM(BaseAgent):
    # initialize智谱AI
    def __init__(self,
                 temperature:float,
                 llm_model_version:str,
                 api_key:str,
                 agent_name:tp.Optional[str] = "zhipuAI",
                 agent_identity:tp.Optional[str] = "ChatBot",
                 max_session_number:tp.Optional[int] = 5,
                 max_history_number:tp.Optional[int] = 5,
                 llm_base_url: tp.Optional[str] = "https://open.bigmodel.cn/api/paas/v4/"
                 ):

        super().__init__(
                agent_name = agent_name,
                agent_identity = agent_identity,
                temperature = temperature,
                llm_api = api_key,
                max_session_number=max_session_number,
                max_history_number=max_history_number,
                base_url = llm_base_url
        )

        self.llm_model = ChatOpenAI(
            temperature=temperature,
            model=llm_model_version,
            openai_api_key=api_key,
            openai_api_base=llm_base_url
        )

        # load the prompt_template in father class "BaseAgent"
        self.prompt = ChatPromptTemplate(super().get_prompt_template)

        # constructing LCEL chain
        self.runnable_chain = self.prompt | self.llm_model | StrOutputParser()

        # utilize AI chatting history, constructing the runnable chain
        self.chain_with_message_history = RunnableWithMessageHistory(
            runnable=self.runnable_chain,
            get_session_history=super().__getSessionHistory__,
            input_messages_key="user_input",
            history_messages_key="history",
        )

        # a state judge whether call function 'loadTools()'
        self.is_load_tools = False
        self.tool_list = {}

    def chatStream_2Terminal(self, input: str,
                        file = None,
                        output_mode = None,
                        reference = None
                        )->None:
        '''
        no AI tool
        output to terminal
        support 2 different AI output mode: synchronous or asynchronous
        :param input: str
        :param file: str
        :param output_mode: str
        :param reference: str
        '''

        # analysis the content in the file
        file_message = str()
        if file is not None:

            # use dict to delivery the parameters to tool
            args_dict = dict()
            args_dict["file_path"] = file

            tool = StrFileReadTool()
            file_message = tool.run(args_dict)

        #file_message also response to the reference
        if reference is not None:
            file_message += reference

        # judge whether use tools, use->change the prompt template
        if self.is_load_tools:
            input = (f"To complete task <task>{input}<\\task>, \
                     you need to choose the suitable tools provided in <Tool List><\\Tool List>.\
                     Requirement(they have equal rank): \
                      - Return the value of the key word 'tool_name' of the suitable tool,\
                      - Return suitable tool parameters which are in <task><\\task> corresponding to their parameters,\
                      - Return format is dict(ensure the type of value is right and don't make any dict in dict)\
                      - not include other tokens \
                      - If no tool satisfy the task, return 'None' instead.\
                     ")

        # select the output mode
        if output_mode == "async":
            super().__Asyncio2terminal__(self.chain_with_message_history, input, file_message)
        else:
            super().__Syncio2terminal__(self.chain_with_message_history, input, file_message)

    def chatStream_2Buffer(self, input: str,
                        file = None,
                        output_mode = None,
                        reference = None
                        )->any:
        '''
        no AI tool
        output to buffer,
        support 2 different AI output mode: synchronous or asynchronous
        :param input: str
        :param file: str
        :param output_mode: str
        :param reference: str
        '''

        # analysis the content in the file
        file_message = str()
        if file is not None:

            # use dict to delivery the parameters to tool
            args_dict = dict()
            args_dict["file_path"] = file

            tool = StrFileReadTool()
            file_message = tool.run(args_dict)

        #file_message also response to the reference
        if reference is not None:
            file_message += reference

        # judge whether use tools, use->change the prompt template
        if self.is_load_tools:
            input = (f"To complete task <task>{input}<\\task>, \
                     you need to choose the suitable tools provided in <Tool List><\\Tool List>.\
                     Requirement(they have equal rank): \
                      - Return the value of the key word 'tool_name' of the suitable tool,\
                      - Return suitable tool parameters which are in <task><\\task> corresponding to their parameters,\
                      - Return format is dict(ensure the type of value is right and don't make any dict in dict)\
                      - not include other tokens \
                      - If no tool satisfy the task, return 'None' instead.\
                     ")

        # select the output mode
        if output_mode == "async":
            message = super().__Asyncio2buffer__(self.chain_with_message_history, input, file_message)
        else:
            message = super().__Syncio2buffer__(self.chain_with_message_history, input, file_message)

        # judge whether self is tool_agent
        if self.is_load_tools:
            ai_context = message['ai_context']

            if not re.findall('None_tool', ai_context):
                # I had no better idea to tacker some odd situation.
                # Had anyone have good idea?
                try:
                    ai_context = ast.literal_eval(ai_context)
                except Exception as e:
                    return None

                suitable_tool_name = ai_context['tool_name']
                ai_context.pop('tool_name')
                suitable_tool_parameters = ai_context
                return suitable_tool_name, suitable_tool_parameters
            else:
                return None
        else:
            return message['ai_context']

    def loadTools(self, tool_list:list[BaseToolProtocol])->str:
        '''
        load the tool to the agent, return a string
        which is the regularized tool list information
        starting with '<Tool List>:\n' and ending with '</Tool List>'.
        The contains in the labels have the json format
        {'tool_name': _str_ , 'purpose': _str_ , 'args_dict': _dict_}
        '''
        reference = '<Tool List>:\n'

        for tool in tool_list:
            tool_info_dict = tool.getToolInfo()
            if not isinstance(tool_info_dict, dict):
                raise ValueError(f"getToolInfo method in {tool} doesn't return dict!")
            if tool_info_dict["name"] is None or tool_info_dict["purposes"] is None:
                raise ValueError(f"Custom tool {tool} lacks name or purposes! Please check them!")
            else:
                if len(tool_info_dict["args_dict"].keys()) == 0:
                    _args = 'None'
                else:
                    _args = str(tool_info_dict["args_dict"])
                reference += ("{'tool_name':" + tool_info_dict["name"]
                              + ",'purposes':" + tool_info_dict["purposes"]
                              + ",'args_dict':" + _args
                              + '}\n')
                self.tool_list[tool_info_dict["name"]] = tool

        reference += '<\Tool List>\n'
        self.is_load_tools = True
        return reference

    def executionTool(self, tool_name:str, tool_args_dict:tp.Optional[dict] = None)->any:
        '''
        execution the proper tool in self.tool_list
        '''
        if tool_name == 'None' or tool_name is None:
            return 'No tool used!'
        if tool_args_dict is None:
            tool_result = self.tool_list[tool_name].run()
        else:
            tool_result = self.tool_list[tool_name].run(**tool_args_dict)
        return tool_result

##################################################################################################
##################   Qwen @                                          #############################
##################################################################################################

class Qwen_LLM(BaseAgent):
    # initialize Qwen_AI
    def __init__(self,
                 temperature:float,
                 llm_model_version:str,
                 api_key:str,
                 agent_name:tp.Optional[str] = "QwenAI",
                 agent_identity:tp.Optional[str] = "ChatBot",
                 max_session_number:tp.Optional[int] = 5,
                 max_history_number:tp.Optional[int] = 5,
                 llm_base_url: tp.Optional[str] = "https://dashscope.aliyuncs.com/compatible-mode/v1",
                 ):

        super().__init__(
            agent_name=agent_name,
            agent_identity=agent_identity,
            temperature=temperature,
            llm_api=api_key,
            max_session_number=max_session_number,
            max_history_number=max_history_number,
            base_url=llm_base_url
        )

        self.llm_model = ChatOpenAI(
            temperature=temperature,
            model=llm_model_version,
            openai_api_key=api_key,
            openai_api_base=llm_base_url
        )
        self.prompt = ChatPromptTemplate(super().get_prompt_template)
        # constructing LCEL chain
        self.runnable_chain = self.prompt | self.llm_model | StrOutputParser()
        # utilize AI chatting history, constructing the runnable chain
        self.chain_with_message_history = RunnableWithMessageHistory(
            self.runnable_chain,
            super().__getSessionHistory__,
            input_messages_key="user_input",
            history_messages_key="history",
        )

        # a state judge whether call function 'loadTools()'
        self.is_load_tools = False
        self.tool_list = {}

    def chatStream_2Terminal(self, input: str,
                        file = None,
                        output_mode = None,
                        reference = None
                        ) -> None:
        '''
        no AI tool
        output to terminal
        support 2 different AI output mode: synchronous or asynchronous
        :param input: str
        :param file: str
        :param output_mode: str
        :param reference: str
        '''

        # analysis the content in the file
        file_message = str()
        if file is not None:

            # use dict to delivery the parameters to tool
            args_dict = dict()
            args_dict["file_path"] = file

            tool = StrFileReadTool()
            file_message = tool.run(args_dict)

        #file_message also response to the reference
        if reference is not None:
            file_message += reference

        # judge whether use tools, use->change the prompt template
        if self.is_load_tools:
            input = (f"To complete task <task>{input}<\\task>, \
                     you need to choose the suitable tools provided in <Tool List><\\Tool List>.\
                     Requirement(they have equal rank): \
                      - Return the value of the key word 'tool_name' of the suitable tool in <Tool list>,\
                      - Return suitable tool parameters which are in <task><\\task> corresponding to their parameters,\
                      - Return format is dict(ensure the type of value is right and don't make any dict in dict)\
                      - not include other tokens \
                      - If no tool satisfy the task, return 'None' instead.\
                     ")

        # select the output mode
        if output_mode == "async":
            super().__Asyncio2terminal__(self.chain_with_message_history, input, file_message)
        else:
            super().__Syncio2terminal__(self.chain_with_message_history, input, file_message)

    def chatStream_2Buffer(self, input: str,
                        file = None,
                        output_mode = None,
                        reference = None
                        ) -> any:
        '''
        no AI tool
        output to buffer,
        support 2 different AI output mode: synchronous or asynchronous
        :param input: str
        :param file: str
        :param output_mode: str
        :param reference: str
        '''

        # analysis the content in the file
        file_message = str()
        if file is not None:

            # use dict to delivery the parameters to tool
            args_dict = dict()
            args_dict["file_path"] = file

            tool = StrFileReadTool()
            file_message = tool.run(args_dict)

        #file_message also response to the reference
        if reference is not None:
            file_message += reference

        # judge whether use tools, use->change the prompt template
        if self.is_load_tools:
            input = (f"To complete task <task>{input}<\\task>, \
                     you need to choose the suitable tools provided in <Tool List><\\Tool List>.\
                     Requirement(they have equal rank): \
                      - Return the value of the key word 'tool_name' of the suitable tool in <Tool list>,\
                      - Return suitable tool parameters which are in <task><\\task> corresponding to their parameters,\
                      - Return format is dict(ensure the type of value is right and don't make any dict in dict)\
                      - not include other tokens \
                      - If no tool satisfy the task, return 'None' instead.\
                     ")

        # select the output mode
        if output_mode == "async":
            message = super().__Asyncio2buffer__(self.chain_with_message_history, input, file_message)
        else:
            message = super().__Syncio2buffer__(self.chain_with_message_history, input, file_message)

        # judge whether self is tool_agent
        if self.is_load_tools:
            ai_context = message['ai_context']

            if not re.findall('None_tool', ai_context):
                # I had no better idea to tacker some odd situation.
                # Had anyone have good idea?
                try:
                    ai_context = ast.literal_eval(ai_context)
                except Exception as e:
                    return None

                suitable_tool_name = ai_context['tool_name']
                ai_context.pop('tool_name')
                suitable_tool_parameters = ai_context
                return suitable_tool_name, suitable_tool_parameters
            else:
                return None
        else:
            return message['ai_context']

    def loadTools(self, tool_list:list)->str:
        '''
        load the tool to the agent, return a string
        which is the regularized tool list information
        starting with '<Tool List>:\n' and ending with '</Tool List>'.
        The contains in the labels have the json format
        {'tool_name': _str_ , 'purpose': _str_ , 'args_dict': _dict_}
        '''
        reference = '<Tool List>:\n'

        for tool in tool_list:
            tool_info_dict = tool.getToolInfo()
            if not isinstance(tool_info_dict,dict):
                raise ValueError(f"getToolInfo method in {tool} doesn't return dict!")
            if tool_info_dict["name"] is None or tool_info_dict["purposes"] is None:
                raise ValueError(f"Custom tool {tool} lacks name or purposes! Please check them!")
            else:
                if len(tool_info_dict["args_dict"].keys()) == 0:
                    _args = 'None'
                else:
                    _args = str(tool_info_dict["args_dict"])
                reference += ("{'tool_name:'" + tool_info_dict["name"]
                              + ",purposes:" + tool_info_dict["purposes"]
                              + ",args_dict" + _args
                              + '}\n')
                self.tool_list[tool_info_dict["name"]] = tool

        reference += '<\Tool List>\n'
        self.is_load_tools = True
        return reference

    def executionTool(self, tool_name:str, tool_args_dict:tp.Optional[dict] = None)->any:
        '''
        execution the proper tool in self.tool_list
        '''
        if tool_name == 'None' or tool_name is None:
            return 'No tool used!'
        if tool_args_dict is None:
            tool_result = self.tool_list[tool_name].run()
        else:
            tool_result = self.tool_list[tool_name].run(**tool_args_dict)
        return tool_result

##################################################################################################
##################   Kimi @moonlight                                 #############################
##################################################################################################

class Kimi_LLM(BaseAgent):
    # initialize Kimi_AI
    def __init__(self,
                 temperature:float,
                 llm_model_version:str,
                 api_key:str,
                 agent_name:tp.Optional[str] = "KimiAI",
                 agent_identity:tp.Optional[str] = "ChatBot",
                 max_session_number:tp.Optional[int] = 5,
                 max_history_number:tp.Optional[int] = 5,
                 llm_base_url: tp.Optional[str] = "https://api.moonshot.cn/v1"
                 ):

        super().__init__(
            agent_name=agent_name,
            agent_identity=agent_identity,
            temperature=temperature,
            llm_api=api_key,
            max_session_number=max_session_number,
            max_history_number=max_history_number,
            base_url=llm_base_url
        )

        self.llm_model = ChatOpenAI(
            temperature=temperature,
            model=llm_model_version,
            openai_api_key=api_key,
            openai_api_base=llm_base_url
        )
        self.prompt = ChatPromptTemplate(super().get_prompt_template)
        # constructing LCEL chain
        self.runnable_chain = self.prompt | self.llm_model | StrOutputParser()
        # utilize AI chatting history, constructing the runnable chain
        self.chain_with_message_history = RunnableWithMessageHistory(
            self.runnable_chain,
            super().__getSessionHistory__,
            input_messages_key="user_input",
            history_messages_key="history",
        )

        # a state judge whether call function 'loadTools()'
        self.is_load_tools = False
        self.tool_list = {}

    def chatStream_2Terminal(self, input: str,
                        file = None,
                        output_mode = None,
                        reference = None
                        ) -> None:
        '''
        no AI tool
        output to terminal
        support 2 different AI output mode: synchronous or asynchronous
        :param input: str
        :param file: str
        :param output_mode: str
        :param reference: str
        '''

        # analysis the content in the file
        file_message = str()
        if file is not None:

            # use dict to delivery the parameters to tool
            args_dict = dict()
            args_dict["file_path"] = file

            tool = StrFileReadTool()
            file_message = tool.run(args_dict)

        #file_message also response to the reference
        if reference is not None:
            file_message += reference

        # judge whether use tools, use->change the prompt template
        if self.is_load_tools:
            input = (f"To complete task <task>{input}<\\task>, \
                     you need to choose the suitable tools provided in <Tool List><\\Tool List>.\
                     Requirement(they have equal rank): \
                      - Return the value of the key word 'tool_name' of the suitable tool in <Tool list>,\
                      - Return suitable tool parameters which are in <task><\\task> corresponding to their parameters,\
                      - Return format is dict(ensure the type of value is right and don't make any dict in dict)\
                      - not include other tokens \
                      - If no tool satisfy the task, return 'None' instead.\
                     ")

        # select the output mode
        if output_mode == "async":
            super().__Asyncio2terminal__(self.chain_with_message_history, input, file_message)
        else:
            super().__Syncio2terminal__(self.chain_with_message_history, input, file_message)

    def chatStream_2Buffer(self, input: str,
                        file = None,
                        output_mode = None,
                        reference = None
                        ) -> any:
        '''
        no AI tool
        output to buffer,
        support 2 different AI output mode: synchronous or asynchronous
        :param input: str
        :param file: str
        :param output_mode: str
        :param reference: str
        '''

        # analysis the content in the file
        file_message = str()
        if file is not None:

            # use dict to delivery the parameters to tool
            args_dict = dict()
            args_dict["file_path"] = file

            tool = StrFileReadTool()
            file_message = tool.run(args_dict)

        #file_message also response to the reference
        if reference is not None:
            file_message += reference

        # judge whether use tools, use->change the prompt template
        if self.is_load_tools:
            input = (f"To complete task <task>{input}<\\task>, \
                     you need to choose the suitable tools provided in <Tool List><\\Tool List>.\
                     Requirement(they have equal rank): \
                      - Return the value of the key word 'tool_name' of the suitable tool in <Tool list>,\
                      - Return suitable tool parameters which are in <task><\\task> corresponding to their parameters,\
                      - Return format is dict(ensure the type of value is right and don't make any dict in dict)\
                      - not include other tokens \
                      - If no tool satisfy the task, return 'None' instead.\
                     ")

        # select the output mode
        if output_mode == "async":
            message = super().__Asyncio2buffer__(self.chain_with_message_history, input, file_message)
        else:
            message = super().__Syncio2buffer__(self.chain_with_message_history, input, file_message)

        # judge whether self is tool_agent
        if self.is_load_tools:
            ai_context = message['ai_context']

            if not re.findall('None_tool', ai_context):
                # I had no better idea to tacker some odd situation.
                # Had anyone have good idea?
                try:
                    ai_context = ast.literal_eval(ai_context)
                except Exception as e:
                    return None

                suitable_tool_name = ai_context['tool_name']
                ai_context.pop('tool_name')
                suitable_tool_parameters = ai_context
                return suitable_tool_name, suitable_tool_parameters
            else:
                return None
        else:
            return message['ai_context']


    def loadTools(self, tool_list:list)->str:
        '''
        load the tool to the agent, return a string
        which is the regularized tool list information
        starting with '<Tool List>:\n' and ending with '</Tool List>'.
        The contains in the labels have the json format
        {'tool_name': _str_ , 'purpose': _str_ , 'args_dict': _dict_}
        '''
        reference = '<Tool List>:\n'

        for tool in tool_list:
            tool_info_dict = tool.getToolInfo()
            if not isinstance(tool_info_dict,dict):
                raise ValueError(f"getToolInfo method in {tool} doesn't return dict!")
            if tool_info_dict["name"] is None or tool_info_dict["purposes"] is None:
                raise ValueError(f"Custom tool {tool} lacks name or purposes! Please check them!")
            else:
                if len(tool_info_dict["args_dict"].keys()) == 0:
                    _args = 'None'
                else:
                    _args = str(tool_info_dict["args_dict"])
                reference += ("{'tool_name:'" + tool_info_dict["name"]
                              + ",purposes:" + tool_info_dict["purposes"]
                              + ",args_dict" + _args
                              + '}\n')
                self.tool_list[tool_info_dict["name"]] = tool

        reference += '<\Tool List>\n'
        self.is_load_tools = True
        return reference

    def executionTool(self, tool_name:str, tool_args_dict:tp.Optional[dict] = None)->any:
        '''
        execution the proper tool in self.tool_list
        '''
        if tool_name == 'None' or tool_name is None:
            return 'No tool used!'
        if tool_args_dict is None:
            tool_result = self.tool_list[tool_name].run()
        else:
            tool_result = self.tool_list[tool_name].run(**tool_args_dict)
        return tool_result

##################################################################################################
##################   DouBao @                                        #############################
##################################################################################################
class DouBao_LLM(BaseAgent):

    # initialize DouBao_AI
    def __init__(self,
                 temperature:float,
                 llm_model_version:str,
                 api_key:str,
                 agent_name:tp.Optional[str] = "DouBaoAI",
                 agent_identity:tp.Optional[str] = "ChatBot",
                 max_session_number:tp.Optional[int] = 5,
                 max_history_number:tp.Optional[int] = 5,
                 llm_base_url:tp.Optional[str] = 'https://ark.cn-beijing.volces.com/api/v3',
                 memorize:tp.Optional[bool] = True
                 ):

        super().__init__(
            agent_name=agent_name,
            agent_identity=agent_identity,
            temperature=temperature,
            llm_api=api_key,
            max_session_number=max_session_number,
            max_history_number=max_history_number,
            base_url=llm_base_url
        )

        self.llm_model = ChatOpenAI(
            temperature=temperature,
            model=llm_model_version,
            openai_api_key=api_key,
            openai_api_base=llm_base_url
        )

        self.prompt = ChatPromptTemplate(super().get_prompt_template)
        # constructing LCEL chain
        self.runnable_chain = self.prompt | self.llm_model | StrOutputParser()

        # utilize AI chatting history, constructing the runnable chain
        self.chain_with_message_history = RunnableWithMessageHistory(
            self.runnable_chain,
            super().__getSessionHistory__,
            input_messages_key="user_input",
            history_messages_key="history",
        )

        # a state judge whether call function 'loadTools()'
        self.is_load_tools = False
        self.tool_list = {}

        self.session_id = 0

        self.memorize = memorize

    def chatStream_2Terminal(self, input: str,
                        file = None,
                        reference = None,
                        output_mode:tp.Optional[str] = "async",
                        ) -> None:
        '''
        output to terminal, only support chatting instead of agent or multi-model llm.
        support 2 different AI output mode: synchronous or asynchronous
        :param input: str
        :param file: str
        :param output_mode: str
        :param reference: str
        '''

        # analysis the content in the file
        file_message = str()
        if file is not None:

            # use dict to delivery the parameters to tool
            args_dict = dict()
            args_dict["file_path"] = file

            tool = StrFileReadTool()
            file_message = tool.run(args_dict)

        #file_message also response to the reference
        if reference is not None:
            file_message += reference

        # judge whether using tools, if true, use->change the prompt template
        if self.is_load_tools:
            input = (f"To complete task <task>{input}<\\task>, \
                     you need to choose the suitable tools provided in <Tool List><\\Tool List>.\
                     Requirement(they have equal rank): \
                      - Return the value of the key word 'tool_name' of the suitable tool in <Tool list>,\
                      - Return suitable tool parameters which are in <task><\\task> corresponding to their parameters,\
                      - Return format is dict(ensure the type of value is right and don't make any dict in dict)\
                      - not include other tokens \
                      - If no tool satisfy the task, return 'None' instead.\
                     ")

        # select the output mode
        if output_mode == "async":
            super().__Asyncio2terminal__(self.chain_with_message_history, input, file_message)
        else:
            super().__Syncio2terminal__(self.chain_with_message_history, input, file_message)


    def chatStream_2Buffer(self, input: str,
                     file = None,
                     output_mode = None,
                     reference = None
                     ) -> any:
        '''
        output to buffer,
        support 2 different AI output mode: synchronous or asynchronous
        :param input: str
        :param file: str
        :param output_mode: str
        :param reference: str
        '''

        # analysis the content in the file
        file_message = str()
        if file is not None:

            # use dict to delivery the parameters to tool
            args_dict = dict()
            args_dict["file_path"] = file

            tool = StrFileReadTool()
            file_message = tool.run(args_dict)

        #file_message also response to the reference
        if reference is not None:
            file_message += reference

        # judge whether use tools, use->change the prompt template
        if self.is_load_tools:
            input = (f"To complete task <task>{input}<\\task>, \
                     you need to choose the suitable tools provided in <Tool List><\\Tool List>.\
                     Requirement(they have equal rank): \
                      - Return the value of the key word 'tool_name' of the suitable tool in <Tool list>,\
                      - Return suitable tool parameters which are in <task><\\task> corresponding to their parameters in <Tool list>,\
                      - Return format is dict(ensure the type of value is right and don't make any dict in dict)\
                      - not include other tokens \
                      - If no tool satisfy the task, return <None_tool> instead.\
                     ")

        # select the output mode
        if output_mode == "async":
            message = super().__Asyncio2buffer__(self.chain_with_message_history, input, file_message)
        else:
            message = super().__Syncio2buffer__(self.chain_with_message_history, input, file_message)

        # judge whether self is tool_agent
        if self.is_load_tools:
            ai_context = message['ai_context']

            if not re.findall('None_tool', ai_context):
                # I had no better idea to tacker some odd situation.
                # Had anyone have good idea?
                try:
                    ai_context = ast.literal_eval(ai_context)
                except Exception as e:
                    return None

                suitable_tool_name = ai_context['tool_name']
                ai_context.pop('tool_name')
                suitable_tool_parameters = ai_context
                if self.memorize:
                    super().__HistoryAppend__(
                        ai_context = f"Last term use tool called function with the tool name {suitable_tool_name} having parameters {suitable_tool_parameters}",
                        user_message = f"user_input: {input}\n file_message: {file_message}\n"
                    )
                return suitable_tool_name, suitable_tool_parameters
            else:
                if self.memorize:
                    super().__HistoryAppend__(
                        ai_context = f"None",
                        user_message = f"user_input: {input}\n file_message: {file_message}\n"
                    )
                return None
        else:
            if self.memorize:
                super().__HistoryAppend__(
                    ai_message = message['ai_context'],
                    user_message = f"user_input: {input}\n file_message: {file_message}\n"
                )
            return message['ai_context']

    def loadTools(self, tool_list:list)->str:
        '''
        load the tool to the agent, return a string
        which is the regularized tool list information
        starting with '<Tool List>:\n' and ending with '</Tool List>'.
        The contains in the labels have the json format
        {'tool_name': _str_ , 'purpose': _str_ , 'args_dict': _dict_}
        '''
        reference = '<Tool List>:\n'

        for tool in tool_list:
            tool_info_dict = tool.getToolInfo()

            # validation check
            if not isinstance(tool_info_dict,dict):
                raise ValueError(f"getToolInfo method in {tool} doesn't return dict!")
            if tool_info_dict["name"] is None or tool_info_dict["purposes"] is None:
                raise ValueError(f"Custom tool {tool} lacks sufficient information! Please check them!")

            # judge whether this tool has parameters or not
            if len(tool_info_dict["args_dict"].keys()) == 0:
                _args = 'None'
            else:
                _args = str(tool_info_dict["args_dict"])

            reference += ("{'tool_name':" + tool_info_dict["name"]
                              + ",'purposes':" + tool_info_dict["purposes"]
                              + ",'args_dict'" + _args
                              + '}\n')
            self.tool_list[tool_info_dict["name"]] = tool

        reference += '<\Tool List>\n'

        # change the llm state to ensure it is a tool_agent
        self.is_load_tools = True
        return reference

    def executionTool(self, tool_name:tp.Optional[str], tool_args_dict:tp.Optional[dict] = None)->any:
        '''
        execution the proper tool in self.tool_list
        '''
        if tool_name == 'None' or tool_name is None:
            return 'No tool used!'
        if tool_args_dict is None:
            tool_result = self.tool_list[tool_name].run()
        else:
            tool_result = self.tool_list[tool_name].run(**tool_args_dict)
        return tool_result
    
    def createNewChatSession(self) -> int:
        try:
            super().createNewSession()
            self.session_id = super().session_id
            return self.session_id
        except Exception as e:
            print(e)
            return None
    
    def getAllHistory(self) -> dict:
        return super().__ListingAllHistory__()
    
    def getCurrentSessionID(self) -> int:
        return super().llm_session_id

    def loadChatHistory(self, messages: list[dict[str, str]]):
        super().__HistoryLoad__(messages)



class Deepseek_LLM(object):
    pass

class Grok_LLM(object):
    pass


if __name__ == '__main__':

    pass

