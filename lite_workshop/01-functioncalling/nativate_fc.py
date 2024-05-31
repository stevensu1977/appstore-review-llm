# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
"""
Shows how to use tools with the Conversation API and the Claude3 model.
"""

import logging
import boto3


from botocore.exceptions import ClientError


class StationNotFoundError(Exception):
    """Raised when a radio station isn't found."""
    pass


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def get_top_song(call_sign):
    """Returns the most popular song for the requested station.
    Args:
        call_sign (str): The call sign for the station for which you want
        the most popular song.

    Returns:
        response (json): The most popular song and artist.
    """

    song = ""
    artist = ""
    if call_sign == 'WZPZ':
        song = "Elemental Hotel"
        artist = "8 Storey Hike"

    else:
        raise StationNotFoundError(f"Station {call_sign} not found.")

    return song, artist


def generate_text(bedrock_client, model_id, tool_config, input_text):
    """Generates text using the supplied Amazon Bedrock model. If necessary,
    the function handles tool use requests and sends the result to the model.
    Args:
        bedrock_client: The Boto3 Bedrock runtime client.
        model_id (str): The Amazon Bedrock model ID.
        tool_config (dict): The tool configuration.
        input_text (str): The input text.
    Returns:
        Nothing.
    """

    logger.info("Generating text with model %s", model_id)

   # Create the initial message from the user input.
    messages = [{
        "role": "user",
        "content": [{"text": input_text}]
    }]

    response = bedrock_client.converse(
        modelId=model_id,
        messages=messages,
        toolConfig=tool_config
    )

    output_message = response['output']['message']
    messages.append(output_message)
    stop_reason = response['stopReason']

    if stop_reason == 'tool_use':
        # Tool use requested. Call the tool and send the result to the model.
        tool_requests = response['output']['message']['content']
        for tool_request in tool_requests:
            if 'toolUse' in tool_request:
                tool = tool_request['toolUse']
                logger.info("Requesting tool %s. Request: %s",
                            tool['name'], tool['toolUseId'])

                if tool['name'] == 'top_song':
                    tool_result = {}
                    try:
                        song, artist = get_top_song(tool['input']['sign'])
                        tool_result = {
                            "toolUseId": tool['toolUseId'],
                            "content": [{"json": {"song": song, "artist": artist}}]
                        }
                    except StationNotFoundError as err:
                        tool_result = {
                            "toolUseId": tool['toolUseId'],
                            "content": [{"text":  err.args[0]}],
                            "status": 'error'
                        }

                    tool_result_message = {
                        "role": "user",
                        "content": [
                            {
                                "toolResult": tool_result

                            }
                        ]
                    }
                    messages.append(tool_result_message)

                    # Send the tool result to the model.
                    response = bedrock_client.converse(
                        modelId=model_id,
                        messages=messages,
                        toolConfig=tool_config
                    )
                    output_message = response['output']['message']

    # print the final response from the model.
    for content in output_message['content']:
        print(f"{content['text']}")


def main():
    """
    Entrypoint for tool use example.
    """

    logging.basicConfig(level=logging.INFO,
                        format="%(levelname)s: %(message)s")

    model_id = "anthropic.claude-3-haiku-20240307-v1:0"
    input_text = "What is the most popular song on WZPZ?"

    tool_config = {
    "tools": [
        {
            "toolSpec": {
                "name": "top_song",
                "description": "Get the most popular song played on a radio station.",
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {
                            "sign": {
                                "type": "string",
                                "description": "The call sign for the radio station for which you want the most popular song. Example calls signs are WZPZ, and WKRP."
                            }
                        },
                        "required": [
                            "sign"
                        ]
                    }
                }
            }
        }
    ]
}
    bedrock_client = boto3.client(service_name='bedrock-runtime',region_name='us-east-1')

    try:
        print(f"Question: {input_text}")
        generate_text(bedrock_client, model_id, tool_config, input_text)

    except ClientError as err:
        message = err.response['Error']['Message']
        logger.error("A client error occurred: %s", message)
        print(f"A client error occured: {message}")

    else:
        print(
            f"Finished generating text with model {model_id}.")


if __name__ == "__main__":
    main()

