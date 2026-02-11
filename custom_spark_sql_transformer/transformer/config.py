from __future__ import annotations
from typing import Dict, List, Optional, Literal
from pydantic import BaseModel, Field

InputFormat = Literal["csv", "parquet"]

class InputSpec(BaseModel):
    name: str = Field(..., description="Temp view name to register, e.g. customers_raw")
    path: str = Field(..., description="Input path")
    format: InputFormat = Field("csv")
    options: Dict[str, str] = Field(default_factory=dict)

class SqlStep(BaseModel):
    name: str
    sql_file: str
    create_view: Optional[str] = None

class NotNullRule(BaseModel):
    type: Literal["not_null"] = "not_null"
    view: str
    columns: List[str]

class UniqueRule(BaseModel):
    type: Literal["unique"] = "unique"
    view: str
    columns: List[str]

class RowCountRule(BaseModel):
    type: Literal["row_count"] = "row_count"
    view: str
    min: Optional[int] = None
    max: Optional[int] = None

DQRule = NotNullRule | UniqueRule | RowCountRule

class OutputSpec(BaseModel):
    view: str
    path: str
    format: Literal["parquet"] = "parquet"
    mode: Literal["overwrite", "append"] = "overwrite"
    partition_by: List[str] = Field(default_factory=list)

class JobSpec(BaseModel):
    job_name: str
    inputs: List[InputSpec]
    sql_steps: List[SqlStep]
    output: OutputSpec
    dq_rules: List[DQRule] = Field(default_factory=list)
    add_audit_columns: bool = True
