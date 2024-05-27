<template>
  <el-dialog :title="title" v-model="dialogVisible">
    <el-form
      ref="userFormRef"
      :model="userForm"
      :rules="rules"
      label-position="top"
      require-asterisk-position="right"
      @submit.prevent
    >
      <el-form-item :prop="isEdit ? '' : 'username'" label="User Name">
        <el-input
          v-model="userForm.username"
          placeholder="Please enter the user name."
          maxlength="20"
          show-word-limit
          :disabled="isEdit"
        >
        </el-input>
      </el-form-item>
      <el-form-item label="Name of">
        <el-input
          v-model="userForm.nick_name"
          placeholder="Please enter the name."
          maxlength="64"
          show-word-limit
        >
        </el-input>
      </el-form-item>
      <el-form-item label="The mailbox" prop="email">
        <el-input type="email" v-model="userForm.email" placeholder="Please enter the mailbox."> </el-input>
      </el-form-item>
      <el-form-item label="The phone number.">
        <el-input type="email" v-model="userForm.phone" placeholder="Please enter the phone number."> </el-input>
      </el-form-item>
      <el-form-item label="Sign up the password." prop="password" v-if="!isEdit">
        <el-input
          type="password"
          v-model="userForm.password"
          placeholder="Please enter the password."
          show-password
        >
        </el-input>
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click.prevent="dialogVisible = false"> Cancel </el-button>
        <el-button type="primary" @click="submit(userFormRef)" :loading="loading"> Save </el-button>
      </span>
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import type { FormInstance } from 'element-plus'
import userApi from '@/api/user-manage'
import { MsgSuccess } from '@/utils/message'

const props = defineProps({
  title: String
})

const emit = defineEmits(['refresh'])

const userFormRef = ref()
const userForm = ref<any>({
  username: '',
  email: '',
  password: '',
  phone: '',
  nick_name: ''
})

const rules = reactive({
  username: [
    { required: true, message: 'Please enter the user name.', trigger: 'blur' },
    {
      min: 6,
      max: 20,
      message: 'The length is 6 to 20 A character.',
      trigger: 'blur'
    }
  ],
  email: [{ required: true, message: 'Please enter the mailbox.', trigger: 'blur' }],
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
  ]
})
const dialogVisible = ref<boolean>(false)
const loading = ref(false)
const isEdit = ref(false)

watch(dialogVisible, (bool) => {
  if (!bool) {
    userForm.value = {
      username: '',
      email: '',
      password: '',
      phone: '',
      nick_name: ''
    }
    isEdit.value = false
    userFormRef.value?.clearValidate()
  }
})

const open = (data: any) => {
  if (data) {
    userForm.value['id'] = data.id
    userForm.value.username = data.username
    userForm.value.email = data.email
    userForm.value.password = data.password
    userForm.value.phone = data.phone
    userForm.value.nick_name = data.nick_name
    isEdit.value = true
  }
  dialogVisible.value = true
}

const submit = async (formEl: FormInstance | undefined) => {
  if (!formEl) return
  await formEl.validate((valid, fields) => {
    if (valid) {
      if (isEdit.value) {
        userApi.putUserManage(userForm.value.id, userForm.value, loading).then((res) => {
          emit('refresh')
          MsgSuccess('Editing Successful')
          dialogVisible.value = false
        })
      } else {
        userApi.postUserManage(userForm.value, loading).then((res) => {
          emit('refresh')
          MsgSuccess('Creating Success')
          dialogVisible.value = false
        })
      }
    }
  })
}

defineExpose({ open })
</script>
<style lang="scss" scope></style>
