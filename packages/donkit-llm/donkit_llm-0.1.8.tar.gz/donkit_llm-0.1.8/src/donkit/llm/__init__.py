from .model_abstract import (
    ContentPart,
    ContentType,
    EmbeddingRequest,
    EmbeddingResponse,
    FunctionCall,
    FunctionDefinition,
    GenerateRequest,
    GenerateResponse,
    LLMModelAbstract,
    Message,
    ModelCapability,
    StreamChunk,
    Tool,
    ToolCall,
)
from .openai_model import (
    AzureOpenAIEmbeddingModel,
    AzureOpenAIModel,
    OpenAIEmbeddingModel,
    OpenAIModel,
)
from .claude_model import ClaudeModel, ClaudeVertexModel
from .vertex_model import VertexAIModel, VertexEmbeddingModel
from .factory import ModelFactory
from .gemini_model import GeminiModel, GeminiEmbeddingModel
from .donkit_model import DonkitModel

import importlib.util

if importlib.util.find_spec("donkit.llm_gate.client") is not None:
    from .llm_gate_model import LLMGateModel
else:
    LLMGateModel = None

__all__ = [
    "ModelFactory",
    # Abstract base
    "LLMModelAbstract",
    "ModelCapability",
    # Request/Response models
    "Message",
    "ContentPart",
    "ContentType",
    "GenerateRequest",
    "GenerateResponse",
    "StreamChunk",
    "EmbeddingRequest",
    "EmbeddingResponse",
    # Tool/Function calling
    "Tool",
    "ToolCall",
    "FunctionCall",
    "FunctionDefinition",
    # Implementations
    "OpenAIModel",
    "AzureOpenAIModel",
    "OpenAIEmbeddingModel",
    "AzureOpenAIEmbeddingModel",
    "ClaudeModel",
    "ClaudeVertexModel",
    "VertexAIModel",
    "VertexEmbeddingModel",
    "GeminiModel",
    "GeminiEmbeddingModel",
    "DonkitModel",
]

if LLMGateModel is not None:
    __all__.append("LLMGateModel")
