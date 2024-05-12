import { Result } from '@/request/Result'
import { get, post } from '@/request/index'
import type {
  LoginRequest,
  RegisterRequest,
  CheckCodeRequest,
  ResetPasswordRequest,
  User,
  ResetCurrentUserPasswordRequest
} from '@/api/type/user'
import type { Ref } from 'vue'

/**
 * Registered
 * @param request Entry interface request form
 * @param loading Interface carrier
 * @returns Certified data
 */
const login: (request: LoginRequest, loading?: Ref<boolean>) => Promise<Result<string>> = (
  request,
  loading
) => {
  return post('/user/login', request, undefined, loading)
}
/**
 * ascending
 * @param loading Interface carrier
 * @returns
 */
const logout: (loading?: Ref<boolean>) => Promise<Result<boolean>> = (loading) => {
  return post('/user/logout', undefined, undefined, loading)
}

/**
 * Registered User
 * @param request Subjects of registration request
 * @param loading Interface carrier
 * @returns
 */
const register: (request: RegisterRequest, loading?: Ref<boolean>) => Promise<Result<string>> = (
  request,
  loading
) => {
  return post('/user/register', request, undefined, loading)
}

/**
 * School verification code.
 * @param request Requested objects
 * @param loading Interface carrier
 * @returns
 */
const checkCode: (request: CheckCodeRequest, loading?: Ref<boolean>) => Promise<Result<boolean>> = (
  request,
  loading
) => {
  return post('/user/check_code', request, undefined, loading)
}

/**
 * sending the mail.
 * @param email  The mail address
 * @param loading Interface carrier
 * @returns
 */
const sendEmit: (
  email: string,
  type: 'register' | 'reset_password',
  loading?: Ref<boolean>
) => Promise<Result<boolean>> = (email, type, loading) => {
  return post('/user/send_email', { email, type }, undefined, loading)
}
/**
 * Send email to current users.
 * @param loading  Send the verification code to the current user
 * @returns
 */
const sendEmailToCurrent: (loading?: Ref<boolean>) => Promise<Result<boolean>> = (loading) => {
  return post('/user/current/send_email', undefined, undefined, loading)
}
/**
 * Modify the current user password.
 * @param request Requested objects
 * @param loading The carrier.
 * @returns
 */
const resetCurrentUserPassword: (
  request: ResetCurrentUserPasswordRequest,
  loading?: Ref<boolean>
) => Promise<Result<boolean>> = (request, loading) => {
  return post('/user/current/reset_password', request, undefined, loading)
}
/**
 * Obtaining User Basic Information
 * @param loading Interface carrier
 * @returns User Basic Information
 */
const profile: (loading?: Ref<boolean>) => Promise<Result<User>> = (loading) => {
  return get('/user', undefined, loading)
}

/**
 * Repeat the password.
 * @param request Reset the password request parameters.
 * @param loading Interface carrier
 * @returns
 */
const resetPassword: (
  request: ResetPasswordRequest,
  loading?: Ref<boolean>
) => Promise<Result<boolean>> = (request, loading) => {
  return post('/user/re_password', request, undefined, loading)
}

/**
 * Adding teams need to consult the user list
 * @param loading Interface carrier
 * email_or_username
 */
const getUserList: (email_or_username: string, loading?: Ref<boolean>) => Promise<Result<any>> = (
  email_or_username,
  loading
) => {
  return get('/user/list', { email_or_username }, loading)
}

/**
 * obtainedversion
 */
const getVersion: (loading?: Ref<boolean>) => Promise<Result<any>> = (loading) => {
  return get('/profile', undefined, loading)
}

export default {
  login,
  register,
  sendEmit,
  checkCode,
  profile,
  resetPassword,
  sendEmailToCurrent,
  resetCurrentUserPassword,
  logout,
  getUserList,
  getVersion
}
