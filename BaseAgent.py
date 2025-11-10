import typing as tp
import asyncio
from abc import abstractmethod

from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import (
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

class BaseAgent(object):
    '''
    The BaseAgent class is the abstract class of downstream agents which
    must inherit from this class
    '''
    prompt_template = [
        SystemMessagePromptTemplate.from_template("your identity: {identity}, response with reference content: {file_message}"),
        MessagesPlaceholder(variable_name="history"),
        HumanMessagePromptTemplate.from_template("{user_input}"),
    ]

    def __init__(self,
                agent_name:tp.Optional[str] = None,
                agent_identity:tp.Optional[str] = None,
                temperature:tp.Optional[float] = '0.7',
                llm_api:tp.Optional[str] = None,
                max_session_number:tp.Optional[int] = 5,
                max_history_number:tp.Optional[int] = 5,
                base_url:tp.Optional[str] = None,
                ):
        self.agent_name = agent_name
        self.agent_identity = agent_identity
        self.temperature = temperature
        self.llm_api = llm_api
        self.llm_url = base_url
        # storing the history
        self.session_id = 0
        self.store = dict[str, __ChatMessageHistory__]()
        # ensure the max_session_number is positive
        assert max_session_number > 0
        self.max_session_number = max_session_number
        # ensure the max_history_number is positive
        assert max_history_number > 0
        self.max_history_number = max_history_number
        self.createNewSession()

    # get the chatting history
    def __getSessionHistory__(self, session_id: int = 1) -> BaseChatMessageHistory:
        session_key = f"UserSession NO.{session_id}"
        if session_key not in self.store.keys():
            self.store[session_key] = __ChatMessageHistory__()
        return self.store[session_key]

    # ensure the number of session wouldn't greater than the max_session_number,
    # if greater, delete the first session and move the rest's session number to former one
    def __sessionNumberControl__(self)->None:
        if len(self.store.keys()) >= self.max_session_number:
            self.store.pop("UserSession NO.1")
            tmpStore = dict[str, __ChatMessageHistory__]()
            for key in self.store.keys():
                if not isinstance(key, str):
                    raise ValueError("self.store.key is not str!")
                key_copy = str(key)
                new_key = key_copy.replace(key_copy[-1], str(int(key_copy[-1]) - 1))
                tmpStore[new_key] = self.store[key]
            self.store = tmpStore
            self.session_id = self.max_session_number - 1

    def __HistoryAppend__(self, ai_message:str, user_message:str, session_id: int = -1):
        if session_id == -1:
            session_id = self.session_id
        session_key = f"UserSession NO.{session_id}"
        history: __ChatMessageHistory__ = self.__getSessionHistory__(session_key)
        history.add_user_message(user_message)
        history.add_ai_message(ai_message)
        self.store[session_key] = history
    
    # create new session
    def createNewSession(self):
        self.__sessionNumberControl__()
        self.session_id += 1
        self.__HistoryAppend__("\n", "\n")
    

    def __ListingAllHistory__(self) -> dict:
        """
        return:
        {
            1 :{
                "session_key": "UserSession NO.1", 
                "ai_messages": str,
                "user_messages": str
            },
            2 :{
                "session_key": "UserSession NO.2", 
                "ai_messages": str,
                "user_messages": str
            },
        }
        """
        history_dict = {}
        if self.session_id >= 1:
            for i in range(1, self.session_id + 1):
                session_key = "UserSession NO." + str(i)
                if session_key not in self.store:
                    continue
                base_history = self.store[session_key]
                # 兼容不同历史实现，优先使用 get_messages()
                messages = (
                    base_history.get_messages() if hasattr(base_history, "get_messages") else getattr(base_history, "messages", [])
                )

                ai_contents = []
                human_contents = []
                for msg in messages:
                    msg_type = getattr(msg, "type", None)
                    if isinstance(msg, HumanMessage) or msg_type == "human":
                        human_contents.append(getattr(msg, "content", ""))
                    elif isinstance(msg, AIMessage) or msg_type == "ai":
                        ai_contents.append(getattr(msg, "content", ""))

                history_dict[i] = {
                    "session_key": session_key,
                    "ai_messages": "\n".join(ai_contents),
                    "user_messages": "\n".join(human_contents),
                }
        return history_dict

    # Asynchronous print AI's response to terminal, only can be called by self.__Asyncio2terminal__ function
    async def __AsyncioPrintResponseStream2terminal__(self, response):
        async for chunk in response:
            print(chunk, end='', flush=True)

    # Asynchronous print AI's response to buffer(actually is dict), only can be called by self.__Asyncio2buffer__ function
    async def __AsyncioPrintResponseStream2buffer__(self, response)->dict:
        result = dict()
        str_buffer = str()
        async for chunk in response:
            str_buffer += chunk
        result['ai_context'] = str_buffer
        return result

    # Asynchronous print AI's response to terminal
    def __Asyncio2terminal__(self,
                            chain_with_message_history,
                            user_input,
                            file_message:tp.Optional[str]=None)->None:
        try:
            # 获取异步流
            response = chain_with_message_history.astream(
                input={"identity": self.agentIdentity, "file_message": file_message, "user_input": user_input},
                config={"configurable": {f"session_id": f"UserSession NO.{self.session_id}"}}
            )
            # 执行异步流
            asyncio.run(self.__AsyncioPrintResponseStream2terminal__(response))
            print('\n')
        except Exception as e:
            raise ValueError(f"LLM wrong! Error:{e}")

    # Synchronous print AI's response to terminal
    def __Syncio2terminal__(self,
                            chain_with_message_history,
                            user_input,
                            file_message:tp.Optional[str]=None)->None:
        try:
            # 获取同步流
            response = chain_with_message_history.stream(
                input={"identity": self.agentIdentity, "file_message": file_message, "user_input": user_input},
                config={"configurable": {"session_id": f"UserSession NO.{self.session_id}"}}
            )
            print('\033[32m'+'AI_response: ')
            for chunk in response:
                print(chunk , end='', flush=True)
            print('\033[0m'+'\n')

        except Exception as e:
            raise ValueError(f"LLM wrong! Error:{e}")

    # Asynchronous print AI's response to dict
    def __Asyncio2buffer__(self,
                           chain_with_message_history,
                           user_input,
                           file_message:tp.Optional[str]=None) -> dict:
        try:
            # 获取异步流
            response = chain_with_message_history.astream(
                input={"identity": self.agentIdentity, "file_message": file_message, "user_input": user_input},
                config={"configurable": {"session_id": f"UserSession NO.{self.session_id}"}}
            )
            # 执行异步流
            result = asyncio.run(self.__AsyncioPrintResponseStream2buffer__(response))
            return result
        except Exception as e:
            raise ValueError(f"LLM wrong! Error:{e}")

    # Synchronous print AI's response to dict
    def __Syncio2buffer__(self,
                          chain_with_message_history,
                          user_input,
                          file_message:tp.Optional[str]=None) -> dict:
        result = dict()
        str_buffer = str()

        try:
            # 获取同步流
            response = chain_with_message_history.stream(
                input={"identity": self.agentIdentity, "file_message": file_message, "user_input": user_input},
                config={"configurable": {"session_id": f"UserSession NO.{self.session_id}"}}
            )
            for chunk in response:
                str_buffer += chunk
            result['ai_context'] = str_buffer
            return result
        except Exception as e:
            raise ValueError(f"LLM wrong! Error:{e}")
    

    @property
    def agentName(self):
        return self.agent_name

    @property
    def agentIdentity(self):
        return self.agent_identity

    @property
    def agentTemperature(self):
        return self.temperature

    @property
    def agentApi(self):
        return self.llm_api

    @property
    def agent_Max_session_number(self):
        return self.max_session_number

    @property
    def agent_Max_history_number(self):
        return self.max_history_number

    @property
    def llm_base_url(self):
        return self.llm_url

    @property
    def llm_session_history(self):
        return self.store

    @property
    def llm_session_id(self):
        return self.session_id

    @property
    def allProperty(self):
        return {
            "agent_name":self.agentName, "agent_identity":self.agentIdentity,
            "output_temperature":self.temperature, "api_key":self.llm_api,
            "agent_max_session_number":self.max_session_number,
            "agent_max_history_number":self.max_history_number,
            "llm_base_url":self.llm_url
        }

    @abstractmethod
    def chatStream_2Terminal(self,*args,**kwargs):
        pass

    @abstractmethod
    def chatStream_2Buffer(self,*args,**kwargs):
        pass

    @abstractmethod
    def loadTools(self,*args,**kwargs):
        pass

    @abstractmethod
    def executionTool(self,*args,**kwargs):
        pass

class __ChatMessageHistory__(BaseChatMessageHistory):
    def __init__(self) -> None:
        super().__init__()
        self.messages: list[HumanMessage|AIMessage] = []
    
    def clear(self):
        self.messages: list[HumanMessage|AIMessage] = []
    
    def add_message(self, message):
        super().add_messages(message)
    
    def get_messages(self) -> list[HumanMessage|AIMessage]:
        return self.messages

    def add_user_message(self, message):
        self.messages.append(HumanMessage(content=message))

    def add_ai_message(self, message):
        self.messages.append(AIMessage(content=message))
