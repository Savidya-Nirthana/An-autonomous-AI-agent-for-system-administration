import sys
import os
import json
from langchain_core.messages import ToolMessage
sys.path.append(os.getcwd())

from core.tool_parser import extract_tool_ui

def test_extract_tool_ui():
    # Case 1: Integer output (simulating firewall_status)
    msgs_int = [ToolMessage(content="0", tool_call_id="1")]
    result_int = extract_tool_ui(msgs_int)
    print(f"Input: '0', Result: {result_int}")
    if result_int != []:
        print("FAIL: Expected empty list for integer input")
        return False

    # Case 2: Dict output (simulating UI tool)
    valid_json = '{"ui_type": "test"}'
    msgs_dict = [ToolMessage(content=valid_json, tool_call_id="2")]
    result_dict = extract_tool_ui(msgs_dict)
    print(f"Input: '{valid_json}', Result: {result_dict}")
    if result_dict != [{"ui_type": "test"}]:
        print("FAIL: Expected list with dict for dict input")
        return False

    # Case 3: Mixed
    msgs_mixed = [
        ToolMessage(content="0", tool_call_id="1"),
        ToolMessage(content='{"ui_type": "test"}', tool_call_id="2")
    ]
    result_mixed = extract_tool_ui(msgs_mixed)
    print(f"Input: Mixed, Result: {result_mixed}")
    # Note: reverse order in extract_tool_ui
    expected = [{"ui_type": "test"}] 
    if result_mixed != expected:
        print(f"FAIL: Expected {expected}, got {result_mixed}")
        return False

    print("SUCCESS: All tests passed")
    return True

if __name__ == "__main__":
    if not test_extract_tool_ui():
        sys.exit(1)
