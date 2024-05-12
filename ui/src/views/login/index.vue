<template>
  <login-layout v-loading="loading">
    <LoginContainer subTitle="Welcome to Use MaxKB Intelligent Knowledge Base">
      <h2 class="mb-24">Regular registration.</h2>
      <el-form
        class="login-form"
        :rules="rules"
        :model="loginForm"
        ref="loginFormRef"
        @keyup.enter="login"
      >
        <div class="mb-24">
          <el-form-item prop="username">
            <el-input
              size="large"
              class="input-item"
              v-model="loginForm.username"
              placeholder="Please enter the user name."
            >
            </el-input>
          </el-form-item>
        </div>
        <div class="mb-24">
          <el-form-item prop="password">
            <el-input
              type="password"
              size="large"
              class="input-item"
              v-model="loginForm.password"
              placeholder="Please enter the password."
              show-password
            >
            </el-input>
          </el-form-item>
        </div>
      </el-form>
      <el-button size="large" type="primary" class="w-full" @click="login">Registered</el-button>
      <div class="operate-container flex-between mt-12">
        <!-- <el-button class="register" @click="router.push('/register')" link type="primary">
          Registered
        </el-button> -->
        <el-button
          class="forgot-password"
          @click="router.push('/forgot_password')"
          link
          type="primary"
        >
          Forget the password.?
        </el-button>
      </div>
    </LoginContainer>
  </login-layout>
</template>
<script setup lang="ts">
import { ref } from 'vue'
import type { LoginRequest } from '@/api/type/user'
import { useRouter } from 'vue-router'
import type { FormInstance, FormRules } from 'element-plus'
import useStore from '@/stores'

const loading = ref<boolean>(false)
const { user } = useStore()
const router = useRouter()
const loginForm = ref<LoginRequest>({
  username: '',
  password: ''
})

const rules = ref<FormRules<LoginRequest>>({
  username: [
    {
      required: true,
      message: 'Please enter the user name.',
      trigger: 'blur'
    }
  ],
  password: [
    {
      required: true,
      message: 'Please enter the password.',
      trigger: 'blur'
    }
  ]
})
const loginFormRef = ref<FormInstance>()

const login = () => {
  loginFormRef.value?.validate().then(() => {
    loading.value = true
    user
      .login(loginForm.value.username, loginForm.value.password)
      .then(() => {
        router.push({ name: 'home' })
      })
      .finally(() => (loading.value = false))
  })
}
</script>
<style lang="scss" scope></style>
