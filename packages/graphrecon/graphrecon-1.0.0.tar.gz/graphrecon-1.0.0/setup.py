from setuptools import setup

setup(
    name="graphrecon",
    version="1.0.0",
    py_modules=["graphrecon"],
    install_requires=["aiohttp"],
    entry_points={
        "console_scripts": [
            "graphrecon=graphrecon:main",
        ]
    },
)