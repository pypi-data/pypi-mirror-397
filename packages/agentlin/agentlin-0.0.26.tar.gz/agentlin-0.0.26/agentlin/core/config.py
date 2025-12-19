import os
import re
import yaml
from typing import Any, Optional, Union

from pathlib import Path
from xlin import load_text


def _extract_developer_prompt(markdown_content: str) -> str:
    """Extract the main content before any code sections."""
    # Split by code section headers
    code_section_pattern = r"\n## Code for (Agent|Interpreter)"
    parts = re.split(code_section_pattern, markdown_content)

    if parts:
        # Return the first part (before any code sections)
        return parts[0].strip()

    return markdown_content.strip()


def _extract_code_section(markdown_content: str, section_name: str) -> Optional[str]:
    """Extract code from a specific section."""
    # Pattern to match: ## Section Name followed by code block
    pattern = rf"## {re.escape(section_name)}\s*\n```(?:python)?\s*\n(.*?)\n```"
    match = re.search(pattern, markdown_content, re.DOTALL | re.IGNORECASE)

    if match:
        return match.group(1).strip()

    return None


def parse_config_from_markdown(base_dir: Path, text: str) -> tuple[dict, str, Optional[str], Optional[str]]:
    """
    Load a agent configuration from a markdown file.

    Expected format:
    ---
    name: agent-name
    description: Agent description
    model: model-name (optional)
    allowed_tools: ["tool1", "tool2"] (optional, defaults to ["*"])
    ---

    Agent prompt content here...

    ## Code for Agent (optional)
    ```python
    # Code specific for agent
    ```

    ## Code for Interpreter (optional)
    ```python
    # Code specific for interpreter
    ```
    """
    # Parse YAML front matter
    front_matter_pattern = r"^---\s*\n(.*?)\n---\s*\n(.*)$"
    match = re.match(front_matter_pattern, text, re.DOTALL)

    if not match:
        raise ValueError("No valid front matter found")

    yaml_content, markdown_content = match.groups()

    try:
        config = yaml.safe_load(yaml_content)
    except yaml.YAMLError as e:
        raise ValueError(f"Error parsing YAML: {e}")

    # Extract developer prompt (everything before code sections)
    developer_prompt = _extract_developer_prompt(markdown_content)

    # Extract code sections
    code_for_agent = _extract_code_section(markdown_content, "Code for Agent")
    if not code_for_agent:
        code_for_agent = config["code_for_agent"] if "code_for_agent" in config else None
    if not code_for_agent:
        file_code_for_agent = config["file_code_for_agent"] if "file_code_for_agent" in config else None
        if file_code_for_agent:
            if Path(file_code_for_agent).exists():
                code_for_agent = load_text(file_code_for_agent)
            elif Path(base_dir / file_code_for_agent).exists():
                code_for_agent = load_text(base_dir / file_code_for_agent)

    code_for_interpreter = _extract_code_section(markdown_content, "Code for Interpreter")
    if not code_for_interpreter:
        code_for_interpreter = config["code_for_interpreter"] if "code_for_interpreter" in config else None
    if not code_for_interpreter:
        file_code_for_interpreter = config["file_code_for_interpreter"] if "file_code_for_interpreter" in config else None
        if file_code_for_interpreter:
            if Path(file_code_for_interpreter).exists():
                code_for_interpreter = load_text(file_code_for_interpreter)
            elif Path(base_dir / file_code_for_interpreter).exists():
                code_for_interpreter = load_text(base_dir / file_code_for_interpreter)

    return config, developer_prompt, code_for_agent, code_for_interpreter


def apply_env_to_text(env: dict, text: str) -> str:
    """Substitute variables in the text using simple {{var}} substitution."""
    # Merge env for template substitution
    merged_env: dict[str, Union[str, dict[str, Any]]] = {}
    if env:
        merged_env.update(env)

    # Perform simple {{VAR}} replacement in text
    if merged_env:
        for key, value in merged_env.items():
            value = os.getenv(key, value)  # allow process env override
            text = text.replace("{{" + str(key) + "}}", str(value))
    return text


def apply_env(env: dict, prompt: str, code_for_agent: Optional[str]=None, code_for_interpreter: Optional[str]=None) -> tuple[str, Optional[str], Optional[str]]:
    """Substitute variables in the code using simple {{var}} substitution."""
    # Merge env for template substitution
    merged_env: dict[str, Union[str, dict[str, Any]]] = {}
    if env:
        merged_env.update(env)

    # Perform simple {{VAR}} replacement in prompt
    if merged_env:
        for key, value in merged_env.items():
            value = os.getenv(key, value)  # allow process env override
            prompt = prompt.replace("{{" + str(key) + "}}", str(value))
            if code_for_interpreter:
                code_for_interpreter = code_for_interpreter.replace("{{" + str(key) + "}}", str(value))
            if code_for_agent:
                code_for_agent = code_for_agent.replace("{{" + str(key) + "}}", str(value))
    if code_for_agent is not None:
        prompt = prompt.replace("{{code_for_agent}}", code_for_agent)
    return prompt, code_for_agent, code_for_interpreter
