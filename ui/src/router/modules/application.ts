import Layout from '@/layout/main-layout/index.vue'
const applicationRouter = {
  path: '/application',
  name: 'application',
  meta: { title: 'Applications', permission: 'APPLICATION:READ' },
  redirect: '/application',
  children: [
    {
      path: '/application',
      name: 'application',
      component: () => import('@/views/application/index.vue')
    },
    {
      path: '/application/create',
      name: 'CreateApplication',
      meta: { activeMenu: '/application' },
      component: () => import('@/views/application/CreateAndSetting.vue'),
      hidden: true
    },
    {
      path: '/application/:id',
      name: 'ApplicationDetail',
      meta: { title: 'Application Details', activeMenu: '/application' },
      component: Layout,
      hidden: true,
      children: [
        {
          path: 'overview',
          name: 'AppOverview',
          meta: {
            icon: 'app-all-menu',
            iconActive: 'app-all-menu-active',
            title: 'Overview',
            active: 'overview',
            parentPath: '/application/:id',
            parentName: 'ApplicationDetail'
          },
          component: () => import('@/views/application-overview/index.vue')
        },
        {
          path: 'setting', 
          name: 'AppSetting',
          meta: {
            icon: 'app-setting',
            iconActive: 'app-setting-active',
            title: 'set up',
            active: 'setting',
            parentPath: '/application/:id',
            parentName: 'ApplicationDetail'
          },
          component: () => import('@/views/application/CreateAndSetting.vue')
        },
        {
          path: 'hit-test',
          name: 'AppHitTest',
          meta: {
            icon: 'app-hit-test',
            title: 'Test of fate.',
            active: 'hit-test',
            parentPath: '/application/:id',
            parentName: 'ApplicationDetail'
          },
          component: () => import('@/views/hit-test/index.vue')
        },
        {
          path: 'log',
          name: 'Log',
          meta: {
            icon: 'app-document',
            iconActive: 'app-document-active',
            title: 'Dialogues',
            active: 'log',
            parentPath: '/application/:id',
            parentName: 'ApplicationDetail'
          },
          component: () => import('@/views/log/index.vue')
        }
      ]
    },
  ]
}

export default applicationRouter
