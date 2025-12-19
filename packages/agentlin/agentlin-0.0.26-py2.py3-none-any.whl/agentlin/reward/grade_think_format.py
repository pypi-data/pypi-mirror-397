import re

from agentlin.reward.grade_boxed_answer import extract_boxed_answer


def validate_think_answer_format(text: str) -> bool:
    """Performs comprehensive validation of the think answer format.

    Args:
        text: Processed response string from the model

    Returns:
        Boolean indicating whether all formatting requirements are met
    """
    if not text:
        return False
    pattern = re.compile(
        r'^\s*<think>((?:(?!<(?:(?:/?think)|(?:/?answer))>).)*?)'
        r'</think>'
        r'((?:(?!<(?:(?:/?think)|(?:/?answer))>).)*?)'
        r'<answer>((?:(?!<(?:(?:/?think)|(?:/?answer))>).)*?)'
        r'</answer>\s*$',
        re.DOTALL  # 如果需要让 . 匹配换行
    )
    # tests = [
    #     "<think>foo</think>bar<answer>baz</answer>", # ✓
    #     "  <think>思考</think>中间内容<answer>回答</answer>  ", # ✓
    #     "  <think>思考</think><answer>回答</answer>  ", # ✓
    #     "  <think>思考</think>\n<answer>回答</answer>  ", # ✓
    #     "  <think>思考</think> <answer>回答</answer>  ", # ✓
    #     "  <think>思考\n</think> \n<answer>回答\n</answer>  ", # ✓
    #     "<think>a<answer>oops</answer></think>x<answer>y</answer>",  # ✗
    # ]

    # for t in tests:
    #     m = pattern.match(t)
    #     print(t)
    #     print("✓" if m else "✗")
    return True if pattern.match(text) else False


def validate_think_format(text: str) -> bool:
    return all(
        [
            isinstance(text, str),
            text.strip().startswith("<think>"),
            text.count("<think>") == 1,
            text.count("</think>") == 1,
            len(text.split("</think>")[-1]) > 0,
        ]
    )

def validate_boxed_answer_format(text: str) -> bool:
    """Validates if the text contains a boxed answer in the format [[answer]].

    Args:
        text: Processed response string from the model

    Returns:
        Boolean indicating whether the boxed answer format is valid
    """
    if not text:
        return False
    answer = extract_boxed_answer(text)
    if isinstance(answer, str):
        return True
    return False
