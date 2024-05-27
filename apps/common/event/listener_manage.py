# coding=utf-8
"""
    @project: maxkb
    @Author:The Tiger
    @file: listener_manage.py
    @date:2023/10/20 14:01
    @desc:
"""
import logging
import os
import traceback
from typing import List

import django.db.models
from blinker import signal
from django.db.models import QuerySet

from common.config.embedding_config import VectorStore, EmbeddingModel
from common.db.search import native_search, get_dynamics_model
from common.event.common import poxy, embedding_poxy
from common.util.file_util import get_file_content
from common.util.fork import ForkManage, Fork
from common.util.lock import try_lock, un_lock
from dataset.models import Paragraph, Status, Document, ProblemParagraphMapping
from embedding.models import SourceType
from smartdoc.conf import PROJECT_DIR

max_kb_error = logging.getLogger("max_kb_error")
max_kb = logging.getLogger("max_kb")


class SyncWebDatasetArgs:
    def __init__(self, lock_key: str, url: str, selector: str, handler):
        self.lock_key = lock_key
        self.url = url
        self.selector = selector
        self.handler = handler


class SyncWebDocumentArgs:
    def __init__(self, source_url_list: List[str], selector: str, handler):
        self.source_url_list = source_url_list
        self.selector = selector
        self.handler = handler


class UpdateProblemArgs:
    def __init__(self, problem_id: str, problem_content: str):
        self.problem_id = problem_id
        self.problem_content = problem_content


class UpdateEmbeddingDatasetIdArgs:
    def __init__(self, paragraph_id_list: List[str], target_dataset_id: str):
        self.paragraph_id_list = paragraph_id_list
        self.target_dataset_id = target_dataset_id


class UpdateEmbeddingDocumentIdArgs:
    def __init__(self, paragraph_id_list: List[str], target_document_id: str, target_dataset_id: str):
        self.paragraph_id_list = paragraph_id_list
        self.target_document_id = target_document_id
        self.target_dataset_id = target_dataset_id


