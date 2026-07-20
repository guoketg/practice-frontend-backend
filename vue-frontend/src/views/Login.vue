<template>
  <div class="form-page">
    <h2>员工登录</h2>
    <form @submit.prevent="handleLogin">
      <label>员工 ID</label>
      <input v-model='form.emp_id' type="number" required />

      <label>密码</label>
      <input v-model="form.password" type="password" required />

      <button type="submit" :disabled="loading">
        {{ loading?'登录中':'登录' }}
      </button>




    </form>


  </div>
</template>

<script setup>
import { reactive,ref} from 'vue'
import {useRouter} from 'vue-router'
import  {login} from '../api'

const router=useRouter()
const form=reactive({emp_id:'',password:''})
const loading =ref(false)
const error =ref('')

async function handleLogin(){
  loading.value=true
  error.value=''

  const res=await login({
    emp_id:Number(form.emp_id),
    password:form.password
  })



} 
</script>