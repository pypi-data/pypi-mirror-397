"""
Evoke Schema - Entity information structures (Model, Tool, DataSource)
"""
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Any


@dataclass
class ModelInfo:
    """Model information"""
    name: str
    provider: str
    tokens_in: Optional[int] = None
    tokens_out: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class ToolInfo:
    """Tool/function information"""
    name: str
    category: Optional[str] = None
    is_external: Optional[bool] = None

    def to_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class DataSourceInfo:
    """Data source information"""
    name: str
    operation: str
    data_type: Optional[str] = None
    trust_level: Optional[str] = None
    sensitive_data: Optional[List[str]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in asdict(self).items() if v is not None}
