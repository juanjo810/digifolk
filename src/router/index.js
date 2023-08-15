
import { createRouter, createWebHashHistory } from 'vue-router'
import store from '@/store'
import Login from '@/views/AppLogin.vue'
import Dashboard from '@/views/AppDashboard.vue'
import Register from '@/views/AppRegister.vue'


const router =  createRouter({
    routes: [
        {
            path: '/',
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
            path: '/dashboard',
            name: 'dashboard',
            component: Dashboard,
            meta: {
                requiresAuth: true
            },
            redirect: () => {
                return {name: 'viewPiece'}
            },
            children: [
                {
                    path:'pieces',
                    name:'pieces',
                    children: [
                      {
                        path: 'viewPiece',
                        name: 'viewPiece',
                        component: () => import('@/views/ViewPiece.vue'),
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
                            return {name: 'userForm'}
                        },
                      },
                      
                    ]
                },
                {
                  path:'collections',
                  name:'collections',
                  children: [
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
                        requiresAuth: true
                    },
                },
                // {
                //     path: 'reports',
                //     name: 'reports',
                //     component: () => import ('@/components/view2/Reports.vue'),
                //     meta: {
                //         requiresAuth: true
                //     },
                
            ]
        },
        // {
        //     path: '/image/:id',
        //     name: 'image',
        //     component: MfImage,
        //     props: true,
        //     meta: {
        //         requiresAuth: true
        //     },
        // },
        // {
        //     path: '/post/:id',
        //     name: 'post',
        //     component: () => import('@/components/MfPostsUser.vue'),
        //     props: true,
        //     meta: {
        //         requiresAuth: true
        //     },
        // },
        // {
        //     path: '/:id/comments',
        //     name: 'comments',
        //     component: () => import('@/components/view2/Comentarios.vue'),
        //     props: true,
        //     meta: {
        //         requiresAuth: true
        //     },
        // },
        // {
        //     path: '/report/:id',
        //     name: 'report',
        //     component: () => import('@/components/view2/Report.vue'),
        //     props: true,
        //     meta: {
        //         requiresAuth: true
        //     },
        // },
        // {
        //     path: '/otroPerfil/:id',
        //     name: 'otroPerfil',
        //     component: MfOtroPerfil,
        //     props: true,
        //     meta: {
        //         requiresAuth: true
        //     },
        // },
        // {
        //     path: '/demo',
        //     name: 'demo',
        //     component: MfDemo,
        //     meta: {
        //         requiresAuth: false
        //     }
        // }
    ],
    history: createWebHashHistory()
})

export default router

router.beforeEach((to, from , next) => {
    // instead of having to check every route record with
    // to.matched.some(record => record.meta.requiresAuth)
    if (to.meta.requiresAuth && store.state.user.tokenSession === '')
    {
        next({name:'login'})
    }else{
        if(!to.meta.requiresAuth && store.state.user.tokenSession !== ''){
            next({name:'dashboard'})
        } else {
            next()
        }
    }
})

