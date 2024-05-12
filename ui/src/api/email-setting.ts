import { Result } from '@/request/Result'
import { get, post, del, put } from '@/request/index'
import type { pageRequest } from '@/api/type/common'
import { type Ref } from 'vue'

const prefix = '/email_setting'
/**
 * Get the mailbox setting.
 */
const getEmailSetting: (loading?: Ref<boolean>) => Promise<Result<any>> = (loading) => {
  return get(`${prefix}`, undefined, loading)
}

/**
 * The mailbox test.
 */
const postTestEmail: (data: any, loading?: Ref<boolean>) => Promise<Result<any>> = (
  data,
  loading
) => {
  return post(`${prefix}`, data, undefined, loading)
}

/**
 * Change the mailbox setting.
 */
const putEmailSetting: (data: any, loading?: Ref<boolean>) => Promise<Result<any>> = (
  data,
  loading
) => {
  return put(`${prefix}`, data, undefined, loading)
}

export default {
  getEmailSetting,
  postTestEmail,
  putEmailSetting
}
