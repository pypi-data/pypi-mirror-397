from typing import Literal

from pydantic import BaseModel

class JsonEntry(BaseModel):
    data: list

class Output(BaseModel):
    """Class for result of a Dify node"""
    text: str
    files: list
    json: list[JsonEntry]
class DataSourceTypeAware(BaseModel):
    datasource_type: Literal["local_file", "online_document", "website_crawl"]