class ListenerManagement:
    embedding_by_problem_signal = signal("embedding_by_problem")
    embedding_by_paragraph_signal = signal("embedding_by_paragraph")
    embedding_by_dataset_signal = signal("embedding_by_dataset")
    embedding_by_document_signal = signal("embedding_by_document")
    delete_embedding_by_document_signal = signal("delete_embedding_by_document")
    delete_embedding_by_document_list_signal = signal("delete_embedding_by_document_list")
    delete_embedding_by_dataset_signal = signal("delete_embedding_by_dataset")
    delete_embedding_by_paragraph_signal = signal("delete_embedding_by_paragraph")
    delete_embedding_by_source_signal = signal("delete_embedding_by_source")
    enable_embedding_by_paragraph_signal = signal('enable_embedding_by_paragraph')
    disable_embedding_by_paragraph_signal = signal('disable_embedding_by_paragraph')
    init_embedding_model_signal = signal('init_embedding_model')
    sync_web_dataset_signal = signal('sync_web_dataset')
    sync_web_document_signal = signal('sync_web_document')
    update_problem_signal = signal('update_problem')
    delete_embedding_by_source_ids_signal = signal('delete_embedding_by_source_ids')
    delete_embedding_by_dataset_id_list_signal = signal("delete_embedding_by_dataset_id_list")

    @staticmethod
    def embedding_by_problem(args):
        VectorStore.get_embedding_vector().save(**args)

    @staticmethod
    @embedding_poxy
    def embedding_by_paragraph(paragraph_id):
        """
        Quantitative Paragraphs According to paragraphid
        :param paragraph_id: Paragraphsid
        :return: None
        """
        max_kb.info(f"Started--->Quantitative Paragraphs:{paragraph_id}")
        status = Status.success
        try:
            data_list = native_search(
                {'problem': QuerySet(get_dynamics_model({'paragraph.id': django.db.models.CharField()})).filter(
                    **{'paragraph.id': paragraph_id}),
                    'paragraph': QuerySet(Paragraph).filter(id=paragraph_id)},
                select_string=get_file_content(
                    os.path.join(PROJECT_DIR, "apps", "common", 'sql', 'list_embedding_text.sql')))
            # Delete the paragraph.
            VectorStore.get_embedding_vector().delete_by_paragraph_id(paragraph_id)
            # Mass to quantity.
            VectorStore.get_embedding_vector().batch_save(data_list)
        except Exception as e:
            max_kb_error.error(f'Quantitative Paragraphs:{paragraph_id}There are errors.{str(e)}{traceback.format_exc()}')
            status = Status.error
        finally:
            QuerySet(Paragraph).filter(id=paragraph_id).update(**{'status': status})
            max_kb.info(f'ended--->Quantitative Paragraphs:{paragraph_id}')

    @staticmethod
    @embedding_poxy
    def embedding_by_document(document_id):
        """
        Quantitative Documents
        :param document_id: Documentsid
        :return: None
        """
        max_kb.info(f"Started--->Quantitative Documents:{document_id}")
        status = Status.success
        try:
            data_list = native_search(
                {'problem': QuerySet(
                    get_dynamics_model({'paragraph.document_id': django.db.models.CharField()})).filter(
                    **{'paragraph.document_id': document_id}),
                    'paragraph': QuerySet(Paragraph).filter(document_id=document_id)},
                select_string=get_file_content(
                    os.path.join(PROJECT_DIR, "apps", "common", 'sql', 'list_embedding_text.sql')))
            # Delete the document data.
            VectorStore.get_embedding_vector().delete_by_document_id(document_id)
            # Mass to quantity.
            VectorStore.get_embedding_vector().batch_save(data_list)
        except Exception as e:
            max_kb_error.error(f'Quantitative Documents:{document_id}There are errors.{str(e)}{traceback.format_exc()}')
            status = Status.error
        finally:
            # Modified state
            QuerySet(Document).filter(id=document_id).update(**{'status': status})
            QuerySet(Paragraph).filter(document_id=document_id).update(**{'status': status})
            max_kb.info(f"ended--->Quantitative Documents:{document_id}")

    @staticmethod
    @embedding_poxy
    def embedding_by_dataset(dataset_id):
        """
        Quantitative Knowledge Base
        :param dataset_id: The knowledge baseid
        :return: None
        """
        max_kb.info(f"Started--->to quantitative data. {dataset_id}")
        try:
            document_list = QuerySet(Document).filter(dataset_id=dataset_id)
            max_kb.info(f"Data collection documents:{[d.name for d in document_list]}")
            for document in document_list:
                ListenerManagement.embedding_by_document(document.id)
        except Exception as e:
            max_kb_error.error(f'to quantitative data. {dataset_id}There are errors.{str(e)}{traceback.format_exc()}')
        finally:
            max_kb.info(f"ended--->to quantitative data. {dataset_id}")

    @staticmethod
    def delete_embedding_by_document(document_id):
        VectorStore.get_embedding_vector().delete_by_document_id(document_id)

    @staticmethod
    def delete_embedding_by_document_list(document_id_list: List[str]):
        VectorStore.get_embedding_vector().delete_bu_document_id_list(document_id_list)

    @staticmethod
    def delete_embedding_by_dataset(dataset_id):
        VectorStore.get_embedding_vector().delete_by_dataset_id(dataset_id)

    @staticmethod
    def delete_embedding_by_paragraph(paragraph_id):
        VectorStore.get_embedding_vector().delete_by_paragraph_id(paragraph_id)

    @staticmethod
    def delete_embedding_by_source(source_id):
        VectorStore.get_embedding_vector().delete_by_source_id(source_id, SourceType.PROBLEM)

    @staticmethod
    def disable_embedding_by_paragraph(paragraph_id):
        VectorStore.get_embedding_vector().update_by_paragraph_id(paragraph_id, {'is_active': False})

    @staticmethod
    def enable_embedding_by_paragraph(paragraph_id):
        VectorStore.get_embedding_vector().update_by_paragraph_id(paragraph_id, {'is_active': True})

    @staticmethod
    @poxy
    def sync_web_document(args: SyncWebDocumentArgs):
        for source_url in args.source_url_list:
            result = Fork(base_fork_url=source_url, selector_list=args.selector.split(' ')).fork()
            args.handler(source_url, args.selector, result)

    @staticmethod
    @poxy
    def sync_web_dataset(args: SyncWebDatasetArgs):
        if try_lock('sync_web_dataset' + args.lock_key):
            try:
                ForkManage(args.url, args.selector.split(" ") if args.selector is not None else []).fork(2, set(),
                                                                                                         args.handler)
            except Exception as e:
                logging.getLogger("max_kb_error").error(f'{str(e)}:{traceback.format_exc()}')
            finally:
                un_lock('sync_web_dataset' + args.lock_key)

    @staticmethod
    def update_problem(args: UpdateProblemArgs):
        problem_paragraph_mapping_list = QuerySet(ProblemParagraphMapping).filter(problem_id=args.problem_id)
        embed_value = VectorStore.get_embedding_vector().embed_query(args.problem_content)
        VectorStore.get_embedding_vector().update_by_source_ids([v.id for v in problem_paragraph_mapping_list],
                                                                {'embedding': embed_value})

    @staticmethod
    def update_embedding_dataset_id(args: UpdateEmbeddingDatasetIdArgs):
        VectorStore.get_embedding_vector().update_by_paragraph_ids(args.paragraph_id_list,
                                                                   {'dataset_id': args.target_dataset_id})

    @staticmethod
    def update_embedding_document_id(args: UpdateEmbeddingDocumentIdArgs):
        VectorStore.get_embedding_vector().update_by_paragraph_ids(args.paragraph_id_list,
                                                                   {'document_id': args.target_document_id,
                                                                    'dataset_id': args.target_dataset_id})

    @staticmethod
    def delete_embedding_by_source_ids(source_ids: List[str]):
        VectorStore.get_embedding_vector().delete_by_source_ids(source_ids, SourceType.PROBLEM)

    @staticmethod
    def delete_embedding_by_paragraph_ids(paragraph_ids: List[str]):
        VectorStore.get_embedding_vector().delete_by_paragraph_ids(paragraph_ids)

    @staticmethod
    def delete_embedding_by_dataset_id_list(source_ids: List[str]):
        VectorStore.get_embedding_vector().delete_by_dataset_id_list(source_ids)

    @staticmethod
    @poxy
    def init_embedding_model(ages):
        EmbeddingModel.get_embedding_model()

    def run(self):
        #  Added quantity. according to the question.id
        ListenerManagement.embedding_by_problem_signal.connect(self.embedding_by_problem)
        #  Added quantity. According to paragraphid
        ListenerManagement.embedding_by_paragraph_signal.connect(self.embedding_by_paragraph)
        #  Added quantity. According to the Knowledge Baseid
        ListenerManagement.embedding_by_dataset_signal.connect(
            self.embedding_by_dataset)
        #  Added quantity. According to the documentationid
        ListenerManagement.embedding_by_document_signal.connect(
            self.embedding_by_document)
        # removed The quantity According to the documentation
        ListenerManagement.delete_embedding_by_document_signal.connect(self.delete_embedding_by_document)
        # removed The quantity According to the documentationidList of
        ListenerManagement.delete_embedding_by_document_list_signal.connect(self.delete_embedding_by_document_list)
        # removed The quantity According to the Knowledge Baseid
        ListenerManagement.delete_embedding_by_dataset_signal.connect(self.delete_embedding_by_dataset)
        # Remove the quantity. According to paragraphid
        ListenerManagement.delete_embedding_by_paragraph_signal.connect(
            self.delete_embedding_by_paragraph)
        # Remove the quantity. According to resourcesid
        ListenerManagement.delete_embedding_by_source_signal.connect(self.delete_embedding_by_source)
        # Prohibited paragraphs
        ListenerManagement.disable_embedding_by_paragraph_signal.connect(self.disable_embedding_by_paragraph)
        # Start the section.
        ListenerManagement.enable_embedding_by_paragraph_signal.connect(self.enable_embedding_by_paragraph)
        # Initialization to Quantitative Models
        ListenerManagement.init_embedding_model_signal.connect(self.init_embedding_model)
        # synchronizedwebSite Knowledge Base
        ListenerManagement.sync_web_dataset_signal.connect(self.sync_web_dataset)
        # synchronizedwebThe site Documents
        ListenerManagement.sync_web_document_signal.connect(self.sync_web_document)
        # Update the problem.
        ListenerManagement.update_problem_signal.connect(self.update_problem)
        ListenerManagement.delete_embedding_by_source_ids_signal.connect(self.delete_embedding_by_source_ids)
        ListenerManagement.delete_embedding_by_dataset_id_list_signal.connect(self.delete_embedding_by_dataset_id_list)
