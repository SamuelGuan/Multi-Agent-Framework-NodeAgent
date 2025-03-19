import csv
import json
import math
from BaseTool import BaseToolProtocol

class StrFileReadTool(BaseToolProtocol):

    '''
    Just for str file, an example of how to program an Agent tool.
    You can customize your tools with father class 'BaseTool'
    and remember to define the function '_run(self, args)',
    don't forget the properties 'name' and 'description'
    '''

    name:str = "str_file_parser_tool"
    purposes:str = "a tool for parsing csv or json files to abstracting the content"
    args_dict:dict = {'file_path':str()}
    input_format:str = "where the file is stored in your computer"
    output_format:str = "str"

    def run(self, args_dict:dict) -> str:
        return self.parseTheFile(**args_dict)

    def getToolInfo(self)->dict:
        return {"name":self.name, "purposes":self.purposes,
                "args_dict":self.args_dict, "output_format":self.output_format}

    def parseTheFile(self, file_path:str)->str:
        '''
        only support local file, parameter 'file' is the file_path,
        recommend absolute file path
        '''

        # check the file format is valid or not.
        # valid file formats list is csv and json.
        state = self.__judgeFileValid__(file_path)
        if not state[0]:
            raise ValueError(state[1])

        file_context = ''
        if state[1] == 'csv':
            with open(file_path, 'r', encoding='UTF-8') as f:
                csv_reader = csv.reader(f)
                for row in csv_reader:
                    for word in row:
                        file_context = file_context + word
        else:
            with open(file_path, 'r') as f:
                json_data = json.load(f)
                if not isinstance(json_data, dict):
                    raise ValueError("json file format error! Lost key 'str_context'")
                file_context += str(json_data['str_context'])

        return file_context

    def __judgeFileValid__(self, file:str)->tuple:
        '''
        check the file format is valid or not.
        only can be used by method 'parseTheFile'
        '''
        try:
            with open(file, 'r') as f:
                csv.reader(f)
            return (True, 'csv')
        except csv.Error:
            try:
                with open(file, 'r') as f:
                    json.load(f)
                return (True, 'json')
            except json.JSONDecodeError as e:
                return (False, 'Invalid file format!')


class Plus(BaseToolProtocol):
    '''
    an example for agents who can use many tool to complete the task
    '''

    name: str = "numeric_plus"
    purposes: str = "calculate the big number with operator '+'  "
    args_dict: dict = {'num1':float(), 'num2':float()}
    output_format: str = "float"

    def run(self, num1: float, num2:float) -> float:
        return num1 + num2

    def getToolInfo(self) -> dict:
        return {"name":self.name, "purposes":self.purposes,
                "args_dict":self.args_dict, "output_format":self.output_format}


class Sub(BaseToolProtocol):
    '''
    an example for agents who can use many tool to complete the task
    '''

    name: str = "numeric_sub"
    purposes: str = "calculate the big number with operator '-'  "
    args_dict: dict = {'num1': float(), 'num2': float()}
    output_format: str = "float"

    def run(self, num1: float, num2: float) -> float:
        return num1 - num2

    def getToolInfo(self) -> dict:
        return {"name": self.name, "purposes": self.purposes,
                "args_dict": self.args_dict, "output_format": self.output_format}

class Mul(BaseToolProtocol):
    '''
    an example for agents who can use many tool to complete the task
    '''

    name: str = "numeric_mul"
    purposes: str = "calculate the big number with operator '*'  "
    args_dict: dict = {'num1': float(), 'num2': float()}
    output_format: str = "float"

    def run(self, num1: float, num2: float) -> float:
        return num1 * num2

    def getToolInfo(self) -> dict:
        return {"name": self.name, "purposes": self.purposes,
                "args_dict": self.args_dict, "output_format": self.output_format}

class Div(BaseToolProtocol):
    '''
    an example for agents who can use many tool to complete the task
    '''

    name: str = "numeric_div"
    purposes: str = "calculate the big number with operator '/'  "
    args_dict: dict = {'num1': float(), 'num2': float()}
    output_format: str = "float"

    def run(self, num1: float, num2: float) -> float:
        return num1 / num2

    def getToolInfo(self) -> dict:
        return {"name": self.name, "purposes": self.purposes,
                "args_dict": self.args_dict, "output_format": self.output_format}

class Pow(BaseToolProtocol):
    '''
    an example for agents who can use many tool to complete the task
    '''

    name: str = "numeric_pow"
    purposes: str = "calculate the big number with operator '^', which means power operator"
    args_dict: dict = {'num1': float(), 'num2': float()}
    output_format: str = "float"

    def run(self, num1: float, num2: float) -> float:
        return num1**num2

    def getToolInfo(self) -> dict:
        return {"name": self.name, "purposes": self.purposes,
                "args_dict": self.args_dict, "output_format": self.output_format}

class Log(BaseToolProtocol):
    '''
    an example for agents who can use many tool to complete the task
    '''

    name: str = "numeric_log"
    purposes: str = "calculate the logarithm of num1 to the base num2"
    args_dict: dict = {'num1': float(), 'num2': float()}
    output_format: str = "float"

    def run(self, num1: float, num2: float) -> float:
        return math.log(num1)/math.log(num2)

    def getToolInfo(self) -> dict:
        return {"name": self.name, "purposes": self.purposes,
                "args_dict": self.args_dict, "output_format": self.output_format}


class SearchOnInternet(BaseToolProtocol):
    '''
    an example for agents who can use many tool to complete the task
    '''

    name: str = "search_on_internet"
    purposes: str = "search the information on the internet"
    args_dict: dict = {'url': str()}
    output_format: str = ""

    def run(self, url:str) -> float:
        raise ValueError("Tool is not defined!")

    def getToolInfo(self) -> dict:
        return {"name": self.name, "purposes": self.purposes,
                "args_dict": self.args_dict, "output_format": self.output_format}


class ManipulateSQL(BaseToolProtocol):
    '''
    an example for agents who can use many tool to complete the task
    '''

    name: str = "Manipulate_SQL"
    purposes: str = "use the SQL Server with mode in [add, delete, update, search] by the SQL"
    args_dict: dict = {'mode': str(), 'SQL':str()}
    output_format: bool = "True or False"

    def run(self, mode:str, SQL:str) -> float:
        raise ValueError("Tool is not defined!")

    def getToolInfo(self) -> dict:
        return {"name": self.name, "purposes": self.purposes,
                "args_dict": self.args_dict, "output_format": self.output_format}
