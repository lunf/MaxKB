<template>
  <login-layout>
    <LoginContainer subTitle="Welcome to Use MaxKB Intelligent Knowledge Base">
      <h2 class="mb-24">Forget the password.</h2>
      <el-form
        class="register-form"
        ref="resetPasswordFormRef"
        :model="CheckEmailForm"
        :rules="rules"
      >
        <div class="mb-24">
          <el-form-item prop="email">
            <el-input
              size="large"
              class="input-item"
              v-model="CheckEmailForm.email"
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
                v-model="CheckEmailForm.code"
                placeholder="Please enter the verification code."
              >
              </el-input>

              <el-button
                :disabled="isDisabled"
                size="large"
                class="send-email-button ml-12"
                @click="sendEmail"
                :loading="loading"
              >
                {{ isDisabled ? `re-send（${time}s）` : 'Get the verification code.' }}</el-button
              >
            </div>
          </el-form-item>
        </div>
      </el-form>
      <el-button size="large" type="primary" class="w-full" @click="checkCode">Verify immediately.</el-button>
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
import type { CheckCodeRequest } from '@/api/type/user'
import { useRouter } from 'vue-router'
import type { FormInstance, FormRules } from 'element-plus'
import UserApi from '@/api/user'
import { MsgSuccess } from '@/utils/message'

const router = useRouter()
const CheckEmailForm = ref<CheckCodeRequest>({
  email: '',
  code: '',
  type: 'reset_password'
})

const resetPasswordFormRef = ref<FormInstance>()
const rules = ref<FormRules<CheckCodeRequest>>({
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
const loading = ref<boolean>(false)
const isDisabled = ref<boolean>(false)
const time = ref<number>(60)

const checkCode = () => {
  resetPasswordFormRef.value
    ?.validate()
    .then(() => UserApi.checkCode(CheckEmailForm.value, loading))
    .then(() => router.push({ name: 'reset_password', params: CheckEmailForm.value }))
}
/**
 * Send the verification code.
 */
const sendEmail = () => {
  resetPasswordFormRef.value?.validateField('email', (v: boolean) => {
    if (v) {
      UserApi.sendEmit(CheckEmailForm.value.email, 'reset_password', loading).then(() => {
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
