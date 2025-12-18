from enum import Enum

from pydantic import BaseModel

from davidkhala.ai.agent.dify.plugins.firecrawl import DataSourceInfo


class IndexingStatus(str, Enum):
    WAITING = "waiting"
    PARSING = "parsing"
    SPLITTING = 'splitting'
    INDEXING = "indexing"
    COMPLETED = "completed"
    FAILED = "error"


class Document(BaseModel):
    id: str
    position: int
    data_source_type: str
    data_source_info: dict[str, str]
    name: str
    indexing_status: IndexingStatus
    error: str | None
    enabled: bool


class Dataset(BaseModel):
    id: str
    name: str
    description: str


class IndexingError(Exception):
    """Raised when document indexing fails (indexing_status = 'error')"""
    pass
