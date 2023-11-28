<template>
  <login-layout>
    <LoginContainer>
      <h4 class="mb-16">修改密码</h4>
      <el-form
        class="reset-password-form"
        ref="resetPasswordFormRef"
        :model="resetPasswordForm"
        :rules="rules"
      >
        <el-form-item prop="password">
          <el-input
            type="password"
            size="large"
            class="input-item"
            v-model="resetPasswordForm.password"
            placeholder="请输入密码"
            show-password
          >
            <template #prepend>
              <el-button icon="Lock" />
            </template>
          </el-input>
        </el-form-item>
        <el-form-item prop="re_password">
          <el-input
            type="password"
            size="large"
            class="input-item"
            v-model="resetPasswordForm.re_password"
            placeholder="请输入确认密码"
            show-password
          >
            <template #prepend>
              <el-button icon="Lock" />
            </template>
          </el-input>
        </el-form-item>
      </el-form>
      <el-button type="primary" class="login-submit-button w-full" @click="resetPassword"
        >确认修改</el-button
      >
      <div class="operate-container mt-8">
        <el-button
          class="register"
          @click="router.push('/login')"
          link
          type="primary"
          icon="DArrowLeft"
        >
          返回登录
        </el-button>
      </div>
    </LoginContainer>
  </login-layout>
</template>
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { ResetPasswordRequest } from '@/api/type/user'
import { useRouter, useRoute } from 'vue-router'
import { MsgSuccess } from '@/utils/message'
import type { FormInstance, FormRules } from 'element-plus'
import UserApi from '@/api/user'
const router = useRouter()
const route = useRoute()
const {
  params: { code, email }
} = route
const resetPasswordForm = ref<ResetPasswordRequest>({
  password: '',
  re_password: '',
  email: '',
  code: ''
})

onMounted(() => {
  if (code && email) {
    resetPasswordForm.value.code = code as string
    resetPasswordForm.value.email = email as string
  } else {
    router.push('forgot_password')
  }
})

const rules = ref<FormRules<ResetPasswordRequest>>({
  password: [
    {
      required: true,
      message: '请输入密码',
      trigger: 'blur'
    },
    {
      min: 6,
      max: 30,
      message: '长度在 6 到 30 个字符',
      trigger: 'blur'
    }
  ],
  re_password: [
    {
      required: true,
      message: '请输入确认密码',
      trigger: 'blur'
    },
    {
      min: 6,
      max: 30,
      message: '长度在 6 到 30 个字符',
      trigger: 'blur'
    },
    {
      validator: (rule, value, callback) => {
        if (resetPasswordForm.value.password != resetPasswordForm.value.re_password) {
          callback(new Error('密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
})
const resetPasswordFormRef = ref<FormInstance>()
const loading = ref<boolean>(false)
const resetPassword = () => {
  resetPasswordFormRef.value
    ?.validate()
    .then(() => UserApi.resetPassword(resetPasswordForm.value, loading))
    .then(() => {
      MsgSuccess('修改密码成功')
      router.push({ name: 'login' })
    })
}
</script>
<style lang="scss" scope>
@import '../index.scss';
</style>