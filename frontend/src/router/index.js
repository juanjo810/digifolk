
import { createRouter, createWebHashHistory } from 'vue-router'
import store from '@/store'
import Login from '@/views/AppLogin.vue'
import Dashboard from '@/views/AppDashboard.vue'
import Register from '@/views/AppRegister.vue'
import utils from '@/utils/utils.js'


const router = createRouter({
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('@/views/AppHome.vue'),
    },
    {
      path: '/contact',
      name: 'contact',
      component: () => import('@/views/AppContact.vue'),
    },
    {
      path: '/login',
      name: 'login',
      component: Login,
      meta: {
        requiresAuth: false
      }
    },
    {
      path: '/register',
      name: 'register',
      component: Register
    },
    {
      path: '/forgotPassword',
      name: 'forgotPassword',
      component: () => import('@/views/ForgotPass.vue'),
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: Dashboard,
      meta: {
        requiresAuth: true
      },
      redirect: () => {
        return { name: 'listPieces' }
      },
      children: [
        {
          path: 'pieces',
          name: 'pieces',
          children: [
            {
              path: 'listPieces',
              name: 'listPieces',
              component: () => import('@/views/AppListPieces.vue'),
              meta: {
                requiresAuth: true
              }
            },
            {
              path: 'viewPiece',
              name: 'viewPiece',
              component: () => import('@/views/ViewPiece.vue'),
              props: route => ({ piece: route.params.piece }),
              meta: {
                requiresAuth: true
              }
            },
            {
              path: 'sheetpiece',
              name: 'sheetpiece',
              component: () => import('@/views/SheetPiece.vue'),
              meta: {
                requiresAuth: true
              }
            },
            {
              path: 'uploadPiece',
              name: 'uploadPiece',
              component: () => import('@/views/UploadPiece.vue'),
              meta: {
                requiresAuth: true
              },
              children: [
                {
                  path: 'userForm',
                  name: 'userForm',
                  component: () => import('@/views/UserForm.vue'),
                  meta: {
                    requiresAuth: true
                  },

                },
                {
                  path: 'sheetForm',
                  name: 'sheetForm',
                  component: () => import('@/views/SheetForm.vue'),
                  meta: {
                    requiresAuth: true
                  },
                },
              ],
              redirect: () => {
                return { name: 'userForm' }
              },
            },

          ]
        },
        {
          path: 'collections',
          name: 'collections',
          children: [
            {
              path: 'listCollections',
              name: 'listCollections',
              component: () => import('@/views/AppListCollections.vue'),
              meta: {
                requiresAuth: true
              }
            },
            {
              path: 'viewCollection',
              name: 'viewCollection',
              component: () => import('@/views/ViewCollection.vue'),
              meta: {
                requiresAuth: true
              }
            },
            {
              path: 'collectionForm',
              name: 'collectionForm',
              component: () => import('@/views/CollectionForm.vue'),
              meta: {
                requiresAuth: true
              },

            },
          ]

        },
        {
          path: 'modifyItems',
          name: 'modifyItems',
          component: () => import('@/views/ModifyItems.vue'),
          meta: {
            requiresAuth: true,
            requiresAdmin: true
          },
        },
        {
          path: 'users',
          name: 'users',
          component: () => import('@/views/UsersList.vue'),
          meta: {
            requiresAuth: true,
            requiresAdmin: true
          },
        },
        {
          path: 'profile',
          name: 'profile',
          component: () => import('@/views/MyProfile.vue'),
          meta: {
            requiresAuth: true
          },
        },
        {
          path: 'reviews',
          name: 'reviews',
          component: () => import('@/views/ReviewPiece.vue'),
          meta: {
            requiresAuth: true,
            requiresAdmin: true
          },
        },

      ]
    },
  ],
  history: createWebHashHistory()
})

export default router

router.beforeEach((to, from, next) => {
  // instead of having to check every route record with
  // to.matched.some(record => record.meta.requiresAuth)
  if (to.meta.requiresAuth) {
    utils.authenticated(store.state.user.tokenSession)
      .then((authenticated) => {
        if (!authenticated) {
          next({ name: 'login' })
        } else if (to.meta.requiresAdmin && !store.state.user.userInfo.is_admin) {
          next({ name: 'dashboard' })
        } else {
          store.commit('REFRESH_TOKEN_SESSION', authenticated.access_token)
          next()
        }
      })
  } else {
    if (store.state.user.tokenSession) {
      utils.authenticated(store.state.user.tokenSession)
        .then((authenticated) => {
          if (authenticated){
           store.commit('REFRESH_TOKEN_SESSION', authenticated.access_token)
            next({ name: 'dashboard' })
          }else
            store.commit('REMOVE_TOKEN_SESSION')
          next()
        })
    } else {
      next()
    }
  }
})

