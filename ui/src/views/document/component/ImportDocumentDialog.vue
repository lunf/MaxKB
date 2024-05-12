<template>
  <el-dialog
    title="Introduction of documents"
    v-model="dialogVisible"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    :destroy-on-close="true"
  >
    <el-form
      label-position="top"
      ref="webFormRef"
      :rules="rules"
      :model="form"
      require-asterisk-position="right"
    >
      <el-form-item label="The document address." prop="source_url" v-if="isImport">
        <el-input
          v-model="form.source_url"
          placeholder="Please enter the document address.，One line one.，The incorrect address document will fail.。"
          :rows="10"
          type="textarea"
        />
      </el-form-item>
      <el-form-item v-else-if="documentType === '1'" label="The document address." prop="source_url">
        <el-input v-model="form.source_url" placeholder="Please enter the document address." />
      </el-form-item>
      <el-form-item label="The Selector" v-if="documentType === '1'">
        <el-input
          v-model="form.selector"
          placeholder="I think body，can enter. .classname/#idname/tagname"
        />
      </el-form-item>
      <el-form-item v-if="!isImport">
        <template #label>
          <div class="flex align-center">
            <span class="mr-4">Method of Treatment</span>
            <el-tooltip
              effect="dark"
              content="When User Questions，Parts under the life Chinese file are processed according to the way set.。"
              placement="right"
            >
              <AppIcon iconName="app-warning" class="app-warning-icon"></AppIcon>
            </el-tooltip>
          </div>
        </template>
        <el-radio-group v-model="form.hit_handling_method">
          <template v-for="(value, key) of hitHandlingMethod" :key="key">
            <el-radio :value="key">{{ value }}</el-radio>
          </template>
        </el-radio-group>
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click.prevent="dialogVisible = false"> cancelled </el-button>
        <el-button type="primary" @click="submit(webFormRef)" :loading="loading"> Certainly </el-button>
      </span>
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import { useRoute } from 'vue-router'
import type { FormInstance, FormRules } from 'element-plus'
import documentApi from '@/api/document'
import { MsgSuccess } from '@/utils/message'
import { hitHandlingMethod } from '../utils'

const route = useRoute()
const {
  params: { id }
} = route as any

const emit = defineEmits(['refresh'])
const webFormRef = ref()
const loading = ref<boolean>(false)
const isImport = ref<boolean>(false)
const form = ref<any>({
  source_url: '',
  selector: '',
  hit_handling_method: ''
})
const documentId = ref('')
const documentType = ref<string | number>('') //Type of Documentation：1: webDocuments；0:Ordinary Documents

const rules = reactive({
  source_url: [{ required: true, message: 'Please enter the document address.', trigger: 'blur' }]
})

const dialogVisible = ref<boolean>(false)

watch(dialogVisible, (bool) => {
  if (!bool) {
    form.value = {
      source_url: '',
      selector: '',
      hit_handling_method: ''
    }
    isImport.value = false
    documentType.value = ''
  }
})

const open = (row: any) => {
  if (row) {
    documentType.value = row.type
    documentId.value = row.id
    form.value = { hit_handling_method: row.hit_handling_method, ...row.meta }
    isImport.value = false
  } else {
    isImport.value = true
  }
  dialogVisible.value = true
}

const submit = async (formEl: FormInstance | undefined) => {
  if (!formEl) return
  await formEl.validate((valid, fields) => {
    if (valid) {
      if (isImport.value) {
        const obj = {
          source_url_list: form.value.source_url.split('\n'),
          selector: form.value.selector
        }
        documentApi.postWebDocument(id, obj, loading).then((res: any) => {
          MsgSuccess('Introduction to Success')
          emit('refresh')
          dialogVisible.value = false
        })
      } else {
        const obj = {
          hit_handling_method: form.value.hit_handling_method,
          meta: {
            source_url: form.value.source_url,
            selector: form.value.selector
          }
        }
        documentApi.putDocument(id, documentId.value, obj, loading).then((res) => {
          MsgSuccess('Setup Success')
          emit('refresh')
          dialogVisible.value = false
        })
      }
    }
  })
}

defineExpose({ open })
</script>
<style lang="scss" scoped></style>
