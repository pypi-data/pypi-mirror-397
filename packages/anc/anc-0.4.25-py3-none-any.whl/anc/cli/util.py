import sys
import os
from typing import Any, Optional
from urllib.parse import urlparse
from pathlib import Path
import click
import yaml
from typing import Dict, Set, Tuple
import re
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.console import Console
from rich import box


from anc.conf.remote import remote_storage_prefix

console = Console(highlight=False)

_ALLOWED_KEYS = {"task", "tp_size", "num_fewshot", "batch_size", "seq_length", "dp_size", "pp_size", "limit", "max_seq_len", "max_out_len"}
_TASK_NAME_RE = re.compile(r"^[A-Za-z0-9_.:\-\/]+$")

WANDB_API_KEY = os.environ.get("WANDB_API_KEY", "a5c281c2ae6c3e5d473072cf64f8c98e7a68b00d")
TEAM_NAME = os.environ.get("MLP_PROJECT", "llm")

def extract_step_from_path(path: str) -> int:
    try:
        if 'step=' in path:
            tail = path.split('step=')[1]
            digits = []
            for ch in tail:
                if ch.isdigit():
                    digits.append(ch)
                else:
                    break
            return int(''.join(digits)) if digits else 0
    except Exception:
        pass
    return 0

def click_group(*args, **kwargs):
    class ClickAliasedGroup(click.Group):
        def get_command(self, ctx, cmd_name):
            rv = click.Group.get_command(self, ctx, cmd_name)
            if rv is not None:
                return rv

            def is_abbrev(x, y):
                # first char must match
                if x[0] != y[0]:
                    return False
                it = iter(y)
                return all(any(c == ch for c in it) for ch in x)

            matches = [x for x in self.list_commands(ctx) if is_abbrev(cmd_name, x)]

            if not matches:
                return None
            elif len(matches) == 1:
                return click.Group.get_command(self, ctx, matches[0])
            ctx.fail(f"'{cmd_name}' is ambiguous: {', '.join(sorted(matches))}")

        def resolve_command(self, ctx, args):
            # always return the full command name
            _, cmd, args = super().resolve_command(ctx, args)
            return cmd.name, cmd, args

    return click.group(*args, cls=ClickAliasedGroup, **kwargs)

def is_valid_source_path(path: str, personal: str) -> bool:
    """Check if the source path is valid."""
    if not os.path.exists(path):
        print(f"Your source {path} is invalid, path not exists")
        return False
    if not os.access(path, os.R_OK):
        print(f"Your source {path} is invalid, path not access")
        return False
    if not path.startswith(remote_storage_prefix):
        print(f"Your source {path} is invalid, path is not prefix of {remote_storage_prefix} ")
        return False
    if path.startswith("/mnt/personal") and not personal:
        print(f"We can't get your personal information as you want to use {path}, so please reach out infra team to setup.")
        return False
    return True

def convert_to_absolute_path(path: str) -> str:
    """Convert a relative path to an absolute path."""
    return os.path.abspath(path)

def get_file_or_folder_name(path: str) -> str:
    """Get the file name with extension or folder name from the given path."""
    if os.path.isdir(path):
        return os.path.basename(path)  # Return folder name
    elif os.path.isfile(path):
        return os.path.basename(path)  # Return file name with extension
    else:
        raise ValueError(f"Invalid path {path}")


class ConfigManager:
    """Configuration management class that handles priority between environment variables and local config files"""

    def __init__(self):
        # Define environment variable names
        self.ENV_USER = "MLP_USER"
        self.ENV_PROJECT = "MLP_PROJECT"
        self.ENV_CLUSTER = "MLP_CLUSTER"
        self.cluster_config_path = '/mnt/project/.anc_profile'
        self.personal_config_path = '~/.anc_personal'

    def _read_anc_cluster_profile(self):
        """Read cluster configuration file
        Returns:
            dict: Cluster configuration dictionary
        """
        # Check if .anc_profile file exists
        if not os.path.isfile(self.cluster_config_path):
            return {}

        # Read and parse the YAML file
        try:
            with open(self.cluster_config_path, 'r') as file:
                profile_data = yaml.safe_load(file)
            return profile_data if profile_data else {}
        except yaml.YAMLError as e:
            return {}
        except IOError as e:
            return {}

    def _read_anc_personal_profile(self):
        """Read personal configuration file
        Returns:
            dict: Personal configuration dictionary
        """
        # Implement actual file reading logic here
        # e.g. personal: xuguang.zhao
        # Check if .anc_profile file exists
        profile_path = os.path.expanduser(self.personal_config_path)

        if not os.path.isfile(profile_path):
            return {}

        try:
            with open(profile_path, 'r') as file:
                profile_data = yaml.safe_load(file)
            return profile_data or {}
        except yaml.YAMLError as e:
            return {}
        except IOError as e:
            return {}

    def get_environment(self):
        """Get environment configuration information
        Priority: First try to get from environment variables,
        if not found, then read from configuration files

        Returns:
            tuple: (project, cluster, personal) configuration values
        """
        # Get values from environment variables
        cluster_info = self._read_anc_cluster_profile()
        user_info = self._read_anc_personal_profile()

        personal = os.environ.get(self.ENV_USER) or user_info.get('personal', '')
        cluster = os.environ.get(self.ENV_CLUSTER) or cluster_info.get('cluster', '')
        project = os.environ.get(self.ENV_PROJECT) or cluster_info.get('project', '')

        return project, cluster, personal

