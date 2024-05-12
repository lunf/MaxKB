<template>
  <el-dialog title="Change the user password." v-model="dialogVisible">
    <el-form
      ref="userFormRef"
      :model="userForm"
      :rules="rules"
      label-position="top"
      require-asterisk-position="right"
      @submit.prevent
    >
      <el-form-item label="The new code." prop="password">
        <el-input
          type="password"
          v-model="userForm.password"
          placeholder="Please enter a new password."
          show-password
        >
        </el-input>
      </el-form-item>
      <el-form-item label="Confirm the password." prop="re_password">
        <el-input
          type="password"
          v-model="userForm.re_password"
          placeholder="Please enter the confirmation password."
          show-password
        >
        </el-input>
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click.prevent="dialogVisible = false"> cancelled </el-button>
        <el-button type="primary" @click="submit(userFormRef)" :loading="loading"> preserved </el-button>
      </span>
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import type { ResetPasswordRequest } from '@/api/type/user'
import userApi from '@/api/user-manage'
import { MsgSuccess } from '@/utils/message'

const emit = defineEmits(['refresh'])

const userFormRef = ref()
const userForm = ref<any>({
  password: '',
  re_password: ''
})

const rules = reactive<FormRules<ResetPasswordRequest>>({
  password: [
    {
      required: true,
      message: 'Please enter a new password.',
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
        if (userFormRef.value.password != userFormRef.value.re_password) {
          callback(new Error('The code is incompatible.'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
})
const dialogVisible = ref<boolean>(false)
const loading = ref(false)
const userId = ref('')

watch(dialogVisible, (bool) => {
  if (!bool) {
    userForm.value = {
      password: '',
      re_password: ''
    }
  }
})

const open = (data: any) => {
  userId.value = data.id
  dialogVisible.value = true
  userFormRef.value?.clearValidate()
}

const submit = async (formEl: FormInstance | undefined) => {
  if (!formEl) return
  await formEl.validate((valid, fields) => {
    if (valid) {
      userApi.putUserManagePassword(userId.value, userForm.value, loading).then((res) => {
        emit('refresh')
        MsgSuccess('Successful User Password Modification')
        dialogVisible.value = false
      })
    }
  })
}

defineExpose({ open })
</script>
<style lang="scss" scope></style>
