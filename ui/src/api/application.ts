import { Result } from '@/request/Result'
import { get, post, postStream, del, put } from '@/request/index'
import type { pageRequest } from '@/api/type/common'
import type { ApplicationFormType } from '@/api/type/application'
import { type Ref } from 'vue'

const prefix = '/application'

/**
 * Get all applications.
 * @param Parameters
 */
const getAllAppilcation: () => Promise<Result<any[]>> = () => {
  return get(`${prefix}`)
}

/**
 * Acquired page application.
 * page {
          "current_page": "string",
          "page_size": "string",
        }
 * param {
          "name": "string",
        }
 */
const getApplication: (
  page: pageRequest,
  param: any,
  loading?: Ref<boolean>
) => Promise<Result<any>> = (page, param, loading) => {
  return get(`${prefix}/${page.current_page}/${page.page_size}`, param, loading)
}

/**
 * Creating Applications
 * @param Parameters
 */
const postApplication: (
  data: ApplicationFormType,
  loading?: Ref<boolean>
) => Promise<Result<any>> = (data, loading) => {
  return post(`${prefix}`, data, undefined, loading)
}

/**
 * Modification of Application
 * @param Parameters 

 */
const putApplication: (
  application_id: String,
  data: ApplicationFormType,
  loading?: Ref<boolean>
) => Promise<Result<any>> = (application_id, data, loading) => {
  return put(`${prefix}/${application_id}`, data, undefined, loading)
}

/**
 * Remove the application.
 * @param Parameters application_id
 */
const delApplication: (
  application_id: String,
  loading?: Ref<boolean>
) => Promise<Result<boolean>> = (application_id, loading) => {
  return del(`${prefix}/${application_id}`, undefined, {}, loading)
}

/**
 * Application Details
 * @param Parameters application_id
 */
const getApplicationDetail: (
  application_id: string,
  loading?: Ref<boolean>
) => Promise<Result<any>> = (application_id, loading) => {
  return get(`${prefix}/${application_id}`, undefined, loading)
}

/**
 * Acquired the knowledge base available for current applications
 * @param Parameters application_id
 */
const getApplicationDataset: (
  application_id: string,
  loading?: Ref<boolean>
) => Promise<Result<any>> = (application_id, loading) => {
  return get(`${prefix}/${application_id}/list_dataset`, undefined, loading)
}

/**
 * obtainedAccessToken
 * @param Parameters application_id
 */
const getAccessToken: (application_id: string, loading?: Ref<boolean>) => Promise<Result<any>> = (
  application_id,
  loading
) => {
  return get(`${prefix}/${application_id}/access_token`, undefined, loading)
}

/**
 * ModifiedAccessToken
 * @param Parameters application_id
 * data {
 *  "is_active": true
 * }
 */
const putAccessToken: (
  application_id: string,
  data: any,
  loading?: Ref<boolean>
) => Promise<Result<any>> = (application_id, data, loading) => {
  return put(`${prefix}/${application_id}/access_token`, data, undefined, loading)
}

/**
 * Applied certification
 * @param Parameters 
 {
  "access_token": "string"
}
 */
const postAppAuthentication: (access_token: string, loading?: Ref<boolean>) => Promise<any> = (
  access_token,
  loading
) => {
  return post(`${prefix}/authentication`, { access_token }, undefined, loading)
}

/**
 * Dialogue to obtain applicable information
 * @param Parameters 
 {
  "access_token": "string"
}
 */
const getProfile: (loading?: Ref<boolean>) => Promise<any> = (loading) => {
  return get(`${prefix}/profile`, undefined, loading)
}

/**
 * Get a temporary response.Id
 * @param Parameters 

}
 */
const postChatOpen: (data: ApplicationFormType) => Promise<Result<any>> = (data) => {
  return post(`${prefix}/chat/open`, data)
}

/**
 * Official ReplyId
 * @param Parameters 
 * {
  "model_id": "string",
  "multiple_rounds_dialogue": true,
  "dataset_id_list": [
    "string"
  ]
}
 */
const getChatOpen: (application_id: String) => Promise<Result<any>> = (application_id) => {
  return get(`${prefix}/${application_id}/chat/open`)
}
/**
 * Dialogue
 * @param Parameters
 * chat_id: string
 * data
 */
const postChatMessage: (chat_id: string, data: any) => Promise<any> = (chat_id, data) => {
  return postStream(`/api${prefix}/chat_message/${chat_id}`, data)
}

/**
 * The praise. step down.
 * @param Parameters 
 * application_id : string; chat_id : string; chat_record_id : string
 * {
    "vote_status": "string", // -1 0 1
  }
 */
const putChatVote: (
  application_id: string,
  chat_id: string,
  chat_record_id: string,
  vote_status: string,
  loading?: Ref<boolean>
) => Promise<any> = (application_id, chat_id, chat_record_id, vote_status, loading) => {
  return put(
    `${prefix}/${application_id}/chat/${chat_id}/chat_record/${chat_record_id}/vote`,
    {
      vote_status
    },
    undefined,
    loading
  )
}

/**
 * Test list of fate
 * @param application_id
 * @param loading
 * @query  { query_text: string, top_number: number, similarity: number }
 * @returns
 */
const getApplicationHitTest: (
  application_id: string,
  data: any,
  loading?: Ref<boolean>
) => Promise<Result<Array<any>>> = (application_id, data, loading) => {
  return get(`${prefix}/${application_id}/hit_test`, data, loading)
}

/**
 * Get a list of models available to current users
 * @param application_id
 * @param loading
 * @query  { query_text: string, top_number: number, similarity: number }
 * @returns
 */
const getApplicationModel: (
  application_id: string,
  loading?: Ref<boolean>
) => Promise<Result<Array<any>>> = (application_id, loading) => {
  return get(`${prefix}/${application_id}/model`, loading)
}

export default {
  getAllAppilcation,
  getApplication,
  postApplication,
  putApplication,
  postChatOpen,
  getChatOpen,
  postChatMessage,
  delApplication,
  getApplicationDetail,
  getApplicationDataset,
  getAccessToken,
  putAccessToken,
  postAppAuthentication,
  getProfile,
  putChatVote,
  getApplicationHitTest,
  getApplicationModel
}
