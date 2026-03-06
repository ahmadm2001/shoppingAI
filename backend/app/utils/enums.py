from enum import Enum


class OrderStatus(str, Enum):
    TEMP = "TEMP"
    CLOSE = "CLOSE"


class SearchOperator(str, Enum):
    LESS_THAN = "<"
    GREATER_THAN = ">"
    EQUAL = "="
