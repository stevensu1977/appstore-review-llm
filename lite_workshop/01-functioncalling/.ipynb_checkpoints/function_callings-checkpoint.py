import sys
from defusedxml import ElementTree
from collections import defaultdict
import os
from typing import Any
import tools
import boto3
import json
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), os.pardir)))

def create_prompt(tools_string, user_input):
    prompt_template = f"""
In this environment you have access to a set of tools you can use to answer the user's question. Your answer must be english.

You may call them like this. Only invoke one function at a time and wait for the results before invoking another function:
<function_calls>
<invoke>
<tool_name>$TOOL_NAME</tool_name>
<parameters>
<$PARAMETER_NAME>$PARAMETER_VALUE</$PARAMETER_NAME>
...
</parameters>
</invoke>
</function_calls>

Here are the tools available:
<tools>
{tools_string}
</tools>

Human:
{user_input}


Assistant:
"""
    return prompt_template

def add_tools():
    tools_string = ""
    for tool_spec in tools.list_of_tools_specs:
        tools_string += tool_spec
    return tools_string

def call_function(tool_name, parameters):
    func = getattr(tools, tool_name)
    print(tool_name,parameters,func)
    output = func(**parameters)
    return output

def format_result(tool_name, output):
    return f"""
<function_results>
<result>
<tool_name>{tool_name}</tool_name>
<stdout>
{output}
</stdout>
</result>
</function_results>
"""

def etree_to_dict(t) -> dict[str, Any]:
    d = {t.tag: {}}
    children = list(t)
    if children:
        dd = defaultdict(list)
        for dc in map(etree_to_dict, children):
            for k, v in dc.items():
                dd[k].append(v)
        d = {t.tag: {k: v[0] if len(v) == 1 else v for k, v in dd.items()}}
    if t.attrib:
        d[t.tag].update(("@" + k, v) for k, v in t.attrib.items())
    if t.text and t.text.strip():
        if children or t.attrib:
            d[t.tag]["#text"] = t.text
        else:
            d[t.tag] = t.text
    return d


system_prompt = f"""
You have access to an additional set of one or more functions you can use to 
answer the user's question.

You may call them like this:
<function_calls>
    <invoke>
        <tool_name>$TOOL_NAME</tool_name>
        <parameters>
            <$PARAMETER_NAME>$PARAMETER_VALUE</$PARAMETER_NAME>
            ...
        </parameters>
    </invoke>
</function_calls>

Here are the tools available:
<tools>......</tools>
Your final answer should be of the form 'The current temperature in <location> is <temp> degrees, windspeed is km/h' 
Your final answer should use Chinese
"""


def run_loop(prompt):
    # Start function calling loop
    while True:
    # initialize variables to make bedrock api call
        bedrock = boto3.client(service_name='bedrock-runtime',region_name="us-east-1")
        modelId = 'anthropic.claude-3-sonnet-20240229-v1:0'
       

        body = json.dumps({
        "anthropic_version":"bedrock-2023-05-31",
        "system": system_prompt,
        "messages": [{'role': 'user', 'content': prompt}],
        "stop_sequences":["\n\nHuman:", "</function_calls>"],
        "max_tokens": 2048,
        "temperature": 0})

        accept = 'application/json'
        contentType = 'application/json'
        # bedrock api call with prompt
        partial_completion = bedrock.invoke_model(
        body=body, 
        modelId=modelId, 
        accept=accept, 
        contentType=contentType
        )
   
        response_body = json.loads(partial_completion.get('body').read())

        for content in response_body.get('content'):
            if content.get("type")=="text":
                print(content["text"])
                partial_completion=content["text"]
        stop_reason=response_body.get('stop_reason')
        stop_seq = partial_completion.rstrip().endswith("</invoke>")

        print(response_body)
        
        # Get a completion from Claude

        # Append the completion to the end of the prommpt
        prompt += partial_completion
        if stop_reason == 'stop_sequence' and stop_seq:
            # If Claude made a function call
            print(partial_completion)
            start_index = partial_completion.find("<function_calls>")
            if start_index != -1:
                # Extract the XML Claude outputted (invoking the function)
                extracted_text = partial_completion[start_index+16:]

                # Parse the XML find the tool name and the parameters that we need to pass to the tool
                print(f"{extracted_text=}")
                xml = ElementTree.fromstring(extracted_text)
                tool_name_element = xml.find("tool_name")
                if tool_name_element is None:
                    print("Unable to parse function call, invalid XML or missing 'tool_name' tag")
                    break
                tool_name_from_xml = tool_name_element.text.strip()
                parameters_xml = xml.find("parameters")
                if parameters_xml is None:
                    print("Unable to parse function call, invalid XML or missing 'parameters' tag")
                    break
                param_dict = etree_to_dict(parameters_xml)
                parameters = param_dict["parameters"]

                # Call the tool we defined in tools.py
                output = call_function(tool_name_from_xml, parameters)

                # Add the stop sequence back to the prompt
                prompt += "</function_calls>"
                print("</function_calls>")

                # Add the result from calling the tool back to the prompt
                function_result = format_result(tool_name_from_xml, output)
                print(function_result)
                prompt += function_result
        else:
            # If Claude did not make a function call
            # outputted answer
            print("\n\nFinal Answer:",partial_completion)
            break

user_input = "Can you check the weather for me in Paris, France?"
user_input = "你能帮我查询一下英国伦敦的天气吗?"

tools_string = add_tools()
prompt = create_prompt(tools_string, user_input)
run_loop(prompt)