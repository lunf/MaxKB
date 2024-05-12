import axios, { type AxiosRequestConfig } from 'axios'
import { MsgError } from '@/utils/message'
import type { NProgress } from 'nprogress'
import type { Ref } from 'vue'
import type { Result } from '@/request/Result'
import useStore from '@/stores'
import router from '@/router'

import { ref, type WritableComputedRef } from 'vue'

const axiosConfig = {
  baseURL: '/api',
  withCredentials: false,
  timeout: 60000,
  headers: {}
}

const instance = axios.create(axiosConfig)

/* Set the request block. */
instance.interceptors.request.use(
  (config: AxiosRequestConfig) => {
    if (config.headers === undefined) {
      config.headers = {}
    }
    const { user } = useStore()
    const token = user.getToken()
    if (token) {
      config.headers['AUTHORIZATION'] = `${token}`
    }
    return config
  },
  (err: any) => {
    return Promise.reject(err)
  }
)

//Set up the response block.
instance.interceptors.response.use(
  (response: any) => {
    if (response.data) {
      if (response.data.code !== 200 && !(response.data instanceof Blob)) {
        MsgError(response.data.message)
        return Promise.reject(response.data)
      }
    }
    return response
  },
  (err: any) => {
    if (err.code === 'ECONNABORTED') {
      MsgError(err.message)
      console.error(err)
    }
    if (err.response?.status === 404) {
      if (!err.response.config.url.includes('/application/authentication')) {
        router.push('/404 ')
      }
    }
    if (err.response?.status === 401) {
      if (
        !err.response.config.url.includes('chat/open') &&
        !err.response.config.url.includes('application/profile')
      ) {
        router.push({ name: 'login' })
      }
    }

    if (err.response?.status === 403 && !err.response.config.url.includes('chat/open')) {
      MsgError(
        err.response.data && err.response.data.message ? err.response.data.message : 'No access permission.'
      )
    }
    return Promise.reject(err)
  }
)

export const request = instance

/* Simplified Application Method，Unified processing of return results，and increaseloadingProcessed，here to{success,data,message}The return value of the format is an example.，Modified projects according to actual needs */
const promise: (
  request: Promise<any>,
  loading?: NProgress | Ref<boolean> | WritableComputedRef<boolean>
) => Promise<Result<any>> = (request, loading = ref(false)) => {
  return new Promise((resolve, reject) => {
    if ((loading as NProgress).start) {
      ;(loading as NProgress).start()
    } else {
      ;(loading as Ref).value = true
    }
    request
      .then((response) => {
        // blobThe type of return isresponse.status
        if (response.status === 200) {
          resolve(response?.data || response)
        } else {
          reject(response?.data || response)
        }
      })
      .catch((error) => {
        reject(error)
      })
      .finally(() => {
        if ((loading as NProgress).start) {
          ;(loading as NProgress).done()
        } else {
          ;(loading as Ref).value = false
        }
      })
  })
}

/**
 * Sendinggetrequested   Generally used to request resources.
 * @param url    Resourcesurl
 * @param params Parameters
 * @param loading loading
 * @returns The ExoduspromiseObjects
 */
export const get: (
  url: string,
  params?: unknown,
  loading?: NProgress | Ref<boolean>,
  timeout?: number
) => Promise<Result<any>> = (
  url: string,
  params: unknown,
  loading?: NProgress | Ref<boolean>,
  timeout?: number
) => {
  return promise(request({ url: url, method: 'get', params, timeout: timeout }), loading)
}

/**
 * faso postrequested Generally used to add resources.
 * @param url    Resourcesurl
 * @param params Parameters
 * @param data   Adding data
 * @param loading loading
 * @returns The ExoduspromiseObjects
 */
export const post: (
  url: string,
  data?: unknown,
  params?: unknown,
  loading?: NProgress | Ref<boolean>,
  timeout?: number
) => Promise<Result<any> | any> = (url, data, params, loading, timeout) => {
  return promise(request({ url: url, method: 'post', data, params, timeout }), loading)
}

/**|
 * Sendingputrequested Modification of server resources.
 * @param url     Resource Address
 * @param params  paramsAddress of Parameters
 * @param data    Data needed to be modified.
 * @param loading The Progress
 * @returns
 */
export const put: (
  url: string,
  data?: unknown,
  params?: unknown,
  loading?: NProgress | Ref<boolean>,
  timeout?: number
) => Promise<Result<any>> = (url, data, params, loading, timeout) => {
  return promise(request({ url: url, method: 'put', data, params, timeout }), loading)
}

/**
 * removed
 * @param url     removedurl
 * @param params  paramsParameters
 * @param loading The Progress
 * @returns
 */
export const del: (
  url: string,
  params?: unknown,
  data?: unknown,
  loading?: NProgress | Ref<boolean>,
  timeout?: number
) => Promise<Result<any>> = (url, params, data, loading, timeout) => {
  return promise(request({ url: url, method: 'delete', params, data, timeout }), loading)
}

/**
 * flow processing
 * @param url  urlAddressed
 * @param data requestedbody
 * @returns
 */
export const postStream: (url: string, data?: unknown) => Promise<Result<any> | any> = (
  url,
  data
) => {
  const { user } = useStore()
  const token = user.getToken()
  const headers: HeadersInit = { 'Content-Type': 'application/json' }
  if (token) {
    headers['AUTHORIZATION'] = `${token}`
  }
  return fetch(url, {
    method: 'POST',
    body: data ? JSON.stringify(data) : undefined,
    headers: headers
  })
}

export const exportExcel: (
  fileName: string,
  url: string,
  params: any,
  loading?: NProgress | Ref<boolean>
) => void = (fileName: string, url: string, params: any, loading?: NProgress | Ref<boolean>) => {
  promise(request({ url: url, method: 'get', params, responseType: 'blob' }), loading)
    .then((res: any) => {
      if (res) {
        const blob = new Blob([res], {
          type: 'application/vnd.ms-excel'
        })
        const link = document.createElement('a')
        link.href = window.URL.createObjectURL(blob)
        link.download = fileName
        link.click()
        //Release the memory.
        window.URL.revokeObjectURL(link.href)
      }
    })
    .catch((e) => {})
}

/**
 * Created with the server.wslinked
 * @param url websocketThe path
 * @returns  Return to one.websocketExamples
 */
export const socket = (url: string) => {
  let protocol = 'ws://'
  if (window.location.protocol === 'https:') {
    protocol = 'wss://'
  }
  let uri = protocol + window.location.host + url
  if (!import.meta.env.DEV) {
    uri = protocol + window.location.host + import.meta.env.VITE_BASE_PATH + url
  }
  return new WebSocket(uri)
}
export default instance
