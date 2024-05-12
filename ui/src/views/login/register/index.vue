<template>
  <login-layout>
    <LoginContainer subTitle="Welcome to Use MaxKB Intelligent Knowledge Base">
      <h2 class="mb-24">User Registration</h2>
      <el-form class="register-form" :model="registerForm" :rules="rules" ref="registerFormRef">
        <div class="mb-24">
          <el-form-item prop="username">
            <el-input
              size="large"
              class="input-item"
              v-model="registerForm.username"
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
              v-model="registerForm.password"
              placeholder="Please enter the password."
              show-password
            >
            </el-input>
          </el-form-item>
        </div>
        <div class="mb-24">
          <el-form-item prop="re_password">
            <el-input
              type="password"
              size="large"
              class="input-item"
              v-model="registerForm.re_password"
              placeholder="Please enter the confirmation password."
              show-password
            >
            </el-input>
          </el-form-item>
        </div>
        <div class="mb-24">
          <el-form-item prop="email">
            <el-input
              size="large"
              class="input-item"
              v-model="registerForm.email"
              placeholder="Please enter the mailbox."
            >
            </el-input>
          </el-form-item>
        </div>
        <div class="mb-24">
          <el-form-item prop="code">
            <div class="flex-between w-full">
              <el-input
                size="large"
                class="code-input"
                v-model="registerForm.code"
                placeholder="Please enter the verification code."
              >
              </el-input>
              <el-button
                :disabled="isDisabled"
                size="large"
                class="send-email-button ml-12"
                @click="sendEmail"
                :loading="sendEmailLoading"
              >
                {{ isDisabled ? `re-send（${time}s）` : 'Get the verification code.' }}</el-button
              >
            </div>
          </el-form-item>
        </div>
      </el-form>
      <el-button size="large" type="primary" class="w-full" @click="register">Registered</el-button>
      <div class="operate-container mt-12">
        <el-button
          class="register"
          @click="router.push('/login')"
          link
          type="primary"
          icon="ArrowLeft"
        >
          Return to Registration.
        </el-button>
      </div>
    </LoginContainer>
  </login-layout>
</template>
<script setup lang="ts">
import { ref } from 'vue'
import type { RegisterRequest } from '@/api/type/user'
import { useRouter } from 'vue-router'
import UserApi from '@/api/user'
import { MsgSuccess } from '@/utils/message'
import type { FormInstance, FormRules } from 'element-plus'

const router = useRouter()
const registerForm = ref<RegisterRequest>({
  username: '',
  password: '',
  re_password: '',
  email: '',
  code: ''
})

const rules = ref<FormRules<RegisterRequest>>({
  username: [
    {
      required: true,
      message: 'Please enter the user name.',
      trigger: 'blur'
    },
    {
      min: 6,
      max: 20,
      message: 'The length is 6 to 20 A character.',
      trigger: 'blur'
    }
  ],
  password: [
    {
      required: true,
      message: 'Please enter the password.',
      trigger: 'blur'
    },
    {
      min: 6,
      max: 20,
      message: 'The length is 6 to 20 A character.',
      trigger: 'blur'
    }
  ],
  re_password: [
    {
      required: true,
      message: 'Please enter the confirmation password.',
      trigger: 'blur'
    },
    {
      min: 6,
      max: 20,
      message: 'The length is 6 to 20 A character.',
      trigger: 'blur'
    },
    {
      validator: (rule, value, callback) => {
        if (registerForm.value.password != registerForm.value.re_password) {
          callback(new Error('The code is incompatible.'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
  email: [
    { required: true, message: 'Please enter the mailbox.', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        const emailRegExp = /^[a-zA-Z0-9_.-]+@[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*\.[a-zA-Z0-9]{2,6}$/
        if (!emailRegExp.test(value) && value != '') {
          callback(new Error('Please enter the valid mailbox format.！'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
  code: [{ required: true, message: 'Please enter the verification code.' }]
})

const registerFormRef = ref<FormInstance>()
const register = () => {
  registerFormRef.value
    ?.validate()
    .then(() => {
      return UserApi.register(registerForm.value)
    })
    .then(() => {
      router.push('login')
    })
}
const sendEmailLoading = ref<boolean>(false)
const isDisabled = ref<boolean>(false)
const time = ref<number>(60)
/**
 * Send the verification code.
 */
const sendEmail = () => {
  registerFormRef.value?.validateField('email', (v: boolean) => {
    if (v) {
      UserApi.sendEmit(registerForm.value.email, 'register', sendEmailLoading).then(() => {
        MsgSuccess('Sending verification code successfully.')
        isDisabled.value = true
        handleTimeChange()
      })
    }
  })
}
const handleTimeChange = () => {
  if (time.value <= 0) {
    isDisabled.value = false
    time.value = 60
  } else {
    setTimeout(() => {
      time.value--
      handleTimeChange()
    }, 1000)
  }
}
</script>
<style lang="scss" scope></style>
