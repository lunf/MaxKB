import { Result } from '@/request/Result'
import { get, post, del, put } from '@/request/index'
import type { Ref } from 'vue'
import type { KeyValue } from '@/api/type/common'
import type { pageRequest } from '@/api/type/common'
const prefix = '/dataset'

/**
 * Section Preview（uploaded documents.）
 * @param Parameters  file:file,limit:number,patterns:array,with_filter:boolean
 */
const postSplitDocument: (data: any) => Promise<Result<any>> = (data) => {
  return post(`${prefix}/document/split`, data, undefined, undefined, 1000 * 60 * 60)
}

/**
 * Part Identification List
 * @param loading The carrier.
 * @returns Part Identification List
 */
const listSplitPattern: (
  loading?: Ref<boolean>
) => Promise<Result<Array<KeyValue<string, string>>>> = (loading) => {
  return get(`${prefix}/document/split_pattern`, {}, loading)
}

/**
 * List of Documents
 * @param Parameters  dataset_id,   
 * page {
              "current_page": "string",
              "page_size": "string",
            }
* param {
          "name": "string",
        }
 */

const getDocument: (
  dataset_id: string,
  page: pageRequest,
  param: any,
  loading?: Ref<boolean>
) => Promise<Result<any>> = (dataset_id, page, param, loading) => {
  return get(
    `${prefix}/${dataset_id}/document/${page.current_page}/${page.page_size}`,
    param,
    loading
  )
}

const getAllDocument: (dataset_id: string, loading?: Ref<boolean>) => Promise<Result<any>> = (
  dataset_id,
  loading
) => {
  return get(`${prefix}/${dataset_id}/document`, undefined, loading)
}

/**
 * Create a mass documentation.
 * @param Parameters 
 * {
  "name": "string",
  "paragraphs": [
    {
      "content": "string",
      "title": "string",
      "problem_list": [
          {
            "id": "string",
              "content": "string"
          }
      ]
    }
  ]
}
 */
const postDocument: (
  dataset_id: string,
  data: any,
  loading?: Ref<boolean>
) => Promise<Result<any>> = (dataset_id, data, loading) => {
  return post(`${prefix}/${dataset_id}/document/_bach`, data, {}, loading, 1000 * 60 * 5)
}

/**
 * Modifying the document.
 * @param Parameters 
 * dataset_id, document_id, 
 * {
      "name": "string",
      "is_active": true,
      "meta": {}
    }
 */
const putDocument: (
  dataset_id: string,
  document_id: string,
  data: any,
  loading?: Ref<boolean>
) => Promise<Result<any>> = (dataset_id, document_id, data: any, loading) => {
  return put(`${prefix}/${dataset_id}/document/${document_id}`, data, undefined, loading)
}

/**
 * Delete the document.
 * @param Parameters dataset_id, document_id,
 */
const delDocument: (
  dataset_id: string,
  document_id: string,
  loading?: Ref<boolean>
) => Promise<Result<boolean>> = (dataset_id, document_id, loading) => {
  return del(`${prefix}/${dataset_id}/document/${document_id}`, loading)
}
/**
 * Remove the document.
 * @param Parameters dataset_id,
 */
const delMulDocument: (
  dataset_id: string,
  data: any,
  loading?: Ref<boolean>
) => Promise<Result<boolean>> = (dataset_id, data, loading) => {
  return del(`${prefix}/${dataset_id}/document/_bach`, undefined, { id_list: data }, loading)
}
/**
 * Document Details
 * @param Parameters dataset_id
 */
const getDocumentDetail: (dataset_id: string, document_id: string) => Promise<Result<any>> = (
  dataset_id,
  document_id
) => {
  return get(`${prefix}/${dataset_id}/document/${document_id}`)
}

/**
 * Update the document to the quantum library.
 * @param Parameters 
 * dataset_id, document_id, 
 * {
      "name": "string",
      "is_active": true
    }
 */
const putDocumentRefresh: (
  dataset_id: string,
  document_id: string,
  loading?: Ref<boolean>
) => Promise<Result<any>> = (dataset_id, document_id, loading) => {
  return put(
    `${prefix}/${dataset_id}/document/${document_id}/refresh`,
    undefined,
    undefined,
    loading
  )
}

/**
 * Multiple synchronous documents
 * @param Parameters dataset_id,
 */
const delMulSyncDocument: (
  dataset_id: string,
  data: any,
  loading?: Ref<boolean>
) => Promise<Result<boolean>> = (dataset_id, data, loading) => {
  return put(`${prefix}/${dataset_id}/document/_bach`, { id_list: data }, undefined, loading)
}

/**
 * CreatedWebSite Documents
 * @param Parameters 
 * {
    "source_url_list": [
    "string"
  ],
  "selector": "string"
 }
}
 */
const postWebDocument: (
  dataset_id: string,
  data: any,
  loading?: Ref<boolean>
) => Promise<Result<any>> = (dataset_id, data, loading) => {
  return post(`${prefix}/${dataset_id}/document/web`, data, undefined, loading)
}

/**
 * Mass Migration Documents
 * @param Parameters dataset_id,target_dataset_id,
 */
const putMigrateMulDocument: (
  dataset_id: string,
  target_dataset_id: string,
  data: any,
  loading?: Ref<boolean>
) => Promise<Result<boolean>> = (dataset_id, target_dataset_id, data, loading) => {
  return put(
    `${prefix}/${dataset_id}/document/migrate/${target_dataset_id}`,
    data,
    undefined,
    loading
  )
}

/**
 * Modifying the way of life.
 * @param dataset_id The knowledge baseid
 * @param data       {id_list:[],hit_handling_method:'directly_return|optimization'}
 * @param loading
 * @returns
 */
const batchEditHitHandling: (
  dataset_id: string,
  data: any,
  loading?: Ref<boolean>
) => Promise<Result<boolean>> = (dataset_id, data, loading) => {
  return put(`${prefix}/${dataset_id}/document/batch_hit_handling`, data, undefined, loading)
}
export default {
  postSplitDocument,
  getDocument,
  getAllDocument,
  postDocument,
  putDocument,
  delDocument,
  delMulDocument,
  getDocumentDetail,
  listSplitPattern,
  putDocumentRefresh,
  delMulSyncDocument,
  postWebDocument,
  putMigrateMulDocument,
  batchEditHitHandling
}
