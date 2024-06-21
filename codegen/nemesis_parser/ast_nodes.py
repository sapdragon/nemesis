from dataclasses import dataclass, field
from typing import List, Optional, Any

@dataclass
class ASTNode:
    pass

@dataclass
class Program(ASTNode):
    declarations: List[ASTNode] = field(default_factory=list)

@dataclass
class Packet(ASTNode):
    name: str
    fields: List['Field'] = field(default_factory=list)
    generic_params: List[str] = field(default_factory=list)
    parent: Optional[str] = None

@dataclass
class Field(ASTNode):
    name: str
    data_type: 'DataType'
    generic_args: List['DataType'] = field(default_factory=list)
    default_value: Optional[Any] = None
    bit_size: Optional[int] = None

@dataclass
class DataType(ASTNode):
    name: str
    is_array: bool = False
    array_size: Optional[int] = None

@dataclass
class Enum(ASTNode):
    name: str
    type: str
    values: List[str]

@dataclass
class TypeAlias(ASTNode):
    name: str
    aliased_type: DataType

@dataclass
class Import(ASTNode):
    path: str
    imported_declarations: List[ASTNode] = field(default_factory=list)