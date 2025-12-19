from agentlin.code_interpreter.types import (
    MIME_TOOL_CALL,
    MIME_TOOL_RESPONSE,
)

# Try to import IPython components and check if we're in an IPython environment
try:
    from IPython.display import display as ipython_display
    from IPython.core.display import DisplayObject
    from IPython import get_ipython

    # Check if we're actually running in an IPython environment
    if get_ipython() is not None:
        display = ipython_display
        IPYTHON_AVAILABLE = True
    else:
        # IPython is installed but we're not in an IPython environment
        raise ImportError("Not in IPython environment")

except (ImportError, AttributeError):
    # Create dummy classes for non-IPython environments
    class DisplayObject:
        def __init__(self, data=None, metadata=None, **kwargs):
            self.data = data or {}
            self.metadata = metadata or {}

        def _repr_mimebundle_(self, include=None, exclude=None):
            return self.data

    class MimeBundle(DisplayObject):
        """A display object that wraps a MIME bundle dictionary"""

        def __init__(self, data_dict):
            if isinstance(data_dict, dict):
                super().__init__(data=data_dict)
            else:
                super().__init__(data={"text/plain": str(data_dict)})

    def display(obj):
        """Fallback display function for non-IPython environments"""
        # Handle our custom display objects first
        if hasattr(obj, "_repr_mimebundle_"):
            bundle = obj._repr_mimebundle_()
        elif isinstance(obj, dict):
            # Handle MIME bundle dictionary directly
            bundle = obj
        else:
            bundle = {"text/plain": str(obj)}

        # Display the content based on available MIME types
        if MIME_TOOL_CALL in bundle:
            tool_call_data = bundle[MIME_TOOL_CALL]
            print(f"🔧 Tool Call: {tool_call_data.get('tool_name', 'Unknown')} (ID: {tool_call_data.get('call_id', 'N/A')})")
            if tool_call_data.get("tool_args"):
                print(f"   Arguments: {tool_call_data['tool_args']}")
        elif MIME_TOOL_RESPONSE in bundle:
            tool_response_data = bundle[MIME_TOOL_RESPONSE]
            blocks = tool_response_data.get("block_list", [])
            content = tool_response_data.get("message_content", [])
            print(f"📤 Tool Response: {len(blocks)} blocks, {len(content)} content items")
            if blocks:
                for i, block in enumerate(blocks[:3]):  # Show first 3 blocks
                    block_type = block.get("type", "unknown")
                    print(f"   Block {i+1}: {block_type}")
                if len(blocks) > 3:
                    print(f"   ... and {len(blocks) - 3} more blocks")
        elif "text/html" in bundle:
            print(f"HTML: {bundle['text/html']}")
        elif "text/markdown" in bundle:
            print(f"Markdown: {bundle['text/markdown']}")
        elif "application/json" in bundle:
            import json

            print(f"JSON: {json.dumps(bundle['application/json'], indent=2)}")
        elif "text/plain" in bundle:
            print(bundle["text/plain"])
        else:
            # Fallback to string representation
            print(str(bundle))

    IPYTHON_AVAILABLE = False


class MimeDisplayObject:
    """Display wrapper for ToolCall objects"""

    def __init__(self, mime_type: str, data: dict):
        self.mime_type = mime_type
        self.data = data

    def __str__(self):
        display(self)
        return ""

    def _repr_mimebundle_(self, include=None, exclude=None):
        return {
            self.mime_type: self.data,
        }


class RawDisplayObject:
    """Display wrapper for ToolCall objects"""

    def __init__(self, data: dict):
        self.data = data

    def __str__(self):
        display(self)
        return ""

    def _repr_mimebundle_(self, include=None, exclude=None):
        return self.data


def safe_b64decode(b64_string: str):
    """安全解码 base64，返回 bytes"""
    import base64
    if b64_string.startswith("data:image"):
        b64_string = b64_string.split(",", 1)[1]
    b64_string = b64_string.strip().replace("\n", "").replace(" ", "")
    missing_padding = len(b64_string) % 4
    if missing_padding:
        b64_string += "=" * (4 - missing_padding)
    return base64.b64decode(b64_string)


class MIME_IMAGE(MimeDisplayObject):
    def __init__(self, base64_str: str, format: str = "png"):
        super().__init__(mime_type="image/" + format, data=safe_b64decode(base64_str))
        self.base64_str = base64_str
        self.format = format

