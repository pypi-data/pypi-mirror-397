# pylint: disable=broad-exception-caught
"""
Module for constructing AI messages based on configuration and templates.

This module provides functions to build lists of messages for AI interactions,
handling initial system and user messages, as well as additional messages
from various sources like frontmatter, files, or direct content.
"""

import os
import json
import importlib.resources
import yaml
from jinja2 import Template
from coauthor.utils.jinja import render_template, template_exists, prompt_template_path, render_content
from coauthor.utils.match_utils import file_submit_to_ai
from coauthor.utils.markdown import get_frontmatter_nested_value
from coauthor.modules.tools import execute_tool
from coauthor.utils.config import get_projects


def ai_messages(config, logger):
    """
    Construct and return a list of AI messages based on the configuration.

    This function initializes a list of messages, adds initial system and user
    messages, and then appends any additional messages specified in the task.

    Args:
        config (dict): Configuration dictionary containing the current task.
        logger (Logger): Logger instance for logging messages.

    Returns:
        list: A list of message dictionaries, each with 'role' and 'content'.
    """
    messages = []
    if not add_initial_messages(messages, config, logger):
        return []
    add_additional_messages(messages, config, logger)
    return messages


def add_initial_messages(messages, config, logger):
    """
    Add initial system and user messages to the messages list.

    This function retrieves and renders templates for system and user roles,
    appending them to the messages list if content is available.

    Args:
        messages (list): List to which messages will be appended.
        config (dict): Configuration dictionary containing the current task.
        logger (Logger): Logger instance for logging messages.

    Returns:
        bool: True if both messages were added successfully, False otherwise.
    """
    task = config["current-task"]
    for role in ["system", "user"]:
        path_template = prompt_template_path(config, f"{role}.md", logger)
        task[f"{role}_template_path"] = path_template
        content = ai_message_content(config, logger, path_template, role)
        if content:
            messages.append({"role": role, "content": content})
        else:
            logger.error("Message content missing!")
            return False
    return True


def add_additional_messages(messages, config, logger):
    """
    Add additional user messages to the messages list based on task configuration.

    This function processes additional messages specified in the task, rendering
    their content and appending them as user messages.

    Args:
        messages (list): List to which messages will be appended.
        config (dict): Configuration dictionary containing the current task.
        logger (Logger): Logger instance for logging messages.
    """
    task = config["current-task"]
    if "messages" not in task:
        return
    for msg in task["messages"]:
        logger.debug(f"message: {msg}")
        items = get_message_items(msg, task, config, logger)
        for item in items:
            if item is not None:
                if "frontmatter" in msg:
                    task["frontmatter-item"] = item
                elif "files" in msg:
                    task["user-message-context-file"] = item
            content = get_additional_message_content(msg, config, logger, task)
            if content:
                logger.info(f"Adding user message: {msg}")
                messages.append({"role": "user", "content": content})
            else:
                logger.error("Missing content for additional user message")


def get_message_items(msg, task, config, logger):
    """
    Retrieve items based on the message configuration.

    If the message specifies a frontmatter key, this function fetches the
    corresponding list from the task's frontmatter. If 'files' is specified,
    it renders the directory path and lists all files in that directory.

    Args:
        msg (dict): Message dictionary potentially containing 'frontmatter' or 'files' key.
        task (dict): Task dictionary containing frontmatter data.
        config (dict): Configuration dictionary.
        logger (Logger): Logger instance for logging messages.

    Returns:
        list: List of items from frontmatter or files, or [None] if not specified.
    """
    if "frontmatter" in msg:
        frontmatter_key = msg["frontmatter"]
        frontmatter_list = get_frontmatter_nested_value(task["path-modify-event"], frontmatter_key)
        if frontmatter_list is None or not frontmatter_list:
            return []
        return frontmatter_list
    if "files" in msg:
        try:
            template_path = msg["files"]
            dir_path = render_content(task, template_path, config, logger)
            logger.debug(f"Looking for files in dir_path: {dir_path}")
        except Exception as exception_error:
            logger.error(f"Failed to render files path: {exception_error}")
            return []
        if not os.path.isdir(dir_path):
            logger.error(f"Directory does not exist: {dir_path}")
            return []
        files = []
        for root, _dirs, filenames in os.walk(dir_path):
            for filename in filenames:
                full = os.path.join(root, filename)
                files.append(full)
        logger.debug(f"Files to include as user message: {', '.join(files)}")
        return files
    return [None]


