import { Result } from '@/request/Result'
import { get, post, del, put } from '@/request/index'
import type { datasetData } from '@/api/type/dataset'
import type { pageRequest } from '@/api/type/common'
import type { ApplicationFormType } from '@/api/type/application'
import { type Ref } from 'vue'
const prefix = '/dataset'

/**
 * Get a page of knowledge.
 * @param Parameters  
 * page {
          "current_page": "string",
          "page_size": "string",
        }
 * param {
          "name": "string",
        }
 */
const getDataset: (
  page: pageRequest,
  param: any,
  loading?: Ref<boolean>
) => Promise<Result<any>> = (page, param, loading) => {
  return get(`${prefix}/${page.current_page}/${page.page_size}`, param, loading)
}

/**
 * Get all knowledge.
 * @param Parameters
 */
const getAllDataset: (loading?: Ref<boolean>) => Promise<Result<any[]>> = (loading) => {
  return get(`${prefix}`, undefined, loading)
}

/**
 * Remove the Knowledge Base
 * @param Parameters dataset_id
 */
const delDataset: (dataset_id: String, loading?: Ref<boolean>) => Promise<Result<boolean>> = (
  dataset_id,
  loading
) => {
  return del(`${prefix}/${dataset_id}`, undefined, {}, loading)
}

/**
 * Creating a Knowledge Base
 * @param Parameters 
 * {
  "name": "string",
  "desc": "string",
  "documents": [
    {
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
  ]
}
 */
const postDataset: (data: datasetData, loading?: Ref<boolean>) => Promise<Result<any>> = (
  data,
  loading
) => {
  return post(`${prefix}`, data, undefined, loading, 1000 * 60 * 5)
}

/**
 * CreatedWebThe knowledge base
 * @param Parameters 
 * {
  "name": "string",
  "desc": "string",
  "source_url": "string",
  "selector": "string",
}
 */
const postWebDataset: (data: any, loading?: Ref<boolean>) => Promise<Result<any>> = (
  data,
  loading
) => {
  return post(`${prefix}/web`, data, undefined, loading)
}

/**
 * Information Base Details
 * @param Parameters dataset_id
 */
const getDatasetDetail: (dataset_id: string, loading?: Ref<boolean>) => Promise<Result<any>> = (
  dataset_id,
  loading
) => {
  return get(`${prefix}/${dataset_id}`, undefined, loading)
}

/**
 * Modification of Knowledge Base Information
 * @param Parameters 
 * dataset_id
 * {
      "name": "string",
      "desc": true
    }
 */
const putDataset: (dataset_id: string, data: any) => Promise<Result<any>> = (
  dataset_id,
  data: any
) => {
  return put(`${prefix}/${dataset_id}`, data)
}
/**
 * Acquire a Knowledge Base List of related applications
 * @param dataset_id
 * @param loading
 * @returns
 */
const listUsableApplication: (
  dataset_id: string,
  loading?: Ref<boolean>
) => Promise<Result<Array<ApplicationFormType>>> = (dataset_id, loading) => {
  return get(`${prefix}/${dataset_id}/application`, {}, loading)
}

/**
 * Test list of fate
 * @param dataset_id
 * @param loading
 * @query  { query_text: string, top_number: number, similarity: number }
 * @returns
 */
const getDatasetHitTest: (
  dataset_id: string,
  data: any,
  loading?: Ref<boolean>
) => Promise<Result<Array<any>>> = (dataset_id, data, loading) => {
  return get(`${prefix}/${dataset_id}/hit_test`, data, loading)
}

/**
 * synchronizing knowledge.
 * @param Parameters dataset_id
 * @query Parameters sync_type // Types of Sync->replace:Replacement of Sync.,complete:Complete synchronization
 */
const putSyncWebDataset: (
  dataset_id: string,
  sync_type: string,
  loading?: Ref<boolean>
) => Promise<Result<any>> = (dataset_id, sync_type, loading) => {
  return put(`${prefix}/${dataset_id}/sync_web`, undefined, { sync_type }, loading)
}

export default {
  getDataset,
  getAllDataset,
  delDataset,
  postDataset,
  getDatasetDetail,
  putDataset,
  listUsableApplication,
  getDatasetHitTest,
  postWebDataset,
  putSyncWebDataset
}
