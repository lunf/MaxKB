interface User {
  /**
   * Usersid
   */
  id: string
  /**
   * User Name
   */
  username: string
  /**
   * The mailbox
   */
  email: string
  /**
   * User role
   */
  role: string
  /**
   * User permits
   */
  permissions: Array<string>
  /**
   * Is it necessary to modify the password?
   */
  is_edit_password?: boolean
}

interface LoginRequest {
  /**
   * User Name
   */
  username: string
  /**
   * The code
   */
  password: string
}

interface RegisterRequest {
  /**
   * User Name
   */
  username: string
  /**
   * The code
   */
  password: string
  /**
   * Identify the password.
   */
  re_password: string
  /**
   * The mailbox
   */
  email: string
  /**
   * verification code
   */
  code: string
}

interface CheckCodeRequest {
  /**
   * The mailbox
   */
  email: string
  /**
   *verification code
   */
  code: string
  /**
   * Type of
   */
  type: 'register' | 'reset_password'
}

interface ResetCurrentUserPasswordRequest {
  /**
   * verification code
   */
  code: string
  /**
   *The code
   */
  password: string
  /**
   * Confirm the password.
   */
  re_password: string
}

interface ResetPasswordRequest {
  /**
   * The mailbox
   */
  email?: string
  /**
   * verification code
   */
  code?: string
  /**
   * The code
   */
  password: string
  /**
   * Confirm the password.
   */
  re_password: string
}

export type {
  LoginRequest,
  RegisterRequest,
  CheckCodeRequest,
  ResetPasswordRequest,
  User,
  ResetCurrentUserPasswordRequest
}
