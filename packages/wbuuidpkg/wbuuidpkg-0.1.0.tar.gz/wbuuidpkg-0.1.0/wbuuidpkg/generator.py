import subprocess
import json
import os

def generate_encrypted_uuid():
    """调用 Node.js 脚本生成 uuid 和 encodedUuid"""
    js_file = os.path.join(os.path.dirname(__file__), "wb_node.js")
    res = subprocess.check_output(["node", js_file])
    return json.loads(res)
