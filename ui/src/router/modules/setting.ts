import { hasPermission } from '@/utils/permission/index'
import Layout from '@/layout/main-layout/index.vue'
import { Role } from '@/utils/permission/type'
const settingRouter = {
  path: '/setting',
  name: 'setting',
  meta: { icon: 'Setting', title: 'System settings', permission: 'SETTING:READ' },
  redirect: (to: any) => {
    if (hasPermission(new Role('ADMIN'), 'AND')) {
      return '/user'
    }
    return '/team'
  },
  component: Layout,
  children: [
    {
      path: '/user',
      name: 'user',
      meta: {
        icon: 'User',
        iconActive: 'UserFilled',
        title: 'User Management',
        activeMenu: '/setting',
        parentPath: '/setting',
        parentName: 'setting',
        permission: new Role('ADMIN')
      },
      component: () => import('@/views/user-manage/index.vue')
    },
    {
      path: '/team',
      name: 'team',
      meta: {
        icon: 'app-team',
        iconActive: 'app-team-active',
        title: 'Members of Team',
        activeMenu: '/setting',
        parentPath: '/setting',
        parentName: 'setting'
      },
      component: () => import('@/views/team/index.vue')
    },
    {
      path: '/template',
      name: 'template',
      meta: {
        icon: 'app-template',
        iconActive: 'app-template-active',
        title: 'Models set up',
        activeMenu: '/setting',
        parentPath: '/setting',
        parentName: 'setting'
      },
      component: () => import('@/views/template/index.vue')
    },
    {
      path: '/email',
      name: 'email',
      meta: {
        icon: 'Message',
        title: 'Postbox setup.',
        activeMenu: '/setting',
        parentPath: '/setting',
        parentName: 'setting',
        permission: new Role('ADMIN')
      },
      component: () => import('@/views/email/index.vue')
    }
  ]
}

export default settingRouter