def get_additional_message_content(msg, config, logger, task):
    """
    Generate content for an additional message.

    This function retrieves content either from a file template or by rendering
    a Jinja2 template string provided in the message.

    Args:
        msg (dict): Message dictionary with 'file' or 'content' for sourcing.
        config (dict): Configuration dictionary.
        logger (Logger): Logger instance for logging messages.
        task (dict): Current task dictionary.

    Returns:
        str or None: The rendered message content, or None if rendering fails.
    """
    content = None
    if "file" in msg:
        path_template = msg["file"]
        content = ai_message_content(config, logger, path_template, "user")
    elif "content" in msg:
        template_string = msg["content"]
        try:
            template = Template(template_string)
            content = template.render(task=task, config=config)
        except Exception as exception_error:
            logger.error(f"Failed to render content: {exception_error}")
            content = None
    else:
        logger.error("Message has neither 'file' nor 'content'")
    return content


def ai_message_content(config, logger, path_template, system_or_user):
    """
    Retrieve or render content for an AI message.

    This function checks for template existence and renders it, falls back to
    task data, or uses file content for user messages in modify events.

    Args:
        config (dict): Configuration dictionary containing the current task.
        logger (Logger): Logger instance for logging messages.
        path_template (str): Path to the template file.
        system_or_user (str): Role of the message ('system' or 'user').

    Returns:
        str or None: The message content, or None if not found.
    """
    task = config["current-task"]
    message_content = None
    if template_exists(task, path_template, config, logger):
        message_content = render_template(task, path_template, config, logger)
    elif system_or_user in task:
        message_content = task[system_or_user]
    elif "path-modify-event" in task and system_or_user == "user":
        logger.info(f"Using the file {task['path-modify-event']} as the user message")
        message_content = file_submit_to_ai(config, logger)
    return message_content


def _get_profile_examples(profile_name: str, logger):
    """Return examples from a profile's config.yml, normalized to a list of dicts."""
    if not profile_name:
        return []
    try:
        profile_config_resource = importlib.resources.files("coauthor.profiles")
        profile_config_resource = profile_config_resource.joinpath(profile_name).joinpath("config.yml")
        with importlib.resources.as_file(profile_config_resource) as profile_config_path:
            if not os.path.exists(profile_config_path):
                return []
            with open(profile_config_path, "r", encoding="utf-8") as f:
                profile_config = yaml.safe_load(f) or {}

        examples = profile_config.get("examples") or []
        normalized = []
        for example in examples:
            if isinstance(example, str):
                normalized.append({"name": example, "description": ""})
            elif isinstance(example, dict):
                name = example.get("name")
                if not name:
                    continue
                normalized.append({"name": name, "description": example.get("description", "")})
        return normalized
    except Exception as exception_error:
        logger.error(f"Failed to read profile examples for profile {profile_name}: {exception_error}")
        return []


def _get_project_examples(project_path: str):
    """Return examples from a project's .coauthor/examples directory."""
    examples_dir = os.path.join(project_path, ".coauthor", "examples")
    if not os.path.isdir(examples_dir):
        return []

    examples = []
    for filename in sorted(os.listdir(examples_dir)):
        full_path = os.path.join(examples_dir, filename)
        if os.path.isfile(full_path) and filename.lower().endswith(".md"):
            examples.append(
                {
                    "name": filename,
                    "description": "Example stored in the project under .coauthor/examples",
                }
            )
    return examples


def insert_projects_status_message(messages, config, logger):
    """
    Insert a user message with project information including Git status into the messages list.

    This function retrieves project details, fetches modified files for each project using
    the list_modified_files tool, constructs a JSON-formatted string of project infos,
    and inserts it as a user message before the first existing user message.

    Args:
        messages (list): List of message dictionaries to modify.
        config (dict): Configuration dictionary.
        logger (Logger): Logger instance for logging messages.
    """
    projects = config.get("all_projects", get_projects(config))
    project_infos = []
    for project in projects:
        project_name = project.get("name")
        project_path = os.path.expanduser(project.get("path", os.getcwd()))
        profile_name = project.get("profile")

        info = {
            "name": project_name,
            "type": project.get("type"),
            "description": project.get("description"),
            "examples": _get_profile_examples(profile_name, logger),
        }

        info["examples"].extend(_get_project_examples(project_path))
        logger.debug(f"info: {info}")
        if project_path == "none":
            info["note"] = "This project has no files."
        else:
            try:
                modified_files = execute_tool(config, "list_modified_files", {"project_name": project_name}, logger)
            except Exception as exception_error:
                logger.error(f"Failed to get modified files for {project_name}: {exception_error}")
                modified_files = []
            info["modified_files"] = modified_files

        project_infos.append(info)

    projects_content = f"Information about the projects:\n{json.dumps(project_infos, indent=2)}"
    projects_message = {"role": "user", "content": projects_content}

    insert_index = 0
    for i, msg in enumerate(messages):
        if msg["role"] == "user":
            insert_index = i
            break
    else:
        insert_index = len(messages)
    messages.insert(insert_index, projects_message)
