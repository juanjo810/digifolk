
import { createRouter, createWebHashHistory } from 'vue-router'
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
            redirect: () => {
                return {name: 'userForm'}
            },
            children: [
                {
                     path: 'userForm',
                     name: 'userForm',
                     component: () => import('@/components/UserForm.vue'),

                },
                {
                    path: 'sheetForm',
                    name: 'sheetForm',
                    component: () => import('@/components/SheetForm.vue'),
                //    meta: {
                //        requiresAuth: true
                //    },
                },
                {
                    path: 'collectionForm',
                    name: 'collectionForm',
                    component: () => import('@/components/CollectionForm.vue'),
                //    meta: {
                //        requiresAuth: true
                //    },
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

// router.beforeEach((to, from , next) => {
//     // instead of having to check every route record with
//     // to.matched.some(record => record.meta.requiresAuth)
//     if (to.meta.requiresAuth && !store.state.user.loggedIn)
//     {
//         next({name:'login'})
//     }else{
//         if(!to.meta.requiresAuth && store.state.user.loggedIn){
//             next({name:'dashboard'})
//         }
//         next()
//     }
// })

