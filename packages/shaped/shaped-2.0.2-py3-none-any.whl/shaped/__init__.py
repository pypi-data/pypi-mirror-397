"""
Shaped V2 SDK for Python.

Provides client SDK for interacting with Shaped AI V2 API.
"""
from shaped.client import Client
from shaped.query_builder import (
    RankQueryBuilder,
    ColumnOrder,
    TextSearch,
    Similarity,
    CandidateIds,
    CandidateAttributes,
    Filter,
    Expression,
    Truncate,
    Prebuilt,
    ensemble as Ensemble,
    Boosted,
    Exploration,
    Diversity,
)
from shaped.config_builders import (
    Engine,
    Table,
    View,
)

# Type alias for ViewConfig
# Type alias for ViewConfig
from shaped.client import ViewConfig

__all__ = [
    'Client',
    'RankQueryBuilder',
    'Similarity',
    'TextSearch',
    'CandidateIds',
    'CandidateAttributes',
    'ColumnOrder',
    'Filter',
    'Expression',
    'Truncate',
    'Prebuilt',
    'Ensemble',
    'Passthrough',
    'Diversity',
    'Boosted',
    'Exploration',
    'ViewConfig',
    'Engine',
    'Table',
    'View',
]
