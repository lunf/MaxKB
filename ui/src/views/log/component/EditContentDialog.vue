<template>
  <el-dialog title="Modification of content" v-model="dialogVisible" width="600">
    <el-form
      ref="formRef"
      :model="form"
      label-position="top"
      require-asterisk-position="right"
      :rules="rules"
      @submit.prevent
    >
      <el-form-item label="Related issues">
        <span>{{ form.problem_text }}</span>
      </el-form-item>
      <el-form-item label="The content" prop="content">
        <el-input
          v-model="form.content"
          placeholder="Please enter the content."
          maxlength="4096"
          show-word-limit
          :rows="8"
          type="textarea"
        >
        </el-input>
      </el-form-item>
      <el-form-item label="The title">
        <el-input v-model="form.title" placeholder="Please set a title for the current content.，To manage checking.">
        </el-input>
      </el-form-item>
      <el-form-item label="Choose a Knowledge Base" prop="dataset_id">
        <el-select
          v-model="form.dataset_id"
          filterable
          placeholder="Please select the knowledge base."
          :loading="optionLoading"
          @change="changeDataset"
        >
          <el-option v-for="item in datasetList" :key="item.id" :label="item.name" :value="item.id">
            <span class="flex align-center">
              <AppAvatar
                v-if="!item.dataset_id && item.type === '1'"
                class="mr-12 avatar-purple"
                shape="square"
                :size="24"
              >
                <img src="@/assets/icon_web.svg" style="width: 58%" alt="" />
              </AppAvatar>
              <AppAvatar
                v-else-if="!item.dataset_id && item.type === '0'"
                class="mr-12"
                shape="square"
                :size="24"
              >
                <img src="@/assets/icon_document.svg" style="width: 58%" alt="" />
              </AppAvatar>
              {{ item.name }}
            </span>
          </el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="Save to the documentation." prop="document_id">
        <el-select
          v-model="form.document_id"
          filterable
          placeholder="Please select the document."
          :loading="optionLoading"
        >
          <el-option
            v-for="item in documentList"
            :key="item.id"
            :label="item.name"
            :value="item.id"
          >
            {{ item.name }}
          </el-option>
        </el-select>
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click.prevent="dialogVisible = false"> cancelled </el-button>
        <el-button type="primary" @click="submitForm(formRef)" :loading="loading"> Save </el-button>
      </span>
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { ref, watch, reactive } from 'vue'
import { useRoute } from 'vue-router'
import type { FormInstance, FormRules } from 'element-plus'
import logApi from '@/api/log'
import useStore from '@/stores'

const { application, document } = useStore()

const props = defineProps({
  chartId: {
    type: String,
    default: ''
  }
})

const route = useRoute()
const {
  params: { id }
} = route as any

const emit = defineEmits(['refresh'])
const formRef = ref()

const dialogVisible = ref<boolean>(false)
const loading = ref(false)

const form = ref<any>({
  chat_id: '',
  record_id: '',
  problem_text: '',
  title: '',
  content: '',
  dataset_id: '',
  document_id: ''
})

const rules = reactive<FormRules>({
  content: [{ required: true, message: 'Please enter the content.', trigger: 'blur' }],
  dataset_id: [{ required: true, message: 'Please select the knowledge base.', trigger: 'change' }],
  document_id: [{ required: true, message: 'Please select the document.', trigger: 'change' }]
})

const datasetList = ref<any[]>([])
const documentList = ref<any[]>([])
const optionLoading = ref(false)

watch(dialogVisible, (bool) => {
  if (!bool) {
    form.value = {
      chat_id: '',
      record_id: '',
      problem_text: '',
      title: '',
      content: '',
      dataset_id: '',
      document_id: ''
    }
    datasetList.value = []
    documentList.value = []
    formRef.value?.clearValidate()
  }
})


function changeDataset(id: string) {
  form.value.document_id = ''
  getDocument(id)
}

function getDocument(id: string) {
  document.asyncGetAllDocument(id, loading).then((res: any) => {
    documentList.value = res.data
  })
}

function getDataset() {
  application.asyncGetApplicationDataset(id, loading).then((res: any) => {
    datasetList.value = res.data
  })
}

const open = (data: any) => {
  getDataset()
  form.value.chat_id = data.chat_id
  form.value.record_id = data.id
  form.value.problem_text = data.problem_text
  form.value.content = data.answer_text
  formRef.value?.clearValidate()
  dialogVisible.value = true
}
const submitForm = async (formEl: FormInstance | undefined) => {
  if (!formEl) return
  await formEl.validate((valid, fields) => {
    if (valid) {
      const obj = {
        title: form.value.title,
        content: form.value.content
      }
      logApi
        .putChatRecordLog(
          id,
          form.value.chat_id,
          form.value.record_id,
          form.value.dataset_id,
          form.value.document_id,
          obj,
          loading
        )
        .then((res: any) => {
          emit('refresh', res.data)
          dialogVisible.value = false
        })
    }
  })
}

defineExpose({ open })
</script>
<style lang="scss" scope></style>
