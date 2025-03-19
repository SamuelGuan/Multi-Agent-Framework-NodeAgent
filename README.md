# Multi-Agent-Framework-NodeAgent
This is an light Open Multi-Agent Framework base on LangChain.
specially designed for CN researchers, but everyone
can customize this framework into your piece of work.

My framework is friendly to langchain freshmen, I think you are able to use it. Followings are support function.

- Support chatting-bot
- Support history message management
- Support session number management
- Support single agent
- Support Agent Tool Call
- Support Multi-Agent workflow
- Support Input message from keyboard in multi-agent workflow
- Support multi-source parameters from different agent

Because of the different return message form and tool-called format is different from each other,
causing a big inconvenient to me when I want use different LLM from different Chinese company.
Nevertheless, LangChain's reference is so difficult to guide me on real study or other task.
when I search the lessons of LangChain/LangGraph on the Internet or ask AI to teach me to use them,
I am always confused by the combination of new version code and old version code. WHO CAN TOLERANT THIS??!!!!
So, I decide to make my own Multi-Agent Framework.

To keep the code flash, I maintain the python code style in my project and provide the huge extensible space.
I hope everyone can easily understand my code and customize your own framework base on this framework, so
instead of defensive style code, I use short code but still provide strong agent ability.


## Insights into the NodeAgent Framework

### Core Concept of GraphAgent

The main concept of GraphAgent is "one agent, one tool".
Agents can communicate with each other through Python strings
or any other form you design (I haven't designed this part and am looking forward to your coding implementation).

### Interface for Connecting Large Language Models from Different Platforms

This Python file is an interface for connecting large language models from different platforms.
Therefore, when developers create agents, they don't need to care about which type of API they are using,
which prompts them to focus on program development and shortens the product production time.
The only thing they need to do is "from Agent import ZHiPu_LLM/Deepseek, etc." and instantiate the agents with some properties.

### Ease of Use of AgentNode

AgentNode is also very easy to use.
Create a Large Language Model (LLM), put it into the AgentNode class, load the tool list into AgentNode,
and then call the agent, which will execute the tool automatically.

AgentNode is just a node and is not in any graph structure
because I hope AgentNode can be as easy to use as numpy.ndarray and torch.Tensor.
In this way, you can use Python keywords such as "if", "while", "for", etc. to construct complex workflows.

When the workflow is running, you can interact with the artificial intelligence by inputting content from your keyboard,
and you can also provide the output of other agents as input to the artificial intelligence when the workflow is running.
For specific details, you can check the original code in "MultiAgentComponents.py".

I think the most programming-friendly module design is to only provide preliminary modules that are short but powerful,
hide the trivial API call details, maintain the original Python programming style,
and simplify the use of the module without affecting other programmers' ability to modify the module.
As the saying goes: "Never guess what the user will do. Just give them something iconic and stimulate their creativity!"

### Agent Tool Design Idea

In my design idea, we should provide a tool list as a prompt for the tool-specific agent
so that the agent can choose one to return information about which tool to use.

In short, we give the agent a task and a tool list, and then the agent returns the name of the useful tool.
Then, iterate through the tool list to match the function (tool) and run the function locally.

I stipulate that in this framework, the way we communicate with the agent is all through "Prompt".
The format of the prompt is as follows:
```
{
    'system': your identity is {identity} and context reference {reference},
    'history': BaseChatMessageHistory,
    'humanMessage': {user_input}
}
```
Any "reference" should be provided in a specific format before chatting with the agent.

Here is an example emphasized with the "-" symbol:
```
"
- you should answer me in short word
- you should answer me in long word
- and so on
"
```
If you don't like the above design, you can modify it in the BaseAgent class in BaseAgent.py.
If you call the llm.loadTools() function, it will call the "getToolInfo" function defined in the tool,
which will generate a tool list in string format containing the properties "tool_name", "purposes", and "args_dict".
This string variable will be combined with a special prompt as {reference} to facilitate the agent to identify these tools
and return the tool name so that we can run the tool.

### Design Related to Asynchrony

    I have designed some basic properties and functions for asynchrony. Since I'm not sure about your style of thread management,
I haven't taken further actions in this regard. If you need to, you can customize the asynchronous application by yourself.
