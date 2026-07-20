import { createApp } from 'vue'
import {createRouter,createWebHistory} from 'vue-router'
import './style.css'
import App from './App.vue'
import Login from './views/Login.vue'
import Register from './views/Register.vue'
import Employee from './views/Employee.vue'

const routes=[
    {path:'/',redirect:'/login'},
    {path:'/login',name:'Login',component:Login},
    {path:'/register',name:'Register',component:Register},
    {path:'/employees',name:'Employees',component:Employee}
]

const router=createRouter({
    history:createWebHistory(),
    routes
})

const app=createApp(App)
app.use(router)
app.mount('#app')

