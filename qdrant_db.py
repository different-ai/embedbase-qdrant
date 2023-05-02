from embedbase.database import VectorDatabase


class Qdrant(VectorDatabase):
    def __init__(
        self,
    ):
        """
        Qdrant is powering the next generation of AI applications with advanced
        and high-performant vector similarity search technology.

        Qdrant is a vector database & vector similarity search engine. 
        It deploys as an API service providing search for the nearest high-dimensional vectors.
        With Qdrant, embeddings or neural network encoders can be turned into
        full-fledged applications for matching, searching, recommending, and much more!
        """
        raise NotImplementedError(
            "Qdrant is not yet implemented. Please use another database."
        )
