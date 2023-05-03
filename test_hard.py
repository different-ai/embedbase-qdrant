"""
Tests at the database abstraction level.
"""

import hashlib
from typing import List

import numpy as np
import pandas as pd
import pytest
import uuid
from embedbase.database.base import VectorDatabase
from qdrant_db import Qdrant
unit_testing_dataset = "unit_test"
vector_databases: List[VectorDatabase] = [Qdrant(host="localhost", port=6333)]

@pytest.mark.asyncio
async def test_search():
    d = [
        "Bob is a human",
        "The quick brown fox jumps over the lazy dog",
    ]
    embeddings = [
        # random embedding of length 1536
        np.random.rand(1536).tolist(),
        np.random.rand(1536).tolist(),
    ]
    df = pd.DataFrame(
        [
            {
                "data": d[i],
                "embedding": embedding,
                "id": str(uuid.uuid4()),
                "metadata": {"test": "test"},
            }
            for i, embedding in enumerate(embeddings)
        ],
        columns=["data", "embedding", "id", "hash", "metadata"],
    )
    df.hash = df.data.apply(lambda x: hashlib.sha256(x.encode()).hexdigest())

    for vector_database in vector_databases:
        await vector_database.clear(unit_testing_dataset)
        await vector_database.update(df, unit_testing_dataset)
        results = await vector_database.search(
            embeddings[0],
            top_k=2,
            dataset_ids=[unit_testing_dataset],
        )
        assert len(results) > 0, f"failed for {vector_database}"
        assert results[0].id == df.id[0], f"failed for {vector_database}"
        assert results[0].data == d[0], f"failed for {vector_database}"
        assert len(results[0].embedding) > 0, f"failed for {vector_database}"
        assert results[0].score > 0, f"failed for {vector_database}"


@pytest.mark.asyncio
async def test_fetch():
    d = [
        "Bob is a human",
        "The quick brown fox jumps over the lazy dog",
    ]
    embeddings = [
        [0.0] * 1536,
        [0.0] * 1536,
    ]
    df = pd.DataFrame(
        [
            {
                "data": d[i],
                "embedding": embedding,
                "id": str(uuid.uuid4()),
                "metadata": {"test": "test"},
            }
            for i, embedding in enumerate(embeddings)
        ],
        columns=["data", "embedding", "id", "hash", "metadata"],
    )
    df.hash = df.data.apply(lambda x: hashlib.sha256(x.encode()).hexdigest())

    for vector_database in vector_databases:
        await vector_database.clear(unit_testing_dataset)
        await vector_database.update(df, unit_testing_dataset)
        results = await vector_database.select(
            ids=[df.id[0]], dataset_id=unit_testing_dataset
        )
        assert len(results) > 0, f"failed for {vector_database}"
        assert results[0].id == df.id[0], f"failed for {vector_database}"


@pytest.mark.asyncio
async def test_fetch_by_hash():
    d = [
        "Bob is a human",
        "The quick brown fox jumps over the lazy dog",
    ]
    embeddings = [
        [0.0] * 1536,
        [0.0] * 1536,
    ]
    df = pd.DataFrame(
        [
            {
                "data": d[i],
                "embedding": embedding,
                "id": str(uuid.uuid4()),
                "metadata": {"test": "test"},
            }
            for i, embedding in enumerate(embeddings)
        ],
        columns=["data", "embedding", "id", "hash", "metadata"],
    )
    df.hash = df.data.apply(lambda x: hashlib.sha256(x.encode()).hexdigest())

    for vector_database in vector_databases:
        await vector_database.clear(unit_testing_dataset)
        await vector_database.update(df, unit_testing_dataset)
        results = await vector_database.select(
            hashes=[df.hash[0]], dataset_id=unit_testing_dataset
        )
        assert len(results) > 0, f"failed for {vector_database}"
        assert results[0].id == df.id[0], f"failed for {vector_database}"


@pytest.mark.asyncio
async def test_clear():
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

    for vector_database in vector_databases:
        await vector_database.clear(unit_testing_dataset)
        await vector_database.update(df, unit_testing_dataset)
        results = await vector_database.search(
            data[0],
            top_k=2,
            dataset_ids=[unit_testing_dataset],
        )
        ids = [result.id for result in results]
        assert ids[0] == df.id[0], f"failed for {vector_database}"
        assert ids[1] == df.id[1], f"failed for {vector_database}"
        # check there is score
        assert results[0].score >= 0, f"failed for {vector_database}"
        await vector_database.clear(unit_testing_dataset)

    for vector_database in vector_databases:
        results = await vector_database.search(
            data[0],
            top_k=2,
            dataset_ids=[unit_testing_dataset],
        )
        assert len(results) == 0, f"failed for {vector_database}"


@pytest.mark.asyncio
async def test_upload():
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
        columns=[
            "data",
            "embedding",
            "id",
            "hash",
            "metadata",
        ],
    )
    df.hash = df.data.apply(lambda x: hashlib.sha256(x.encode()).hexdigest())

    for vector_database in vector_databases:
        await vector_database.clear(unit_testing_dataset)
        await vector_database.update(df, unit_testing_dataset)

        results = await vector_database.search(
            data[0],
            top_k=2,
            dataset_ids=[unit_testing_dataset],
        )
        ids = [result.id for result in results]
        assert ids[0] == df.id[0], f"failed for {vector_database}"
        assert ids[1] == df.id[1], f"failed for {vector_database}"


@pytest.mark.asyncio
async def test_batch_select_large_content():
    """
    should not throw an error
    """
    d = []
    for i in range(1000):
        d.append("a" * i)
    hashes = [hashlib.sha256(x.encode()).hexdigest() for x in d]
    for vector_database in vector_databases:
        # add documents
        await vector_database.clear(unit_testing_dataset)
        await vector_database.update(
            pd.DataFrame(
                [
                    {
                        "data": x,
                        "embedding": [0.0] * 1536,
                        "id": str(uuid.uuid4()),
                        "metadata": {"test": "test"},
                        "hash": hashes[i],
                    }
                    for i, x in enumerate(d)
                ],
                columns=["data", "embedding", "id", "hash", "metadata"],
            ),
            unit_testing_dataset,
        )
        results = await vector_database.select(
            hashes=list(set(hashes)),
            dataset_id=unit_testing_dataset,
            user_id=None,
        )
        assert len(list(results)) == len(d), f"failed for {vector_database}"
