from setuptools import setup

setup(
    name="poly-edgefinder",
    version="0.1.0",
    install_requires=[
        "requests>=2.31.0",
        "websocket-client>=1.6.0",
        "py-clob-client>=0.3.0",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "python-dotenv>=1.0.0",
        "schedule>=1.2.0",
        "sqlalchemy>=2.0.0",
        "fastapi>=0.110.0",
        "uvicorn[standard]>=0.29.0",
        "aiohttp>=3.9.0",
    ],
    python_requires=">=3.9",
)