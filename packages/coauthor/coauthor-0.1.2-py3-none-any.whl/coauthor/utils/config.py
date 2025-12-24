import yaml
import os
import importlib.resources
import copy


def deep_merge(d1, d2):
    for key, value in d2.items():
        if key in d1 and isinstance(d1[key], dict) and isinstance(value, dict):
            deep_merge(d1[key], value)
        else:
            d1[key] = value
    return d1


def read_config(file_path, logger=None):
    if logger:
        logger.info(f"Reading configuration from {file_path}")
    with open(file_path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def get_config_path(config_filename=".coauthor.yml", search_dir=os.getcwd()):
    traversed_paths = []
    while True:
        potential_path = os.path.join(search_dir, config_filename)
        if os.path.exists(potential_path):
            return potential_path, traversed_paths
        traversed_paths.append(search_dir)
        parent_dir = os.path.dirname(search_dir)
        if parent_dir == search_dir:
            break
        search_dir = parent_dir

    home_dir = os.path.expanduser("~")
    home_path = os.path.join(home_dir, config_filename)
    if os.path.exists(home_path):
        traversed_paths.append(home_dir)
        return home_path, traversed_paths

    return None, traversed_paths


def get_default_config():
    config = {
        "jinja": {"search_path": ".coauthor/templates"},
        "agent": {
            "api_key_var": "OPENAI_API_KEY",
            "api_url_var": "OPENAI_API_URL",
            "model": "openai/gpt-5.2-pro",
        },
        "file-watcher": {"ignore-folders": ["__pycache__", ".obsidian", ".git"]},
    }
    return config


def get_projects(config):
    projects = config.get("projects", [])
    config_name = config.get("name")
    if config_name and not any(p.get("name") == config_name for p in projects):
        projects += [config]
    return projects


def expand_paths(conf):
    if "path" in conf:
        conf["path"] = os.path.expanduser(conf["path"])
    if "projects" in conf:
        for proj in conf["projects"]:
            expand_paths(proj)


def save_config_dump(config, logger=None):
    dump_path = os.path.join(os.getcwd(), ".coauthor_dump.yml")
    with open(dump_path, "w", encoding="utf-8") as dump_file:
        yaml.safe_dump(config, dump_file, default_flow_style=False)
        if logger:
            logger.info(f"Dumped configuration to {dump_path}")


def _apply_profile_args_to_single_workflow(profile_config, profile_args):
    """Apply project-level profile_args into the single workflow when a profile defines exactly one workflow.

    Profiles often define a single workflow (e.g. the Jira profile). In that case we flatten the workflow
    into top-level keys, but the runtime still iterates over profile_config['workflows'][0].

    Without this, overrides like profile_args.watch.jira.query would only affect the flattened keys and
    not the workflow itself.
    """

    workflows = profile_config.get("workflows") or []
    if len(workflows) != 1:
        return

    workflow = workflows[0]

    # Only merge known workflow-level keys (avoid polluting workflow dict with unrelated project keys).
    workflow_level_keys = {
        "watch",
        "scan",
        "tasks",
        "content_patterns",
        "path_patterns",
        "path",
        "name",
        "description",
        "agent",
    }
    filtered_profile_args = {k: v for k, v in profile_args.items() if k in workflow_level_keys}
    if filtered_profile_args:
        deep_merge(workflow, filtered_profile_args)



def get_config(path=None, logger=None, config_filename=".coauthor.yml", search_dir=os.getcwd(), args=None):
    config = {}
    config_path = None
    if args and hasattr(args, "config_path") and args.config_path:
        config_path = args.config_path
    elif args and hasattr(args, "profile") and args.profile:
        profile = args.profile
        profile_path = importlib.resources.files("coauthor.profiles").joinpath(profile).joinpath("config.yml")
        config = get_default_config()
        deep_merge(config, read_config(profile_path, logger))
        expand_paths(config)
        return config
    if not config_path:
        if path:
            config_path = path
        else:
            config_path, searched_paths = get_config_path(config_filename, search_dir)
            if not config_path:
                if logger:
                    logger.warning(f"Configuration file not found. Searched directories: {', '.join(searched_paths)}")
                config_path = os.path.join(os.getcwd(), config_filename)
                config = get_default_config()
                with open(config_path, "w", encoding="utf-8") as file:
                    if logger:
                        logger.debug(f"Dump config to YAML file {config_path}")
                    yaml.safe_dump(config, file)

                if logger:
                    logger.info(f"Created default configuration file at {config_path}")
    config = get_default_config()
    deep_merge(config, read_config(config_path, logger))
    expand_paths(config)
    if "projects" in config:
        for proj in config["projects"]:
            if "profile" in proj:
                logger.info(f"Applying profile {proj['profile']} config to project {proj['name']}")
                profile = proj["profile"]
                profile_path = importlib.resources.files("coauthor.profiles").joinpath(profile).joinpath("config.yml")
                profile_config = read_config(profile_path, logger)
                # Flatten if single workflow
                workflows = profile_config.get("workflows", [])
                if len(workflows) == 1:
                    workflow = workflows[0]
                    deep_merge(profile_config, workflow)
                # Apply profile_args if present
                if "profile_args" in proj:
                    profile_args = proj["profile_args"]
                    deep_merge(profile_config, profile_args)
                    _apply_profile_args_to_single_workflow(profile_config, profile_args)
                    del proj["profile_args"]
                local = copy.deepcopy(proj)
                proj.clear()
                default = get_default_config()
                deep_merge(proj, default)
                deep_merge(proj, profile_config)
                deep_merge(proj, local)
        expand_paths(config)
        all_projects = get_projects(config)
        for proj in config["projects"]:
            proj["all_projects"] = all_projects
    return config


def get_jinja_config(config):
    if "jinja" in config:
        return config["jinja"]
    config_jinja = {"search_path": ".coauthor/templates"}
    return config_jinja
