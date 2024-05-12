import { request } from './../request/index'
import { Result } from '@/request/Result'
import { get, post, del, put } from '@/request/index'
import { type Ref } from 'vue'
import type {
  modelRequest,
  Provider,
  ListModelRequest,
  Model,
  BaseModel,
  CreateModelRequest,
  EditModelRequest
} from '@/api/type/model'
import type { FormField } from '@/components/dynamics-form/type'
import type { KeyValue } from './type/common'
const prefix = '/model'
const prefix_provider = '/provider'

/**
 * Get a model list.
 * @params Parameters name, model_type, model_name
 */
const getModel: (
  request?: ListModelRequest,
  loading?: Ref<boolean>
) => Promise<Result<Array<Model>>> = (data, loading) => {
  return get(`${prefix}`, data, loading)
}

/**
 * Get a Supplier List
 */
const getProvider: (loading?: Ref<boolean>) => Promise<Result<Array<Provider>>> = (loading) => {
  return get(`${prefix_provider}`, {}, loading)
}

/**
 * Get a model to create a form
 * @param provider
 * @param model_type
 * @param model_name
 * @param loading
 * @returns
 */
const getModelCreateForm: (
  provider: string,
  model_type: string,
  model_name: string,
  loading?: Ref<boolean>
) => Promise<Result<Array<FormField>>> = (provider, model_type, model_name, loading) => {
  return get(`${prefix_provider}/model_form`, { provider, model_type, model_name }, loading)
}

/**
 * Get a Model Type List
 * @param provider Suppliers
 * @param loading  The carrier.
 * @returns List of Model Types
 */
const listModelType: (
  provider: string,
  loading?: Ref<boolean>
) => Promise<Result<Array<KeyValue<string, string>>>> = (provider, loading?: Ref<boolean>) => {
  return get(`${prefix_provider}/model_type_list`, { provider }, loading)
}

/**
 * Get a basic model list.
 * @param provider
 * @param model_type
 * @param loading
 * @returns
 */
const listBaseModel: (
  provider: string,
  model_type: string,
  loading?: Ref<boolean>
) => Promise<Result<Array<BaseModel>>> = (provider, model_type, loading) => {
  return get(`${prefix_provider}/model_list`, { provider, model_type }, loading)
}

/**
 * Creating a model.
 * @param request Requested objects
 * @param loading The carrier.
 * @returns
 */
const createModel: (
  request: CreateModelRequest,
  loading?: Ref<boolean>
) => Promise<Result<Model>> = (request, loading) => {
  return post(`${prefix}`, request, {}, loading)
}

/**
 * Modifying the model
 * @param request Requested Objects
 * @param loading The carrier.
 * @returns
 */
const updateModel: (
  model_id: string,
  request: EditModelRequest,
  loading?: Ref<boolean>
) => Promise<Result<Model>> = (model_id, request, loading) => {
  return put(`${prefix}/${model_id}`, request, {}, loading)
}

/**
 * Get the model details according to the modelid Including certification information
 * @param model_id The modelid
 * @param loading  The carrier.
 * @returns
 */
const getModelById: (model_id: string, loading?: Ref<boolean>) => Promise<Result<Model>> = (
  model_id,
  loading
) => {
  return get(`${prefix}/${model_id}`, {}, loading)
}
/**
 * Obtaining model information does not include certification information based on modelid
 * @param model_id The modelid
 * @param loading  The carrier.
 * @returns
 */
const getModelMetaById: (model_id: string, loading?: Ref<boolean>) => Promise<Result<Model>> = (
  model_id,
  loading
) => {
  return get(`${prefix}/${model_id}/meta`, {}, loading)
}

const deleteModel: (model_id: string, loading?: Ref<boolean>) => Promise<Result<boolean>> = (
  model_id,
  loading
) => {
  return del(`${prefix}/${model_id}`, undefined, {}, loading)
}
export default {
  getModel,
  getProvider,
  getModelCreateForm,
  listModelType,
  listBaseModel,
  createModel,
  updateModel,
  deleteModel,
  getModelById,
  getModelMetaById
}
