"""
Custom JSON encoders for handling Neo4j data types
"""
from datetime import date, datetime
from neo4j.time import Date as Neo4jDate, DateTime as Neo4jDateTime, Time as Neo4jTime
from typing import Any, Dict

def serialize_neo4j_types(data: Any) -> Any:
    """
    Recursively convert Neo4j types to standard Python types
    """
    if isinstance(data, Neo4jDate):
        return date(data.year, data.month, data.day).isoformat()
    elif isinstance(data, Neo4jDateTime):
        return datetime(data.year, data.month, data.day, 
                       data.hour, data.minute, data.second, 
                       data.nanosecond // 1000000).isoformat()
    elif isinstance(data, Neo4jTime):
        return f"{data.hour:02d}:{data.minute:02d}:{data.second:02d}"
    elif isinstance(data, dict):
        return {k: serialize_neo4j_types(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [serialize_neo4j_types(item) for item in data]
    return data
