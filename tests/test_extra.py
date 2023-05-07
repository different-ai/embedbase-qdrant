"""
Unit tests special to Qdrant because of its specific API
"""

import hashlib
from qdrant_client.http.models import (
    Filter,
    FieldCondition,
    MatchValue,
)
import numpy as np
import pandas as pd
import pytest
import uuid
from embedbase_qdrant import Qdrant

vector_database = Qdrant(host="localhost", port=6333)


@pytest.mark.asyncio
async def test_multi_collections_scroll():
    """
    Test if ye can properly scroll through multiple collections
    """
    data = [
        # random numpy array of length 1536
        np.random.rand(1536).tolist(),
        np.random.rand(1536).tolist(),
    ]
    df = pd.DataFrame(
        [
            {
                "data": "Bob is a human",
                "embedding": embedding,
                "id": str(uuid.uuid4()),
                "metadata": {"test": "test"},
            }
            for i, embedding in enumerate(data)
        ],
        columns=["data", "embedding", "id", "hash", "metadata"],
    )
    df.hash = df.data.apply(lambda x: hashlib.sha256(x.encode()).hexdigest())
    unit_testing_datasets = ["unit_test_1", "unit_test_2"]
    for unit_testing_dataset in unit_testing_datasets:
        await vector_database.clear(unit_testing_dataset)
        await vector_database.update(df, unit_testing_dataset)
    results = await vector_database._multi_collections_scroll(
        unit_testing_datasets,
        query_filter=Filter(
            should=[FieldCondition(key="hash", match=MatchValue(value=df.hash[0]))]
        ),
    )
    # we expect to get duplicates because we are searching through multiple collections
    assert len(results) == 4
    assert len(set([result.id for result in results])) == 2