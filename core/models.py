from pydantic import BaseModel
from typing import List, Optional
from pydantic import Field


class AgentResponse(BaseModel):
    status: str
    warnings: List[str] = Field(default_factory=list)


class ResolvedMapping(BaseModel):
    source_table: str
    source: str
    target_table: str
    target: str
    cast: Optional[str] = None
    transform: Optional[str] = None


class SchemaAnalysisData(BaseModel):
    resolved_mappings: List[ResolvedMapping]


class SchemaAnalystResponse(AgentResponse):
    data: SchemaAnalysisData


class SQLStatement(BaseModel):
    target_table: str
    sql: str


class SQLGeneratorData(BaseModel):
    sql_statements: List[SQLStatement]


class SQLGeneratorResponse(AgentResponse):
    data: SQLGeneratorData

class ValidationIssue(BaseModel):
    severity: str 
    message: str
    suggestion: Optional[str] = None


class ValidationData(BaseModel):
    issues: List[ValidationIssue] = Field(default_factory=list)
    markdown: str


class ValidationResponse(AgentResponse):
    data: ValidationData


class ExplanationData(BaseModel):
    explanation: str


class ExplainerResponse(AgentResponse):
    data: ExplanationData