def validate_path_exists(path: str) -> bool:
    """Validate if the path exists"""
    if not os.path.exists(path):
        print(f"Your path {path} is invalid, path not exists")
        return False
    return True


def get_custom_code_base_from_env() -> str:
    custom_code_base_string = ""
    # Read code base paths from environment variables
    harness_code_base = os.getenv("HARNESS_CODE_BASE", "")
    ocean_code_base = os.getenv("OCEAN_CODE_BASE", "")
    nemo_code_base = os.getenv("NEMO_CODE_BASE", "")
    megatron_code_base = os.getenv("MEGATRON_CODE_BASE", "")
    anc_omni_code_base = os.getenv("ANC_OMNI_CODE_BASE", "")
    
    path_list = [path for path in [harness_code_base, ocean_code_base, nemo_code_base, megatron_code_base, anc_omni_code_base] if path != ""]
    
    for path in path_list:
        if not validate_path_exists(path):
            print(f"Your path {path} is invalid, path not exists")
            sys.exit(1)
   
    custom_code_base_string += f"OCEAN={ocean_code_base}," if ocean_code_base else ""
    custom_code_base_string += f"NEMO={nemo_code_base}," if nemo_code_base else ""
    custom_code_base_string += f"MEGATRON={megatron_code_base}," if megatron_code_base else ""
    custom_code_base_string += f"LM_EVALUATION_HARNESS={harness_code_base}," if harness_code_base else ""
    custom_code_base_string += f"ANC_OMNI={anc_omni_code_base}," if anc_omni_code_base else ""
    if custom_code_base_string.endswith(","):
        custom_code_base_string = custom_code_base_string[:-1]
    return custom_code_base_string


def is_hf_ckpt(ckpt_path: str) -> bool:
    d = Path(ckpt_path)
    has_config = (d / "config.json").is_file()
    has_safetensors = any(d.glob("*.safetensors"))
    return has_config and has_safetensors


def is_megatron_ckpt(ckpt_path: str) -> str:
    d = Path(ckpt_path)
    has_config = (d / "metadata.json").is_file()
    has_safetensors = any(d.glob("*.distcp"))
    return has_config and has_safetensors


def validate_task_and_reason(task: str, allowed_tasks: Optional[Set[str]] = None) -> Tuple[bool, str]:
    if task is None:
        return False, "empty input"

    s = task.strip()
    if not s:
        return False, "empty input"
    
    if "=" not in s:
        parts = [p.strip() for p in s.split("|")]
        if not parts or any(not p for p in parts):
            return False, "empty task in basic mode"
        for t in parts:
            if not _TASK_NAME_RE.match(t):
                return False, f"invalid task name: {t}"
            if allowed_tasks is not None and t not in allowed_tasks:
                return False, f"task not allowed: {t}"
        return True, "basic"
    
    groups = [g.strip() for g in s.split("|")]
    if not groups or any(not g for g in groups):
        return False, "empty group in advanced mode"

    for grp in groups:
        kvs = [p.strip() for p in grp.split(",") if p.strip()]
        if not kvs:
            return False, "empty kv list in group"

        seen = {}
        for kv in kvs:
            if "=" not in kv:
                return False, f"missing '=' in '{kv}'"
            k, v = kv.split("=", 1)
            k, v = k.strip(), v.strip()

            if k not in _ALLOWED_KEYS:
                return False, f"unknown key '{k}'"
            if k in seen:
                return False, f"duplicate key '{k}'"
            if k == "task":
                if not v:
                    return False, "empty task value"
                if not _TASK_NAME_RE.match(v):
                    return False, f"invalid task name: {v}"
                if allowed_tasks is not None and v not in allowed_tasks:
                    return False, f"task not allowed: {v}"
            # else:
            #     if not re.fullmatch(r"\d+", v):
            #         return False, f"value for '{k}' must be a non-negative integer: {v}"

            seen[k] = v

        if "task" not in seen:
            return False, "missing required key 'task' in group"
    
    return True, "advanced"


