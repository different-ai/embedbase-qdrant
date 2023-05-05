import asyncio
from embedbase.database import VectorDatabase
from typing import Coroutine, List, Optional
from pandas import DataFrame
from embedbase.utils import BatchGenerator
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct
from qdrant_client.http.models import (
    Filter,
    FieldCondition,
    MatchValue,
    PointIdsList,
    FilterSelector,
    VectorParams,
    Distance,
    HasIdCondition,
)
from qdrant_client.http.exceptions import UnexpectedResponse

from embedbase.database.base import SearchResponse, SelectResponse, Dataset
from typing import Callable, TypeVar

T = TypeVar("T")


class Qdrant(VectorDatabase):
    """
    Qdrant is powering the next generation of AI applications with advanced
    and high-performant vector similarity search technology.

    Qdrant is a vector database & vector similarity search engine.
    It deploys as an API service providing search for the nearest high-dimensional vectors.
    With Qdrant, embeddings or neural network encoders can be turned into
    full-fledged applications for matching, searching, recommending, and much more!
    """

    client: QdrantClient

    def _try_or_create_collection(
        self, dataset_id: str, func: Callable[[], T], kwargs
    ) -> T:
        """
        Try to run the Qdrant function and if it fails, create the collection and try again.
        :param dataset_id: dataset id
        :param func: function to run
        """
        try:
            return func(**kwargs)
        except UnexpectedResponse as exc:
            if exc.status_code != 404:
                raise exc
            self.client.create_collection(
                collection_name=dataset_id,
                vectors_config=VectorParams(
                    size=self._dimensions, distance=Distance.COSINE
                ),
            )
            return func(**kwargs)

    def __init__(self, host: str = "localhost", port: int = 6333, **kwargs):
        """

        :param host: qdrant host
        :param port: qdrant port
        """

        super().__init__(**kwargs)

        self.client = QdrantClient(host=host, port=port)

    async def select(
        self,
        ids: List[str] = [],
        hashes: List[str] = [],
        dataset_id: Optional[str] = None,
        user_id: Optional[str] = None,
        distinct: bool = True,
    ):
        """
        :param ids: list of ids
        :param hashes: list of hashes
        :param dataset_id: dataset id
        :param user_id: user id
        :param distinct: distinct
        :return: list of documents
        """
        # either ids or hashes must be provided
        assert ids or hashes, "ids or hashes must be provided"

        must = []
        should = []
        if user_id:
            must.append(
                FieldCondition(key="user_id", range=MatchValue(value="user_id"))
            )
        if hashes:
            for h in hashes:
                should.append(FieldCondition(key="hash", match=MatchValue(value=h)))
        if ids:
            should.append(HasIdCondition(has_id=ids))

        try:
            search_result = self.client.scroll(
                collection_name=dataset_id,
                # query_vector=[0.0] * self._dimensions,
                query_filter=Filter(
                    should=should,
                    must=must,
                ),
                with_payload=True,
                with_vectors=True,
                # TODO pagination
                limit=10_000,
            )
        except UnexpectedResponse as exc:
            # ignore unexisting collections
            if exc.status_code != 404:
                raise exc
            return []
        responses = []
        for e in search_result[0]:
            responses.append(
                SelectResponse(
                    id=e.id,
                    data=e.payload.get("data"),
                    metadata=e.payload.get("metadata"),
                    hash=e.payload.get("hash"),
                    embedding=e.vector,
                )
            )
        return responses

    async def update(
        self,
        df: DataFrame,
        dataset_id: str,
        user_id: Optional[str] = None,
        batch_size: Optional[int] = 100,
        # todo: implement store_data someday
        store_data: bool = True,
    ):
        df_batcher = BatchGenerator(batch_size)
        batches = [batch_df for batch_df in df_batcher(df)]

        async def _insert(batch_df: DataFrame):
            points = [
                PointStruct(
                    id=row.id,
                    vector=row.embedding,
                    payload={
                        "dataset_id": dataset_id,
                        "user_id": user_id,
                        "metadata": row.metadata,
                        "data": row.data,
                        "hash": row.hash,
                    },
                )
                for _, row in batch_df.iterrows()
            ]

            response = self._try_or_create_collection(
                dataset_id=dataset_id,
                func=self.client.upsert,
                kwargs={"collection_name": dataset_id, "points": points},
            )
            return response

        await asyncio.gather(*[_insert(batch_df) for batch_df in batches])

    async def delete(
        self,
        ids: List[str],
        dataset_id: str,
        user_id: Optional[str] = None,
    ):
        must = [
            HasIdCondition(has_id=ids),
        ]
        if user_id:
            must.append(
                FieldCondition(key="user_id", range=MatchValue(value="user_id"))
            )
        try:
            self.client.delete(
                wait=True,
                collection_name=dataset_id,
                points_selector=FilterSelector(
                    filter=Filter(
                        must=must,
                    )
                ),
            )
        except UnexpectedResponse as exc:
            # ignore unexisting collections
            if exc.status_code != 404:
                raise exc

    async def search(
        self,
        vector: List[float],
        top_k: Optional[int],
        dataset_ids: List[str],
        user_id: Optional[str] = None,
    ):
        must = []
        if user_id:
            must.append(
                FieldCondition(key="user_id", range=MatchValue(value="user_id"))
            )
        try:
            search_result = self.client.search(
                # TODO: does not support cross-collection search atm
                collection_name=dataset_ids[0],
                query_vector=vector,
                limit=top_k,
                query_filter=Filter(
                    must=must,
                ),
                with_vectors=True,
                with_payload=True,
            )
        except UnexpectedResponse as exc:
            # ignore unexisting collections
            if exc.status_code != 404:
                raise exc
            return []
        search_response = []
        for e in search_result:
            search_response.append(
                SearchResponse(
                    id=e.id,
                    score=e.score,
                    data=e.payload.get("data"),
                    metadata=e.payload.get("metadata"),
                    hash=e.payload.get("hash"),
                    embedding=e.vector,
                )
            )
        return search_response

    async def clear(self, dataset_id: str, user_id: Optional[str] = None):
        """
        :param dataset_id: dataset id
        :param user_id: user id
        """
        must = []
        if user_id:
            must.append(
                FieldCondition(key="user_id", range=MatchValue(value="user_id"))
            )
        try:
            self.client.delete(
                wait=True,
                collection_name=dataset_id,
                points_selector=FilterSelector(filter=Filter(must=must)),
            )
        except UnexpectedResponse as exc:
            # ignore unexisting collection
            if exc.status_code != 404:
                raise

    async def get_datasets(self, user_id: Optional[str] = None):
        """
        :param user_id: user id
        :return: list of datasets
        """
        must = []
        if user_id:
            must.append(
                FieldCondition(key="user_id", range=MatchValue(value="user_id"))
            )
        result = self.client.get_collections()
        response = []
        # todo: parallelize
        for e in result.collections:
            count = self.client.count(
                collection_name=e.name,
                count_filter=Filter(
                    must=must,
                ),
            )
            response.append(
                Dataset(
                    dataset_id=e.name,
                    documents_count=count,
                )
            )
        return response
