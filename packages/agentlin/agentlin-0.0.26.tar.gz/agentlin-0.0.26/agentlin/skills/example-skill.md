---
name: Example Skill
description: An example skill demonstrating how to create a custom skill in AgentLin.
---
# Example Skill
This is an example skill that showcases how to create a custom skill in AgentLin. It includes a simple tool that can be used by the agent to perform a specific task.

<executed-code>
{{code_for_agent}}
</executed-code>

## Code for Agent
```python
def example_tool(input_text: str) -> str:
    """A simple example tool that reverses the input text."""
    return input_text[::-1]
```

## Code for Interpreter
```python
def interpret_example_tool(input_text: str) -> str:
    """Interprets the output of the example tool."""
    return f"Interpreted Output: {input_text}"
```
