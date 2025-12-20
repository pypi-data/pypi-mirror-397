# Suppress Pydantic V1 warning from langchain_core (Python 3.14+ compatibility)
import warnings
warnings.filterwarnings(
    "ignore",
    message=r"Core Pydantic V1 functionality isn't compatible with Python 3\.14",
    category=UserWarning,
)

# Package initialization
import os

# Force LangSmith project name to be "fwauto" at package import time
# This ensures it's set before any LangChain/LangSmith components are initialized
os.environ["LANGCHAIN_PROJECT"] = "fwauto"

# Note: Logging is now initialized lazily in CLI/nodes when first needed,
# using the actual project directory (with .fwauto/) instead of fwauto dev directory
