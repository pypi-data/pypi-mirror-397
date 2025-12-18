from setuptools import find_packages, setup  # pyright: ignore[reportMissingModuleSource]

setup(
    name="rayel-rpa-executor",
    version="0.5.44",  # 由 publish.sh 自动递增
    packages=find_packages(),
    install_requires=[
        "pydantic>=2.7.4",
        "python-dotenv>=1.0.1",
        "aiohttp>=3.10.9",
        "protobuf>=5.27.2",
        "grpcio>=1.66.2",
        "GitPython>=3.1.0",
        "playwright>=1.55.0",
        "fastapi>=0.122.0",           # 新增：FastAPI框架
        "uvicorn[standard]>=0.38.0",  # 新增：ASGI服务器
        "apscheduler>=3.11.1",        # 新增：定时任务调度
    ],
    extras_require={
        "dev": [
            "ruff>=0.3.0",
            "grpcio-tools>=1.66.2",
        ],
    },
    python_requires=">=3.12",
    description="Distributed task scheduler and RPA executor with FastAPI and browser pool management",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
)
