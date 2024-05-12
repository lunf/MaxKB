import Layout from '@/layout/main-layout/index.vue'
const datasetRouter = {
  path: '/dataset',
  name: 'dataset',
  meta: { title: 'The knowledge base', permission: 'DATASET:READ' },
  redirect: '/dataset',
  children: [
    {
      path: '/dataset',
      name: 'dataset',
      component: () => import('@/views/dataset/index.vue')
    },
    {
      path: '/dataset/:type', // create or upload
      name: 'CreateDataset',
      meta: { activeMenu: '/dataset' },
      component: () => import('@/views/dataset/CreateDataset.vue'),
      hidden: true
    },
    {
      path: '/dataset/:id',
      name: 'DatasetDetail',
      meta: { title: 'Documents', activeMenu: '/dataset' },
      component: Layout,
      hidden: true,
      children: [
        {
          path: 'document',
          name: 'Document',
          meta: {
            icon: 'app-document',
            iconActive: 'app-document-active',
            title: 'Documents',
            active: 'document',
            parentPath: '/dataset/:id',
            parentName: 'DatasetDetail'
          },
          component: () => import('@/views/document/index.vue')
        },
        {
          path: 'problem',
          name: 'Problem',
          meta: {
            icon: 'app-problems',
            title: 'The problem',
            active: 'problem',
            parentPath: '/dataset/:id',
            parentName: 'DatasetDetail'
          },
          component: () => import('@/views/problem/index.vue')
        },
        {
          path: 'hit-test',
          name: 'DatasetHitTest',
          meta: {
            icon: 'app-hit-test',
            title: 'Test of fate.',
            active: 'hit-test',
            parentPath: '/dataset/:id',
            parentName: 'DatasetDetail'
          },
          component: () => import('@/views/hit-test/index.vue')
        },
        {
          path: 'setting',
          name: 'DatasetSetting',
          meta: {
            icon: 'app-setting',
            iconActive: 'app-setting-active',
            title: 'set up',
            active: 'setting',
            parentPath: '/dataset/:id',
            parentName: 'DatasetDetail'
          },
          component: () => import('@/views/dataset/DatasetSetting.vue')
        }
      ]
    },
    {
      path: '/dataset/:id/:documentId', // Section Details
      name: 'Paragraph',
      meta: { activeMenu: '/dataset' },
      component: () => import('@/views/paragraph/index.vue'),
      hidden: true
    }
  ]
}

export default datasetRouter
