/**
 * The role objects
 */
export class Role {
  role: string

  constructor(role: string) {
    this.role = role
  }
}
/**
 * Authority Objects
 */
export class Permission {
  permission: string

  constructor(permission: string) {
    this.permission = permission
  }
}
/**
 * Complex authority objects
 */
export class ComplexPermission {
  roleList: Array<string>

  permissionList: Array<string>

  compare: 'OR' | 'AND'

  constructor(roleList: Array<string>, permissionList: Array<string>, compare: 'OR' | 'AND') {
    this.roleList = roleList
    this.permissionList = permissionList
    this.compare = compare
  }
}
