# wbuuidpkg

Python package to generate encrypted UUID using Node.js.

## Installation

1. Install Node.js.
2. Install Python package:

```bash
pip install wbuuidpkg


Usage
from myuuidpkg import generate_encrypted_uuid

data = generate_encrypted_uuid()
print(data["uuid"])
print(data["encodedUuid"])

打包命令
python setup.py sdist bdist_wheel