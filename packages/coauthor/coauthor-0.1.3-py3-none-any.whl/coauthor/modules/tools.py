# pylint: disable=broad-exception-caught
"""
Module for managing project files and executing tools on Git repositories.
"""

import os
import yaml
import subprocess
import shutil
from typing import Dict, List, Any
import importlib.resources
import re
from coauthor.utils.config import get_projects
import urllib.request


def list_tracked_files(project_path: str) -> List[str]:
    """List all tracked files in the Git repository at project_path."""
    try:
        result = subprocess.run(["git", "ls-files"], cwd=project_path, capture_output=True, text=True, check=True)
        if result.returncode != 0:
            raise ValueError(f"Error listing files: {result.stderr}")
        return result.stdout.splitlines()
    except Exception as exception_error:
        return [f"Error: {str(exception_error)}"]


def list_tracked_directories(project_path: str) -> List[str]:
    """List all directories that contain tracked files in the Git repository at project_path."""
    files = list_tracked_files(project_path)
    if files and isinstance(files[0], str) and files[0].startswith("Error:"):
        return files
    directories = set()
    for file in files:
        directory = os.path.dirname(file)
        while directory not in directories:
            directories.add(directory)
            if directory == "":
                break
            directory = os.path.dirname(directory)
    directories = {"." if d == "" else d for d in directories}
    return sorted(directories)


def write_file(project_path: str, path: str, content: str) -> None:
    """Write or update a single file in the project."""
    full_path = os.path.join(project_path, path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)


def write_files(project_path: str, files: List[Dict[str, str]]) -> None:
    """Write or update files in the project."""
    for file in files:
        write_file(project_path, file["path"], file["content"])


def get_files(project_path: str, paths: List[str]) -> Dict[str, str]:
    """Retrieve content of specified files."""
    contents = {}
    for path in paths:
        full_path = os.path.join(project_path, path)
        if os.path.exists(full_path):
            with open(full_path, "r", encoding="utf-8") as f:
                contents[path] = f.read()
        else:
            contents[path] = "File not found"
    return contents


def get_context(project_path: str) -> str:
    result = get_files(project_path, ["COAUTHOR.md"])
    return result.get("COAUTHOR.md", "No context found")


def update_context(project_path: str, content: str) -> Dict[str, str]:
    write_files(project_path, [{"path": "COAUTHOR.md", "content": content}])
    return {"status": "updated"}


def create_directories(project_path: str, directories: List[str]) -> None:
    """Create directories in the project, similar to mkdir -p."""
    for dir_path in directories:
        full_path = os.path.join(project_path, dir_path)
        os.makedirs(full_path, exist_ok=True)


def list_modified_files(project_path: str) -> List[str]:
    """List files with outstanding changes in the specified project path."""
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=project_path,
            capture_output=True,
            text=True,
            check=True,
        )
        lines = result.stdout.splitlines()
        modified = []
        for line in lines:
            if line:
                status = line[0:2]
                path = line[3:]
                if status in ("R ", "C "):
                    path = path.split(" -> ")[1]
                modified.append(path)
        return modified
    except Exception as exception_error:
        return [f"Error: {str(exception_error)}"]


