from __future__ import annotations

import logging
import os
import uuid
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Iterable,
    List,
    Optional,
    Tuple,
    TypeVar,
)

import numpy as np
from langchain_core._api.deprecation import deprecated
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.utils.iter import batch_iterate
from langchain_core.vectorstores import VectorStore


logger = logging.getLogger(__name__)

VST = TypeVar("VST", bound=VectorStore)


def _import_endee() -> Any:
    """
    Try to import endee module. If it's not already installed, instruct user how to install.
    """
    try:
        import endee
        from endee import Endee
    except ImportError as e:
        raise ImportError(
            "Could not import endee python package. "
            "Please install it with `pip install endee`."
        ) from e
    return endee


class EndeeVectorStore(VectorStore):
    """Vector store for Endee vector database."""

    def __init__(
        self,
        endee_index: Optional[Any] = None,
        embedding: Optional[Embeddings] = None,
        text_key: str = "text",
        api_token: Optional[str] = None,
        index_name: Optional[str] = None,
        space_type: str = "cosine",
        dimension: Optional[int] = None,
        precision: str = "medium",
        encryption_key: Optional[str] = None,
    ):
        """Initialize with Endee client.

        Args:
            endee_index: Endee index instance
            embedding: Embedding function to use
            text_key: Key in metadata to store the text
            api_token: Endee API token
            index_name: Name of the index
            space_type: Distance metric (cosine, l2, ip)
            dimension: Dimension of vectors
            precision: Precision level (fp16, medium, high, ultra-high)
            encryption_key: Optional encryption key for client-side encryption
        """
        if embedding is None:
            raise ValueError("Embedding must be provided")
        self._embedding = embedding
        self._text_key = text_key
        self._encryption_key = encryption_key

        # If index is not provided, initialize it
        if endee_index is None:
            if api_token is None:
                raise ValueError("API token must be provided if endee_index is not provided")
            if index_name is None:
                raise ValueError("Index name must be provided if endee_index is not provided")
            
            endee_index = self._initialize_endee_index(
                api_token, index_name, dimension, space_type, precision, encryption_key
            )
        
        self._endee_index = endee_index

    @classmethod
    def _initialize_endee_index(
        cls,
        api_token: str,
        index_name: str,
        dimension: Optional[int] = None,
        space_type: str = "cosine",
        precision: str = "medium",
        encryption_key: Optional[str] = None,
    ) -> Any:
        """Initialize Endee index using the current API."""
        endee = _import_endee()
        from endee import Endee

        # Initialize Endee client
        nd = Endee(token=api_token)

        try:
            # Try to get existing index (with encryption key if provided)
            if encryption_key is not None:
                index = nd.get_index(name=index_name, key=encryption_key)
            else:
                index = nd.get_index(name=index_name)
            logger.info(f"Retrieved existing index: {index_name}")
            return index
        except Exception as e:
            if dimension is None:
                raise ValueError(
                    "Must provide dimension when creating a new index"
                ) from e
            
            # Create a new index if it doesn't exist
            logger.info(f"Creating new index: {index_name}")
            create_params = {
                "name": index_name,
                "dimension": dimension,
                "space_type": space_type,
                "precision": precision,
            }
            if encryption_key is not None:
                create_params["key"] = encryption_key
            
            nd.create_index(**create_params)

            # Get the newly created index
            if encryption_key is not None:
                return nd.get_index(name=index_name, key=encryption_key)
            else:
                return nd.get_index(name=index_name)
        
    @property
    def embeddings(self) -> Optional[Embeddings]:
        """Access the query embedding object if available."""
        return self._embedding

    def add_texts(
        self,
        texts: Iterable[str],
        metadatas: Optional[List[dict]] = None,
        ids: Optional[List[str]] = None,
        batch_size: int = 100,
        embedding_chunk_size: int = 100,
        *,
        async_req: bool = False,
        **kwargs: Any,
    ) -> List[str]:
        """Add texts to the vectorstore.

        Args:
            texts: Iterable of strings to add to the vectorstore.
            metadatas: Optional list of metadatas associated with the texts.
            ids: Optional list of ids to associate with the texts.
            batch_size: Batch size for insertion.
            embedding_chunk_size: Batch size for embedding generation.
            async_req: Whether to make asynchronous request (not supported yet).

        Returns:
            List of ids from adding the texts into the vectorstore.
        """
        texts = list(texts)
        ids = ids or [str(uuid.uuid4()) for _ in texts]
        metadatas = metadatas or [{} for _ in texts]
        
        for metadata, text in zip(metadatas, texts):
            metadata[self._text_key] = text

        # Process in batches
        for i in range(0, len(texts), batch_size):
            chunk_texts = texts[i : i + batch_size]
            chunk_ids = ids[i : i + batch_size]
            chunk_metadatas = metadatas[i : i + batch_size]
            
            # Generate embeddings
            embeddings = []
            for j in range(0, len(chunk_texts), embedding_chunk_size):
                sub_texts = chunk_texts[j : j + embedding_chunk_size]
                sub_embeddings = self._embedding.embed_documents(sub_texts)
                embeddings.extend(sub_embeddings)
            
            # Prepare entries for upsert
            entries = []
            for id, embedding, metadata in zip(chunk_ids, embeddings, chunk_metadatas):
                # Extract filter values - keep it simple for efficient filtering
                filter_data = {}

                for key, value in metadata.items():
                    if key not in ["text"]:
                        filter_data[key] = value
                
                
                entry = {
                    "id": id,
                    "vector": embedding,
                    "meta": metadata,
                    "filter": filter_data
                }
                entries.append(entry)
                
            # Insert to Endee
            self._endee_index.upsert(entries)

        return ids
    
    def similarity_search_with_score(
        self,
        query: str,
        k: int = 4,
        filter: Optional[List[dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> List[Tuple[Document, float]]:
        """Search with a text query and return documents and scores.

        Args:
            query: Text query.
            k: Number of results to return.
            filter: Optional filter dict.

        Returns:
            List of tuples of (document, similarity score).
        """
        embedding = self._embedding.embed_query(query)
        return self.similarity_search_by_vector_with_score(embedding, k=k, filter=filter)
    
    def similarity_search_by_vector_with_score(
        self,
        embedding: List[float],
        *,
        k: int = 4,
        filter: Optional[List[dict[str, Any]]] = None,
    ) -> List[Tuple[Document, float]]:
        """Search by vector and return documents and scores.

        Args:
            embedding: Query embedding.
            k: Number of results to return.
            filter: Optional filter dict.

        Returns:
            List of tuples of (document, similarity score).
        """
        docs = []

        # Execute query
        results = self._endee_index.query(
            vector=embedding, 
            top_k=k, 
            filter=filter,
            include_vectors=False
        )

        # Process results
        for res in results:
            metadata = res["meta"]
            if self._text_key in metadata:
                text = metadata.pop(self._text_key)
                score = res["similarity"]
                docs.append((Document(page_content=text, metadata=metadata), score))
            else:
                logger.warning(
                    f"Found document with no `{self._text_key}` key. Skipping."
                )
        return docs
    
    def similarity_search(
        self,
        query: str,
        k: int = 4,
        filter: Optional[List[dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> List[Document]:
        """Search with a text query and return documents.

        Args:
            query: Text query.
            k: Number of results to return.
            filter: Optional filter dict.

        Returns:
            List of documents.
        """
        docs_and_scores = self.similarity_search_with_score(
            query, k=k, filter=filter, **kwargs
        )
        return [doc for doc, _ in docs_and_scores]
    
    @classmethod
    def from_documents(
        cls,
        documents: List[Document],
        embedding: Embeddings,
        endee_index: Optional[Any] = None,
        ids: Optional[List[str]] = None,
        batch_size: int = 32,
        text_key: str = "text",
        index_name: Optional[str] = None,
        api_token: Optional[str] = None,
        space_type: str = "cosine",
        dimension: Optional[int] = None,
        precision: str = "medium",
        encryption_key: Optional[str] = None,
        **kwargs: Any,
    ) -> EndeeVectorStore:
        """Create a vector store from documents.

        Args:
            documents: List of Document objects to add.
            embedding: Embedding function.
            endee_index: Optional Endee index. If not provided, one will be created.
            ids: Optional list of ids.
            batch_size: Batch size for addition.
            text_key: Key to store text in metadata.
            index_name: Index name, required if endee_index not provided.
            api_token: Endee API token, required if endee_index not provided.
            space_type: Distance metric type.
            dimension: Vector dimension, must be provided when creating new index.
            precision: Precision level (fp16, medium, high, ultra-high)
            encryption_key: Optional encryption key for client-side encryption.

        Returns:
            EndeeVectorStore instance.
        """
        texts = [doc.page_content for doc in documents]
        metadatas = [doc.metadata for doc in documents]
        return cls.from_texts(
            texts=texts,
            embedding=embedding,
            metadatas=metadatas,
            endee_index=endee_index,
            ids=ids,
            batch_size=batch_size,
            text_key=text_key,
            index_name=index_name,
            api_token=api_token,
            space_type=space_type,
            dimension=dimension,
            precision=precision,
            encryption_key=encryption_key,
            **kwargs,
        )
    
    @classmethod
    def from_texts(
        cls,
        texts: List[str],
        embedding: Embeddings,
        metadatas: Optional[List[dict]] = None,
        endee_index: Optional[Any] = None,
        ids: Optional[List[str]] = None,
        batch_size: int = 32,
        text_key: str = "text",
        index_name: Optional[str] = None,
        api_token: Optional[str] = None,
        space_type: str = "cosine",
        dimension: Optional[int] = None,
        precision: str = "medium",
        encryption_key: Optional[str] = None,
        **kwargs: Any,
    ) -> EndeeVectorStore:
        """Create a vector store from texts.

        Args:
            texts: List of texts to add.
            embedding: Embedding function.
            metadatas: Optional list of metadatas.
            endee_index: Optional Endee index. If not provided, one will be created.
            ids: Optional list of ids.
            batch_size: Batch size for addition.
            text_key: Key to store text in metadata.
            index_name: Index name, required if endee_index not provided.
            api_token: Endee API token, required if endee_index not provided.
            space_type: Distance metric type.
            dimension: Vector dimension, can be inferred if not provided.
            precision: Precision level (fp16, medium, high, ultra-high)
            encryption_key: Optional encryption key for client-side encryption.

        Returns:
            EndeeVectorStore instance.
        """
        # If dimension not provided, infer from embedding
        if dimension is None and endee_index is None:
            raise ValueError("Dimension must be explicitly provided when creating a new index.")
            
        endee = cls(
            endee_index=endee_index,
            embedding=embedding,
            text_key=text_key,
            api_token=api_token,
            index_name=index_name,
            space_type=space_type,
            dimension=dimension,
            precision=precision,
            encryption_key=encryption_key,
        )

        endee.add_texts(
            texts,
            metadatas=metadatas,
            ids=ids,
            batch_size=batch_size,
        )
        return endee
    
    def delete(
        self,
        ids: Optional[List[str]] = None,
        filter: Optional[List[dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> None:
        """Delete by either ids or filter.

        Args:
            ids: List of ids to delete.
            filter: Filter to use for deletion.

        Returns:
            None
        """
        if ids is not None:
            # Delete by IDs - one at a time to avoid errors
            for id in ids:
                try:
                    self._endee_index.delete_vector(id)
                except Exception as e:
                    logger.warning(f"Error deleting vector with ID {id}: {e}")
        elif filter is not None:
            # Delete by filter
            try:
                self._endee_index.delete_with_filter(filter=filter)
            except Exception as e:
                logger.warning(f"Error deleting vectors with filter {filter}: {e}")
        else:
            raise ValueError("Either ids or filter must be provided.")

        return None
    
    @classmethod
    def from_params(
        cls,
        embedding: Embeddings,
        api_token: str,
        index_name: str,
        dimension: Optional[int] = None,
        space_type: str = "cosine",
        text_key: str = "text",
        precision: str = "medium",
        encryption_key: Optional[str] = None,
    ) -> "EndeeVectorStore":
        """Create EndeeVectorStore from parameters.
        
        Args:
            embedding: Embedding function
            api_token: Endee API token
            index_name: Name of the index
            dimension: Dimension of vectors
            space_type: Distance metric (cosine, l2, ip)
            text_key: Key in metadata to store the text
            precision: Precision level (fp16, medium, high, ultra-high)
            encryption_key: Optional encryption key for client-side encryption
            
        Returns:
            EndeeVectorStore instance
        """
        # If dimension not provided, infer from embedding
        # if dimension is None:
        #     raise ValueError("Dimension must be explicitly provided when creating a new index.")
            
        endee_index = cls._initialize_endee_index(
            api_token,index_name, dimension, space_type, precision, encryption_key
        )

        return cls(
            endee_index=endee_index,
            embedding=embedding,
            text_key=text_key,
            encryption_key=encryption_key,
        )