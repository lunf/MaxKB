import { store } from '@/stores'
import type { Dict } from './common'
interface modelRequest {
  name: string
  model_type: string
  model_name: string
}

interface Provider {
  /**
   * Code of Supplier
   */
  provider: string
  /**
   * Name of Supplier
   */
  name: string
  /**
   * Suppliersicon
   */
  icon: string
}

interface ListModelRequest {
  /**
   * Name of model
   */
  name?: string
  /**
   * Type of Model
   */
  model_type?: string
  /**
   * The basic model name.
   */
  model_name?: string
  /**
   * Suppliers
   */
  provider?: string
}

interface Model {
  /**
   * The key.id
   */
  id: string
  /**
   * The model name
   */
  name: string
  /**
   * Type of Model
   */
  model_type: string
  /**
   * The Basic Model
   */
  model_name: string
  /**
   * Certification Information
   */
  credential: any
  /**
   * Suppliers
   */
  provider: string
  /**
   * state of
   */
  status: 'SUCCESS' | 'DOWNLOAD' | 'ERROR'
  /**
   * The data
   */
  meta: Dict<any>
}
interface CreateModelRequest {
  /**
   * The model name
   */
  name: string
  /**
   * Type of Model
   */
  model_type: string
  /**
   * The Basic Model
   */
  model_name: string
  /**
   * Certification Information
   */
  credential: any
  /**
   * Suppliers
   */
  provider: string
}

interface EditModelRequest {
  /**
   * The model name
   */
  name: string
  /**
   * Type of Model
   */
  model_type: string
  /**
   * The Basic Model
   */
  model_name: string
  /**
   * Certification Information
   */
  credential: any
}

interface BaseModel {
  /**
   * The basic model name.
   */
  name: string
  /**
   * Basic Model Description
   */
  desc: string
  /**
   * Type of Basic Model
   */
  model_type: string
}
export type {
  modelRequest,
  Provider,
  ListModelRequest,
  Model,
  BaseModel,
  CreateModelRequest,
  EditModelRequest
}
