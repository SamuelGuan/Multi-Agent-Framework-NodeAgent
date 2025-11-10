import time
import typing as tp
from . import BaseAgent
from typing import List, Optional, Dict, Any

'''
The main concept of NodeAgent is one agent one tool
can communicate with other agents by python's string or any other form you design (I don't design this part, hope for yor coding)
'''


'''
I design some basic properties and function for asynchronous
I don't know what is your style of the thread management, so I do nothing about it
just customize your asynchronous application if you want!
'''

class AgentNode(object):
    def __init__(self,
                llm:BaseAgent,
                output_mode:tp.Optional[str]=None,
                tool_list:tp.Optional[callable]=None,
                max_waiting_time:tp.Optional[float]=None,
                sleep_time:tp.Optional[float]=1,
                print_agent_execute_result:tp.Optional[bool]=False,
                require_graph:tp.Optional[bool]=False):

        '''
        :param llm: Large Language Model instance
        :param output_mode: Async or Sync
        :param tool_list: a list of tool function
        :param max_waiting_time: the maximum wait time in queue
        :param sleep_time: the sleep period when waiting for work in queue
        :param print_agent_execute_result: whether print the agent execute result to terminal
        :param require_graph: whether this nood need to be recorded to the multi-agent team graph
        '''

        self.llm = llm
        self.agent_node_identity = llm.agentIdentity
        self.require_autograph = require_graph
        self.output_mode = output_mode
        self.tool_reference = None

        if tool_list is not None:
            self.tool_list = [(lambda name:name)(name=tool.getToolInfo()['name']) for tool in tool_list]
            self.tool_reference = self.llm.loadTools(tool_list)
        else:
            self.tool_list = None

        self.max_waiting_time = max_waiting_time

        if sleep_time is None and output_mode == 'async':
            raise Warning(f"system info: Agent 【{llm.agentName}】's Sleep time is None, if it's async mode, it will be dangerous.")

        self.sleep_time = sleep_time
        self.print_agent_execute_result = print_agent_execute_result

        # the agent state,
        # 'Free' denote the agentNode isn't working
        # 'Busy' denote the agentNode is working
        # 'Waiting' denote the agentNode is in task queue
        self.state_dict = {
            "Free": True,
            "Busy": False,
            "Waiting": False,
        }

    #def toOtherNode(self, prev_node=None, next_node=None):
        #'''Connect this agent node to other agent nodes'''
        #if prev_node is not None and not isinstance(prev_node, AgentNode):
            #raise TypeError(f"can't connect {type(prev_node)} to <class.AgentNode>!")
        #else:
            #self.node_connect_dict['Previous_AgentNode'] = next_node.node_identity

        #if next_node is not None and not isinstance(next_node, AgentNode):
            #raise TypeError(f"can't connect {type(next_node)} to <class.AgentNode>!")
        #else:
            #self.node_connect_dict['Previous_AgentNode'] = next_node.node_identity


    def __call__(self, user_input:str,
                 file_path=None,
                 reference=None,
                 other_param_of_tool=None)->any:
        # check agent node's state
        '''
        Busy -> raise Error
        Waiting -> wait for some time until waiting_time > max_waiting_time or is_waiting_time == False
        Free -> execute the task
        '''

        if self.is_busy:
            raise ValueError("Agent is busy!It can't execute the task!")

        ### this judge is for asyncio mode ###
        if self.is_waiting:
            start_time = time.time()
            if self.max_waiting_time is not None:
                while self.is_waiting:
                    if time.time() - start_time > self.max_waiting_time:
                        raise TimeoutError("waiting in Queue for too long!Check your code!")
                    time.sleep(self.sleep_time)
            else:
                while self.is_waiting:
                    time.sleep(self.sleep_time)

        if self.is_free:
            start_time = time.time()
            self.__switchState__('Busy')

            # judge if there is any other reference and concatenate them into one string!
            if reference is not None:
                if self.tool_reference is not None:
                    reference = self.tool_reference + "\n Besides, there also has another reference:\n"+ reference
                else:
                    reference = "\n Besides, there also has another reference:\n"+ reference
            else:
                if self.tool_reference is not None:
                    reference = self.tool_reference

            suitable_tool_info = self.llm.chatStream_2Buffer(input=user_input,
                                                                 output_mode=self.output_mode,
                                                                 reference=reference,
                                                                 file=file_path)

            # if suitable_tool_info is not None, it does can execute the tool!
            if isinstance(suitable_tool_info, tuple) and self.tool_list is not None:
                suitable_tool_name, suitable_tool_parameters = suitable_tool_info[0], suitable_tool_info[1]
                # concatenate the parameters if is necessary
                if other_param_of_tool is not None:
                    suitable_tool_parameters.update(other_param_of_tool)
                tool_call_result = self.llm.executionTool(tool_name=suitable_tool_name,
                                      tool_args_dict=suitable_tool_parameters)

                print('\033[36m'+f"system info:Agent 【{self.llm.agentName}】 running for {time.time() - start_time}s"+'\033[0m')
                if self.print_agent_execute_result:
                    print('\033[32m' + " Agent Info: " + str(tool_call_result) + '\033[0m')
                self.__switchState__('Free')
                return tool_call_result

            # if suitable_tool_info is str, maybe it is chatting bot
            elif isinstance(suitable_tool_info, str):
                if self.print_agent_execute_result:
                    print('\033[32m' +"Agent Info: "+ str(suitable_tool_info)+ '\033[0m')
                self.__switchState__('Free')
                return suitable_tool_info

            # else suitable_tool_info is None, it does couldn't match the task with proper tool
            else:
                print('\033[36m'+f"system info:Agent 【{self.llm.agentName}】 return Nothing. Maybe no suitable tool!"+'\033[0m')
                self.__switchState__('Free')
                return None


    def __switchState__(self, state:str):
        if state == 'Busy':
            self.state_dict['Busy'] = True
            self.state_dict['Free'] = False
            self.state_dict['Waiting'] = False
        elif state == 'Free':
            self.state_dict['Busy'] = False
            self.state_dict['Free'] = True
            self.state_dict['Waiting'] = False
        elif state == 'Waiting':
            self.state_dict['Busy'] = False
            self.state_dict['Free'] = False
            self.state_dict['Waiting'] = True
        else:
            raise ValueError(f"parameter {state} is invalid!")

    @property
    def is_free(self):
        return self.state_dict["Free"]

    @property
    def is_busy(self):
        return self.state_dict["Busy"]

    @property
    def is_waiting(self):
        return self.state_dict["Waiting"]

    @property
    def node_identity(self):
        return self.agent_node_identity

    @property
    def require_graph(self):
        return self.require_autograph

    @property
    def tools_list(self):
        return self.tool_list

    @property
    def all_properties(self):
        return {
            'agent_node_identity': self.agent_node_identity,
            'llm': self.llm.allProperty,
            'output_mode':self.output_mode,
            'tool_list':self.tool_list,
            'max_waiting_time':self.max_waiting_time,
            'sleep_time':self.sleep_time,
            'print_agent_execute_result_or_not':self.print_agent_execute_result,
            'require_graph':self.require_autograph,
        }

# for autograph framework
class AgentTeam(object):
    def __init__(self, agent_list: List[AgentNode]) -> None:
        self.agent_list = agent_list
        self.team_chat_history = {}
        if hasattr(agent_list[0].llm, 'getCurrentSessionID'):
            self.session_id = agent_list[0].llm.getCurrentSessionID()
        else:
            self.session_id = 0

    def createNewChatSession(self) -> int:
        for agent in self.agent_list:
            self.session_id = agent.llm.createNewChatSession()
        return self.session_id
    
    def getTeamChatHistory(self) -> dict:
        return self.team_chat_history
    
    def teamChatHistoryAppend(self, human_input: str, last_agent_response: str, session_id: int = -1, kwargs: dict = None) -> None:
        if session_id == -1:
            session_id = self.session_id
        if session_id not in self.team_chat_history:
            self.team_chat_history[session_id] = []
        if kwargs is None:
            self.team_chat_history[session_id].append({'human_input':human_input, 'last_agent_response':last_agent_response})
        else:
            self.team_chat_history[session_id].append({'human_input':human_input, 'last_agent_response':last_agent_response, **kwargs})
    
    def workflowTrajectory(self):
        # TODO: 教师团队工作流轨迹
        pass
