#𝖇𝖞 𝖊𝖑𝖎7𝖊𝖎𝖓 - 𝕰7

import time
from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class QueryRecord:
    sql: str
    params: List[Any]
    duration: float
    timestamp: datetime


class QueryProfiler:
    def __init__(self):
        self.queries: List[QueryRecord] = []
        self.enabled = False

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False

    def record_query(self, sql: str, params: List[Any], duration: float):
        if self.enabled:
            record = QueryRecord(
                sql=sql,
                params=params,
                duration=duration,
                timestamp=datetime.now()
            )
            self.queries.append(record)

    def get_statistics(self) -> Dict[str, Any]:
        if not self.queries:
            return {}

        total_queries = len(self.queries)
        total_duration = sum(q.duration for q in self.queries)
        avg_duration = total_duration / total_queries
        slowest = max(self.queries, key=lambda q: q.duration)

        return {
            "total_queries": total_queries,
            "total_duration": total_duration,
            "avg_duration": avg_duration,
            "slowest_query": {
                "sql": slowest.sql,
                "duration": slowest.duration,
                "timestamp": slowest.timestamp
            }
        }

    def clear(self):
        self.queries.clear()