from setuptools import setup, find_packages

setup(
    name="wbuuidpkg",
    version="0.1.1",
    packages=find_packages(),
    include_package_data=True,
    package_data={"wbuuidpkg": ["wb_node.js", "lib/crypto-js.min.js"]},
    install_requires=[],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "generate-uuid=wbuuidpkg.generator:generate_encrypted_uuid",
        ]
    },
    description="Generate encrypted uuid using Node.js script",
    author="yige",
    url="",  # 可选
)
