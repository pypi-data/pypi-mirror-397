import os
import re
import traceback
import json
import datetime
from openai import OpenAI
from httpx import Client
from coauthor.utils.ai_utils import ai_messages, insert_projects_status_message
from coauthor.modules.tools import execute_tool, load_tools
from coauthor.modules.request_history import save_messages, save_response, next_ai_request_id, next_ai_workflow_id
from coauthor.utils.config import get_projects


def get_api_credentials(agent):
    if "api_key" in agent:
        api_key = agent["api_key"]
    else:
        api_key = os.getenv(agent["api_key_var"])
    if "api_url" in agent:
        api_url = agent["api_url"]
    else:
        api_url = os.getenv(agent["api_url_var"])
    return api_url, api_key


def create_chat_completion_submit(
    config, client, messages, model, tools, tool_choice, logger, workflow_id=None, json_mode=False
):
    kwargs = {}
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}
    if tools:
        kwargs["tools"] = tools
        kwargs["tool_choice"] = tool_choice
    api_url, _api_key = get_api_credentials(config["agent"])
    logger.debug(f"kwargs: {kwargs}")
    # save_messages(messages, logger)
    start_time = datetime.datetime.now()
    request_id = next_ai_request_id()
    logger.info(f"Submit AI request {request_id} {len(messages)} messages to {api_url} / {model}")
    save_messages(messages, model, kwargs, logger, workflow_id)
    response = client.chat.completions.create(messages=messages, model=model, **kwargs)
    save_response(response, logger, workflow_id)
    end_time = datetime.datetime.now()
    duration = (end_time - start_time).seconds
    logger.info(f"Response for {request_id} received after {duration} seconds")
    message = response.choices[0].message
    tool_calls = message.tool_calls
    content = message.content.strip() if message.content else None
    return tool_calls, content, message


def is_duplicate_tool_call(messages, tool_call):
    tool_name = tool_call.function.name
    arguments = tool_call.function.arguments
    # Find the most recent previous assistant message
    for msg in reversed(messages):
        if msg["role"] == "assistant" and "tool_calls" in msg:
            for prev_tool_call in msg["tool_calls"]:
                prev_name = prev_tool_call["function"]["name"]
                prev_args = prev_tool_call["function"]["arguments"]
                if prev_name == tool_name and prev_args == arguments:
                    return True
            return False  # Checked the most recent, no match, not duplicate
    return False  # No previous assistant found


def has_context_message(messages, project=None):
    if project is None:
        for msg in messages:
            if msg["role"] == "user" and "Project context from COAUTHOR.md" in msg["content"]:
                return True
    else:
        for msg in messages:
            if msg["role"] == "user" and f"Project context for {project} from COAUTHOR.md" in msg["content"]:
                return True
    return False


def create_chat_completion(config, client, messages, logger, tools=None, workflow_id=None, json_mode=False):
    model = config["agent"]["model"]
    task = config["current-task"]
    tool_choice = task.get("tool_choice", "auto")
    # logger.debug(f"Messages before submit: {messages}")
    # logger.debug(f"Tools before submit: {tools}")

    try:
        tool_calls, content, message = create_chat_completion_submit(
            config, client, messages, model, tools, tool_choice, logger, workflow_id, json_mode
        )

        if tool_calls:
            # Append the assistant's message including tool_calls
            assistant_message = {
                "role": "assistant",
                "content": content,
                "tool_calls": [tc.model_dump() for tc in tool_calls],
            }
            messages.append(assistant_message)

            tool_results = []
            for tool_call in tool_calls:
                tool_name = tool_call.function.name
                if is_duplicate_tool_call(messages[:-1], tool_call):  # Check previous messages
                    logger.error(
                        f"Duplicate tool call detected: {tool_name} with arguments {tool_call.function.arguments}"
                    )
                    tool_results.append(
                        {
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": tool_name,
                            "content": "Duplicate tool call skipped. This call was already executed.",
                        }
                    )
                    continue

                tool_def = next((t for t in tools if t["function"]["name"] == tool_name), None)
                if tool_def is None:
                    raise ValueError(f"Tool definition not found for {tool_name}")
                result = execute_tool(
                    config,
                    tool_name,
                    json.loads(tool_call.function.arguments),
                    logger,
                )
                tool_content = json.dumps(result) if result is not None else '{"status": "success"}'
                tool_results.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": tool_name,
                        "content": tool_content,
                    }
                )
                logger.debug(f"Executed tool: {tool_name} with result: {result}")

            messages.extend(tool_results)

            # Collect unique projects from tool calls
            unique_projects = set()
            for tc in tool_calls:
                args = json.loads(tc.function.arguments)
                project = args.get("project_name")
                if project:
                    unique_projects.add(project)

            # Add context for each project if not already present
            for project in unique_projects:
                if not has_context_message(messages, project):
                    try:
                        context = execute_tool(config, "get_context", {"project_name": project}, logger)
                        context_message = {
                            "role": "user",
                            "content": f"Project context for {project} from COAUTHOR.md:\n{context}",
                        }
                        messages.append(context_message)
                    except Exception as error:
                        logger.error(f"Failed to get context for {project}: {error}")

            return create_chat_completion(
                config, client, messages, logger, tools=tools, workflow_id=workflow_id, json_mode=True
            )  # Recurse for final response

        # if content.startswith("```") and content.endswith("```"):
        #     content = "\n".join(content.splitlines()[1:-1]).strip()

        # write_response_to_yaml(config, messages, model, content, logger, duration)
        return content

    except Exception as error:
        logger.error(f"Error: {error}")
        logger.error(traceback.format_exc())
        raise


def process_with_openai_agent(config, logger):
    """Submit content to OpenAI API for processing."""
    task = config["current-task"]
    workflow = config["current-workflow"]
    logger.info(
        f"Preparing AI processing for workflow {workflow['name']} task {task['id']} using model {config['agent']['model']}"
    )
    agent = config["agent"]
    logger.debug(f"agent: {agent}")

    # Load tools from tools.yml
    tools = load_tools()

    api_url, api_key = get_api_credentials(agent)
    logger.debug(f"api_url: {api_url}, api_key: {api_key}")

    disable_ssl = agent.get("disable_ssl_verification", False)
    http_client = Client(verify=not disable_ssl) if disable_ssl else None

    client = OpenAI(api_key=api_key, base_url=api_url, http_client=http_client)

    workflow_id = next_ai_workflow_id()

    messages = ai_messages(config, logger)
    # logger.debug(f"messages: {messages}")

    context_message = (
        "To get necessary context for working on a project,"
        "especially if you intend to change files of the project,"
        "use the tool get_context. And if you learn from interactions,"
        "update the project context using tool update_context."
    )

    system_context = {"role": "system", "content": context_message}
    insert_context_index = 0
    for i, msg in enumerate(messages):
        if msg["role"] == "system":
            insert_context_index = i + 1
        else:
            break
    messages.insert(insert_context_index, system_context)

    # Insert projects status message
    insert_projects_status_message(messages, config, logger)

    if not messages:
        logger.error("No messages to submit to AI")
        return
    for message in messages:
        log_message = re.sub(r"[\r\n]+", " ", message["content"])[:100]
        logger.info(f"{message['role']} → {log_message}")

    content = create_chat_completion(config, client, messages, logger, tools=tools, workflow_id=workflow_id)
    return content


def process_file_with_openai_agent(config, logger):  # TODO replace this with process with AI
    """Submit file to OpenAI API for processing."""
    task = config["current-task"]
    task["response"] = process_with_openai_agent(config, logger)
    return task["response"]