def get_diffs(project_path: str, paths: List[str] = []) -> Dict[str, str]:
    """Retrieve diffs for specified files in the project path."""
    try:
        if paths:
            file_list = paths
        else:
            file_list = list_modified_files(project_path)
        if file_list and isinstance(file_list[0], str) and file_list[0].startswith("Error:"):
            return {"error": file_list[0]}
        diffs = {}
        for file in file_list:
            stat_res = subprocess.run(
                ["git", "status", "--porcelain", file],
                cwd=project_path,
                capture_output=True,
                text=True,
                check=False,
            )
            line = stat_res.stdout.strip()
            if not line:
                diffs[file] = "No changes"
                continue
            status = line[0:2]
            if status == "??":
                full_path = os.path.join(project_path, file)
                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        lines = f.read().splitlines()
                    diff = f"diff --git a/{file} b/{file}\n"
                    diff += "new file mode 100644\n"
                    diff += "index 0000000..e69de29\n"
                    diff += "--- /dev/null\n"
                    diff += f"+++ b/{file}\n"
                    diff += f"@@ -0,0 +1,{len(lines)} @@\n"
                    diff += "\n".join([f"+{l}" for l in lines]) + "\n"
                    diffs[file] = diff
                except Exception as exception_error:
                    diffs[file] = f"Error reading file: {str(exception_error)}"
            else:
                diff_res = subprocess.run(
                    ["git", "diff", "HEAD", file],
                    cwd=project_path,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                diffs[file] = diff_res.stdout or "No changes"
        return diffs
    except Exception as exception_error:
        return {"error": f"Error: {str(exception_error)}"}


def delete_files(project_path: str, paths: List[str]) -> Dict[str, str]:
    """Delete specified files or directories in the project."""
    results = {}
    for path in paths:
        full_path = os.path.join(project_path, path)
        try:
            if os.path.exists(full_path):
                if os.path.isdir(full_path):
                    shutil.rmtree(full_path)
                else:
                    os.remove(full_path)
                results[path] = "Deleted"
            else:
                results[path] = "Not found"
        except Exception as exception_error:
            results[path] = f"Error: {str(exception_error)}"
    return results


def move_files(project_path: str, moves: List[Dict[str, str]]) -> Dict[str, str]:
    """Move files or directories in the project."""
    results = {}
    for move in moves:
        source = os.path.join(project_path, move["source"])
        destination = os.path.join(project_path, move["destination"])
        try:
            if os.path.exists(source):
                os.makedirs(os.path.dirname(destination), exist_ok=True)
                shutil.move(source, destination)
                results[move["source"]] = f'Moved to {move["destination"]}'
            else:
                results[move["source"]] = "Source not found"
        except Exception as exception_error:
            results[move["source"]] = f"Error: {str(exception_error)}"
    return results


def search_files(
    project_path: str, query: str, is_regex: bool = False, context_lines: int = 0
) -> Dict[str, List[Dict[str, Any]]]:
    """Search for a query in tracked files of the project."""
    files = list_tracked_files(project_path)
    if isinstance(files, list) and files and isinstance(files[0], str) and files[0].startswith("Error:"):
        return {"error": [{"message": files[0]}]}
    results: Dict[str, List[Dict[str, Any]]] = {}
    for rel_path in files:
        full_path = os.path.join(project_path, rel_path)
        try:
            with open(full_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            matches = []
            for i, line in enumerate(lines):
                if (not is_regex and query in line) or (is_regex and re.search(query, line)):
                    match = {
                        "line_number": i + 1,
                        "match_line": line.strip(),
                    }
                    if context_lines > 0:
                        start = max(0, i - context_lines)
                        end = min(len(lines), i + context_lines + 1)
                        match["context"] = [lines[j].strip() for j in range(start, end) if j != i]
                    matches.append(match)
            if matches:
                results[rel_path] = matches
        except Exception as exception_error:
            if "error" not in results:
                results["error"] = []
            results["error"].append({"message": f"{rel_path}: {str(exception_error)}"})
    return results


def run_pytest(project_path: str, test_path: str) -> str:
    """Run Pytest on the specified test file in the project."""
    config_path = os.path.join(project_path, ".coauthor.yml")
    tool_env = ""
    tool_shell = None
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
            tool_env = config.get("tool_environment", "")
            tool_shell = config.get("tool_shell", None)

    cmd = tool_env.strip() + "\n" if tool_env else ""
    cmd += f"pytest {test_path}"

    run_kwargs = {
        "shell": True,
        "cwd": project_path,
        "capture_output": True,
        "text": True,
        "check": True,
    }
    if tool_shell:
        run_kwargs["executable"] = tool_shell

    try:
        result = subprocess.run(cmd, **run_kwargs)
        return result.stdout + result.stderr
    except subprocess.CalledProcessError as exception_error:
        return (
            f"Pytest failed with exit code {exception_error.returncode}:\n"
            f"{exception_error.stdout}{exception_error.stderr}"
        )
    except Exception as exception_error:
        return f"Error executing Pytest: {str(exception_error)}"


def get_url(url: str) -> str:
    """Fetch content from the specified URL."""
    try:
        with urllib.request.urlopen(url) as response:
            content = response.read().decode("utf-8")
            return content
    except Exception as exception_error:
        return f"Error fetching URL: {str(exception_error)}"


def _example_name_candidates(example_name: str) -> List[str]:
    """Return candidate example filenames.

    The preferred form is to use example_name as provided. For backwards
    compatibility, if the name has no .md extension, also try adding it.

    This prevents accidental double extensions like .md.md.
    """
    if not example_name:
        return []
    candidates = [example_name]
    if not example_name.lower().endswith(".md"):
        candidates.append(f"{example_name}.md")
    return candidates


def get_example(project_path: str, example_name: str) -> str:
    """Retrieve a specific example/template from the project or its profile."""
    # First, check project .coauthor/examples
    for candidate_name in _example_name_candidates(example_name):
        project_example_path = os.path.join(project_path, ".coauthor/examples", candidate_name)
        if os.path.exists(project_example_path):
            with open(project_example_path, "r", encoding="utf-8") as f:
                return f.read()

    # Get profile from config
    config_path = os.path.join(project_path, ".coauthor.yml")
    if not os.path.exists(config_path):
        return "No config found, cannot locate profile examples"
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    profile_name = config.get("profile")
    if not profile_name:
        return "No profile specified in config"

    # Find profile example using importlib.resources
    try:
        for candidate_name in _example_name_candidates(example_name):
            profile_resource = importlib.resources.files("coauthor.profiles").joinpath(
                profile_name, "examples", candidate_name
            )
            with importlib.resources.as_file(profile_resource) as profile_example_path:
                if os.path.exists(profile_example_path):
                    with open(profile_example_path, "r", encoding="utf-8") as f:
                        return f.read()
        return "No example found in profile"
    except Exception as exception_error:
        return f"Error: {str(exception_error)}"


def load_tools():
    tools_resource = importlib.resources.files("coauthor.config").joinpath("tools.yml")
    with importlib.resources.as_file(tools_resource) as tools_path:
        with open(tools_path, "r", encoding="utf-8") as f:
            tools_config = yaml.safe_load(f)["tools"]
    return [{"type": "function", "function": t} for t in tools_config]  # Format for OpenAI


def execute_tool(config, tool_name: str, params: Dict, logger) -> Any:
    """Execute a specified tool on a project.

    Args:
        tool_name (str): The name of the tool to execute.
        params (Dict): Parameters for the tool, including 'project_name'.
        logger: Logger instance.

    Returns:
        Any: Result of the tool execution or error dictionary.
    """
    projects = config.get("all_projects") or get_projects(config)
    logger.info(f"Executing tool: {tool_name}, params: {params}")
    # logger.debug(f"Parameters: {params}")
    # logger.debug(f"Projects: {projects}")
    if projects:
        project = next((p for p in projects if p["name"] == params["project_name"]), None)
        if not project:
            raise ValueError(f"Project not found: {params['project_name'] }, projects: {projects}")
        project_path = os.path.expanduser(project.get("path", os.getcwd()))
    else:
        project = config
        project_path = os.path.expanduser(config.get("path", os.getcwd()))

    if project_path == "none":
        raise ValueError(f"File operations are not supported for project {params['project_name']}")

    all_tools = load_tools()
    logger.debug(f"all_tools: {all_tools}")
    project_tools = project.get("tools", all_tools)
    tool_config = next((t for t in project_tools if t["function"]["name"] == tool_name), None)
    if not tool_config:
        raise ValueError(f"Unknown tool: {tool_name}")

    logger.debug(f'Executing tool "{tool_name}" on project "{params["project_name"]}", "{project_path}"')
    if tool_name == "list_tracked_files":
        result = list_tracked_files(project_path)
    elif tool_name == "list_tracked_directories":
        result = list_tracked_directories(project_path)
    elif tool_name == "write_files":
        write_files(project_path, params["files"])
        result = {"status": "success"}
    elif tool_name == "write_file":
        write_file(project_path, params["path"], params["content"])
        result = {"status": "success"}
    elif tool_name == "get_files":
        result = get_files(project_path, params["paths"])
    elif tool_name == "get_context":
        result = get_context(project_path)
    elif tool_name == "update_context":
        result = update_context(project_path, params["content"])
    elif tool_name == "create_directories":
        create_directories(project_path, params["directories"])
        result = {"status": "success"}
    elif tool_name == "list_modified_files":
        result = list_modified_files(project_path)
    elif tool_name == "get_diffs":
        result = get_diffs(project_path, params.get("paths", []))
    elif tool_name == "delete_files":
        result = delete_files(project_path, params["paths"])
    elif tool_name == "move_files":
        result = move_files(project_path, params["moves"])
    elif tool_name == "search_files":
        result = search_files(
            project_path, params["query"], params.get("is_regex", False), params.get("context_lines", 0)
        )
    elif tool_name == "run_pytest":
        result = run_pytest(project_path, params["test_path"])
    elif tool_name == "get_url":
        result = get_url(params["url"])
    elif tool_name == "get_example":
        result = get_example(project_path, params["example_name"])
    else:
        raise ValueError("Unknown tool: {tool_name}")

    if tool_config.get("returns_response", True):
        logger.debug(f"Tool result: {result}")
        return result

    return None
