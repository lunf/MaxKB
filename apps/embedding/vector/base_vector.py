# coding=utf-8
"""
    @project: maxkb
    @Author：The Tiger
    @file： base_vector.py
    @date：2023/10/18 19:16
    @desc:
"""
import threading
from abc import ABC, abstractmethod
from typing import List, Dict

from langchain_community.embeddings import HuggingFaceEmbeddings

from common.config.embedding_config import EmbeddingModel
from common.util.common import sub_array
from embedding.models import SourceType, SearchMode

lock = threading.Lock()


class BaseVectorStore(ABC):
    vector_exists = False

    @abstractmethod
    def vector_is_create(self) -> bool:
        """
        To determine whether the quota is created.
        :return: Create a quantum.
        """
        pass

    @abstractmethod
    def vector_create(self):
        """
        Created to quantum.
        :return:
        """
        pass

    def save_pre_handler(self):
        """
        Enter the front processor. Especially to determine whether the quantum library is created.
        :return: True
        """
        if not BaseVectorStore.vector_exists:
            if not self.vector_is_create():
                self.vector_create()
                BaseVectorStore.vector_exists = True
        return True

    def save(self, text, source_type: SourceType, dataset_id: str, document_id: str, paragraph_id: str, source_id: str,
             is_active: bool,
             embedding=None):
        """
        Introduction of data
        :param source_id:  Resourcesid
        :param dataset_id: The knowledge baseid
        :param text: The text
        :param source_type: Type of Resource
        :param document_id: Documentsid
        :param is_active:   is prohibited.
        :param embedding:   The Quantitative Processor
        :param paragraph_id Paragraphsid
        :return:  bool
        """

        if embedding is None:
            embedding = EmbeddingModel.get_embedding_model()
        self.save_pre_handler()
        self._save(text, source_type, dataset_id, document_id, paragraph_id, source_id, is_active, embedding)

    def batch_save(self, data_list: List[Dict], embedding=None):
        # Get the lock.
        lock.acquire()
        try:
            """
            Mass entrance.
            :param data_list: List of data
            :param embedding: The Quantitative Processor
            :return: bool
            """
            if embedding is None:
                embedding = EmbeddingModel.get_embedding_model()
            self.save_pre_handler()
            result = sub_array(data_list)
            for child_array in result:
                self._batch_save(child_array, embedding)
        finally:
            # Release the lock.
            lock.release()
        return True

    @abstractmethod
    def _save(self, text, source_type: SourceType, dataset_id: str, document_id: str, paragraph_id: str, source_id: str,
              is_active: bool,
              embedding: HuggingFaceEmbeddings):
        pass

    @abstractmethod
    def _batch_save(self, text_list: List[Dict], embedding: HuggingFaceEmbeddings):
        pass

    def search(self, query_text, dataset_id_list: list[str], exclude_document_id_list: list[str],
               exclude_paragraph_list: list[str],
               is_active: bool,
               embedding: HuggingFaceEmbeddings):
        if dataset_id_list is None or len(dataset_id_list) == 0:
            return []
        embedding_query = embedding.embed_query(query_text)
        result = self.query(embedding_query, dataset_id_list, exclude_document_id_list, exclude_paragraph_list,
                            is_active, 1, 0.65)
        return result[0]

    @abstractmethod
    def query(self, query_text:str,query_embedding: List[float],  dataset_id_list: list[str],
              exclude_document_id_list: list[str],
              exclude_paragraph_list: list[str], is_active: bool, top_n: int, similarity: float,
              search_mode: SearchMode):
        pass

    @abstractmethod
    def hit_test(self, query_text, dataset_id: list[str], exclude_document_id_list: list[str], top_number: int,
                 similarity: float,
                 search_mode: SearchMode,
                 embedding: HuggingFaceEmbeddings):
        pass

    @abstractmethod
    def update_by_paragraph_id(self, paragraph_id: str, instance: Dict):
        pass

    @abstractmethod
    def update_by_source_id(self, source_id: str, instance: Dict):
        pass

    @abstractmethod
    def update_by_source_ids(self, source_ids: List[str], instance: Dict):
        pass

    @abstractmethod
    def embed_documents(self, text_list: List[str]):
        pass

    @abstractmethod
    def embed_query(self, text: str):
        pass

    @abstractmethod
    def delete_by_dataset_id(self, dataset_id: str):
        pass

    @abstractmethod
    def delete_by_document_id(self, document_id: str):
        pass

    @abstractmethod
    def delete_bu_document_id_list(self, document_id_list: List[str]):
        pass

    @abstractmethod
    def delete_by_dataset_id_list(self, dataset_id_list: List[str]):
        pass

    @abstractmethod
    def delete_by_source_id(self, source_id: str, source_type: str):
        pass

    @abstractmethod
    def delete_by_source_ids(self, source_ids: List[str], source_type: str):
        pass

    @abstractmethod
    def delete_by_paragraph_id(self, paragraph_id: str):
        pass
