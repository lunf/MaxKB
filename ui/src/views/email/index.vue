<template>
  <LayoutContainer header="Postbox setup.">
    <div class="email-setting main-calc-height">
      <el-scrollbar>
        <div class="p-24" v-loading="loading">
          <el-form
            ref="emailFormRef"
            :rules="rules"
            :model="form"
            label-position="top"
            require-asterisk-position="right"
          >
            <el-form-item label="SMTP The host" prop="email_host">
              <el-input v-model="form.email_host" placeholder="Please enter. SMTP The host" />
            </el-form-item>
            <el-form-item label="SMTP The port." prop="email_port">
              <el-input v-model="form.email_port" placeholder="Please enter. SMTP The port." />
            </el-form-item>
            <el-form-item label="SMTP The account" prop="email_host_user">
              <el-input v-model="form.email_host_user" placeholder="Please enter. SMTP The account" />
            </el-form-item>
            <el-form-item label="The mailbox of the sender" prop="from_email">
              <el-input v-model="form.from_email" placeholder="Please enter the sender’s mailbox." />
            </el-form-item>
            <el-form-item label="The code" prop="email_host_password">
              <el-input
                v-model="form.email_host_password"
                placeholder="Please enter the sender’s password."
                show-password
              />
            </el-form-item>
            <el-form-item>
              <el-checkbox v-model="form.email_use_ssl"
                >openedSSL(IfSMTPThe port is465，It usually needs to be activated.SSL)
              </el-checkbox>
            </el-form-item>
            <el-form-item>
              <el-checkbox v-model="form.email_use_tls"
                >openedTLS(IfSMTPThe port is587，It usually needs to be activated.TLS)</el-checkbox
              >
            </el-form-item>
            <el-button @click="submit(emailFormRef, 'test')" :disabled="loading">
              Testing connection.
            </el-button>
          </el-form>

          <div class="text-right">
            <el-button @click="submit(emailFormRef)" type="primary" :disabled="loading">
              Save
            </el-button>
          </div>
        </div>
      </el-scrollbar>
    </div>
  </LayoutContainer>
</template>
<script setup lang="ts">
import { reactive, ref, watch, onMounted } from 'vue'
import emailApi from '@/api/email-setting'
import type { FormInstance, FormRules } from 'element-plus'

import { MsgSuccess } from '@/utils/message'
const form = ref<any>({
  email_host: '',
  email_port: '',
  email_host_user: '',
  email_host_password: '',
  email_use_tls: false,
  email_use_ssl: false,
  from_email: ''
})

const emailFormRef = ref()

const loading = ref(false)

const rules = reactive<FormRules<any>>({
  email_host: [{ required: true, message: 'Please enter. SMTP The host', trigger: 'blur' }],
  email_port: [{ required: true, message: 'Please enter. SMTP The port.', trigger: 'blur' }],
  email_host_user: [{ required: true, message: 'Please enter. SMTP The account', trigger: 'blur' }],
  email_host_password: [{ required: true, message: 'Please enter the mailbox password.', trigger: 'blur' }],
  from_email: [{ required: true, message: 'Please enter the sender’s mailbox.', trigger: 'blur' }]
})

const submit = async (formEl: FormInstance | undefined, test?: string) => {
  if (!formEl) return
  await formEl.validate((valid, fields) => {
    if (valid) {
      if (test) {
        emailApi.postTestEmail(form.value, loading).then((res) => {
          MsgSuccess('Test connectivity success.')
        })
      } else {
        emailApi.putEmailSetting(form.value, loading).then((res) => {
          MsgSuccess('Setup Success')
        })
      }
    }
  })
}

function getDetail() {
  emailApi.getEmailSetting(loading).then((res: any) => {
    if (res.data && JSON.stringify(res.data) !== '{}') {
      form.value = res.data
    }
  })
}

onMounted(() => {
  getDetail()
})
</script>
<style lang="scss" scoped>
.email-setting {
  width: 70%;
  margin: 0 auto;
  :deep(.el-checkbox__label) {
    font-weight: 400;
  }
}
</style>
