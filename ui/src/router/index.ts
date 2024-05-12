import { hasPermission } from '@/utils/permission/index'
import {
  createRouter,
  createWebHistory,
  type NavigationGuardNext,
  type RouteLocationNormalized,
  type RouteRecordRaw,
  type RouteRecordName
} from 'vue-router'
import useStore from '@/stores'
import { routes } from '@/router/routes'
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: routes
})

// The routing front blocker.
router.beforeEach(
  async (to: RouteLocationNormalized, from: RouteLocationNormalized, next: NavigationGuardNext) => {
    if (to.name === '404') {
      next()
      return
    }
    const { user } = useStore()
    const notAuthRouteNameList = ['register', 'login', 'forgot_password', 'reset_password', 'Chat']

    if (!notAuthRouteNameList.includes(to.name ? to.name.toString() : '')) {
      const token = user.getToken()
      if (!token) {
        next({
          path: '/login'
        })
        return
      }
      if (!user.userInfo) {
        await user.profile()
      }
    }
    // To determine whether the menu is authorized.
    if (to.meta.permission ? hasPermission(to.meta.permission as any, 'OR') : true) {
      next()
    } else {
      // If there is no authorization, take it directly.404page
      next('404')
    }
  }
)

export const getChildRouteListByPathAndName = (path: any, name?: RouteRecordName | any) => {
  return getChildRouteList(routes, path, name)
}

export const getChildRouteList: (
  routeList: Array<RouteRecordRaw>,
  path: string,
  name?: RouteRecordName | null | undefined
) => Array<RouteRecordRaw> = (routeList, path, name) => {
  for (let index = 0; index < routeList.length; index++) {
    const route = routeList[index]
    if (name === route.name && path === route.path) {
      return route.children || []
    }
    if (route.children && route.children.length > 0) {
      const result = getChildRouteList(route.children, path, name)
      if (result && result?.length > 0) {
        return result
      }
    }
  }
  return []
}

export default router