def generate_eval_ckpt_list(ckpt_paths: str, ckpt_list: str) -> list[str]:
    # Process checkpoint paths
    eval_ckpt_paths_list = []
    if ckpt_paths:
        if not ckpt_paths.startswith("/mnt/project") and not ckpt_paths.startswith("/mnt/share"):
            print("❌ Checkpoint path is invalid, must start with /mnt/project or /mnt/share")
            print(f"   Provided path: {ckpt_paths}")
            sys.exit(1)
        
        if not os.path.exists(ckpt_paths):
            print("❌ Checkpoint path does not exist:")
            print(f"   Path: {ckpt_paths}")
            sys.exit(1)
        
        if not os.path.isdir(ckpt_paths):
            print("❌ Checkpoint path is not a directory:")
            print(f"   Path: {ckpt_paths}")
            print("   Please provide a directory containing checkpoint files.")
            sys.exit(1)
        
        # List all items in the checkpoint directory
        ckpt_items = os.listdir(ckpt_paths)
        if not ckpt_items:
            print("❌ Checkpoint directory is empty:")
            print(f"   Path: {ckpt_paths}")
            sys.exit(1)
        
        for ckpt_path in ckpt_items:
            eval_ckpt_paths_list.append(os.path.join(ckpt_paths, ckpt_path))
    else:  # ckpt_list is provided
        ckpt_list_paths = [path.strip() for path in ckpt_list.split(',')]
        
        # Check each checkpoint path individually
        valid_paths = []
        invalid_paths = []
        
        for i, ckpt_path in enumerate(ckpt_list_paths, 1):
            # Check if path starts with valid prefix
            if not (ckpt_path.startswith("/mnt/project") or ckpt_path.startswith("/mnt/share")):
                print(f"⚠️  WARNING: Checkpoint {i} path is invalid (must start with /mnt/project or /mnt/share):")
                print(f"   Path: {ckpt_path}")
                invalid_paths.append(ckpt_path)
                continue
            
            # Check if path exists
            if not os.path.exists(ckpt_path):
                print(f"⚠️  WARNING: Checkpoint {i} path does not exist:")
                print(f"   Path: {ckpt_path}")
                invalid_paths.append(ckpt_path)
                continue
            
            # Path is valid
            print(f"✅ Checkpoint {i} path validated: {os.path.basename(ckpt_path)}")
            valid_paths.append(ckpt_path)
            eval_ckpt_paths_list.append(ckpt_path)
        
        # Summary
        print(f"\n📊 Checkpoint Path Summary:")
        print(f"   ✅ Valid paths: {len(valid_paths)}")
        print(f"   ❌ Invalid paths: {len(invalid_paths)}")
        
        if invalid_paths:
            print(f"\n❌ Found {len(invalid_paths)} invalid checkpoint path(s). Cannot proceed.")
            for path in invalid_paths:
                print(f"   - {path}")
            print("\nPlease fix the invalid paths and try again.")
            sys.exit(1)
        
        if not valid_paths:
            print("❌ No valid checkpoint paths found. Cannot proceed.")
            sys.exit(1)
    return eval_ckpt_paths_list

def generate_eval_dataset_list(dataset_paths: str, dataset_list: str) -> list[str]:
    eval_dataset_list = []
    if dataset_paths:
        if os.path.isdir(dataset_paths):
            dataset_files = [f for f in os.listdir(dataset_paths) if os.path.isfile(os.path.join(dataset_paths, f)) or os.path.isdir(os.path.join(dataset_paths, f))]

            for i, dataset_file in enumerate(dataset_files, 1):
                full_path = os.path.join(dataset_paths, dataset_file)
                eval_dataset_list.append(full_path)
        else:
            print("Error: Dataset path is not a directory")
            sys.exit(1)
    elif dataset_list:
        for path in dataset_list.split(','):
            if not path.strip().startswith("/mnt/project") and not path.strip().startswith("/mnt/share"):
                print("Error: Dataset path is invalid, must start with /mnt/project or /mnt/share")
                sys.exit(1)
            if not os.path.exists(path.strip()):
                print("Error: Dataset path does not exist")
                sys.exit(1)
            eval_dataset_list.append(path.strip())

    return eval_dataset_list


def generate_tasks_list(dataset_tasks: str) -> list[str]:
    tasks_list = []
    if dataset_tasks:
        valid, reason = validate_task_and_reason(dataset_tasks)
        if not valid:
            print(f"❌ Invalid dataset tasks: {reason}")
            sys.exit(1)
        
        # Split dataset_tasks by "|" and display each task on a separate line
        tasks_list = [task.strip() for task in dataset_tasks.split("|")]
        for task in tasks_list:
            if task.startswith(";"):
                tasks_list.remove(task)
                tasks_list.insert(0, task)

    return tasks_list


def receipt_print_and_confirm(run_id,
                model_name,
                project_name,
                tokenizer_path,
                eval_ckpt_paths_list: list[str],
                eval_dataset_list: list[str],
                eval_tasks_list: list[str],
                validation_batch_size,
                harness_backend,
                queue,
                omni_mode,
                wandb_project,
                wandb_api_key,
                custom_code_base_string,
                tp,
                pp,
                seq_len,
                task_eval_mode,
                training_framework,
                private_eval_batch_size,
                batch_size
            ) -> None:
    # Create a rich Table for configuration details
    if len(eval_ckpt_paths_list) == 0:
        print("Error: No checkpoint paths provided")
        sys.exit(1)

    config_table = Table(box=box.ROUNDED, show_header=False, border_style="blue", expand=True)
    config_table.add_column("Parameter", style="cyan", no_wrap=True, width=30)
    config_table.add_column("Value", style="green", no_wrap=False, overflow="fold")

    config_table.add_row("team", TEAM_NAME)
    config_table.add_row("project Name", project_name)
    config_table.add_row("eval queue", queue)

    # Model Configuration
    config_table.add_section()
    config_table.add_row("model name", model_name)
    config_table.add_row("tokenizer", tokenizer_path)

    # Evaluation Configuration
    config_table.add_section()
    config_table.add_row("ckpt origin framework", training_framework)
    config_table.add_row("ckpt count", f"{len(eval_ckpt_paths_list)} checkpoints")
    for i, ckpt_path in enumerate(eval_ckpt_paths_list, 1):
        config_table.add_row(f"  ckpt {i}", ckpt_path)

    # validation loss dataset
    if len(eval_dataset_list) > 0:
        config_table.add_section()
        config_table.add_row("validation iteration", f"{validation_batch_size}")
        config_table.add_row("private eval batch size", f"{private_eval_batch_size}")
        config_table.add_row("validation datasets", f"{len(eval_dataset_list)} datasets")
        for i, dataset_path in enumerate(eval_dataset_list, 1):
            config_table.add_row(f"  ds {i}", dataset_path)

    if len(eval_tasks_list) > 0:
        config_table.add_section()
        config_table.add_row("task eval mode", task_eval_mode)
        config_table.add_row("batch size", f"{batch_size}")
        if "harness" in task_eval_mode:
            config_table.add_row("harness backend", harness_backend)

        if "omni" in task_eval_mode:
            config_table.add_row("omni mode", omni_mode)

        config_table.add_row("tasks count", f"{len(eval_tasks_list)} tasks")
        for i, task in enumerate(eval_tasks_list, 1):
            config_table.add_row(f"  task {i}", task)
    
    config_table.add_section()
    config_table.add_row("global tp:", str(tp))
    config_table.add_row("global pp:", str(pp))
    config_table.add_row("global seq len:", str(seq_len))

    #  Code Base Configuration
    if custom_code_base_string:
        config_table.add_section()
        val = ""
        for code_base in custom_code_base_string.split(","):
            val += f"{code_base}\n"
        config_table.add_row("code from local", val)

    # Wandb Configuration
    config_table.add_section()
    config_table.add_row("wandb project", wandb_project)
    config_table.add_row("wandb api Key", wandb_api_key)

    # Create title with run ID
    title = Text(f"✨ EVALUATION RECEIPT [ID: {run_id}] ✨", style="bold magenta")
    
    # Print the title and table directly without panel wrapper
    console.print("\n")
    console.print(title, justify="center")
    console.print("\n")
    console.print(config_table)
    console.print("\n")
    # TODO: Implement need the user confirm the evaluation receipt
    user_confirm = input("Do you want to start the evaluation? (y/n): ")
    if user_confirm.lower() != 'y':
        print("Evaluation cancelled.")
        sys.exit(0)
