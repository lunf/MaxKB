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
          placeholder="Please enter the document address. One line one. The incorrect address document will fail. "
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
          placeholder="I think body, can enter. .classname/#idname/tagname"
        />
      </el-form-item>
      <el-form-item v-if="!isImport">
        <template #label>
          <div class="flex align-center">
            <span class="mr-4">Method of Treatment</span>
            <el-tooltip
              effect="dark"
              content="When User Questions, Parts under the life Chinese file are processed according to the way set. "
              placement="right"
            >
              <AppIcon iconName="app-warning" class="app-warning-icon"></AppIcon>
            </el-tooltip>
          </div>
        </template>
        <el-radio-group v-model="form.hit_handling_method" class="radio-block mt-4">
          <template v-for="(value, key) of hitHandlingMethod" :key="key">
            <el-radio :value="key">{{ value }} </el-radio>
          </template>
        </el-radio-group>
      </el-form-item>
      <el-form-item
        prop="directly_return_similarity"
        v-if="!isImport && form.hit_handling_method === 'directly_return'"
      >
        <div class="lighter w-full" style="margin-top: -20px">
          <span>Similarity is higher than</span>
          <el-input-number
            v-model="form.directly_return_similarity"
            :min="0"
            :max="1"
            :precision="3"
            :step="0.1"
            controls-position="right"
            size="small"
            class="ml-4 mr-4"
          /><span>Return segmented content directly</span>
        </div>
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
  hit_handling_method: 'optimization',
  directly_return_similarity: 0.9
})

// Document settings
const documentId = ref('')
const documentType = ref<string | number>('') //Type of Documentation:1: webDocuments；0:Ordinary Documents

// Batch settings
const documentList = ref<Array<string>>([])

const rules = reactive({
  source_url: [{ required: true, message: 'Please enter the document address', trigger: 'blur' }],
  directly_return_similarity: [{ required: true, message: 'Please enter the similarity', trigger: 'blur' }]
})

const dialogVisible = ref<boolean>(false)

watch(dialogVisible, (bool) => {
  if (!bool) {
    form.value = {
      source_url: '',
      selector: '',
      hit_handling_method: 'optimization',
      directly_return_similarity: 0.9
    }
    isImport.value = false
    documentType.value = ''
    documentList.value = []
  }
})

const open = (row: any, list: Array<string>) => {
  if (row) {
    documentType.value = row.type
    documentId.value = row.id
    form.value = {
      hit_handling_method: row.hit_handling_method,
      directly_return_similarity: row.directly_return_similarity,
      ...row.meta
    }
    isImport.value = false
  } else if (list) {
    // 批量设置
    documentList.value = list
  } else {
    // 导入
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
        if (documentId.value) {
          const obj = {
            hit_handling_method: form.value.hit_handling_method,
            directly_return_similarity: form.value.directly_return_similarity || 0.9,
            meta: {
              source_url: form.value.source_url,
              selector: form.value.selector
            }
          }
          documentApi.putDocument(id, documentId.value, obj, loading).then((res) => {
            MsgSuccess('设置成功')
            emit('refresh')
            dialogVisible.value = false
          })
        } else if (documentList.value.length > 0) {
          // 批量设置
          const obj = {
            hit_handling_method: form.value.hit_handling_method,
            directly_return_similarity: form.value.directly_return_similarity,
            id_list: documentList.value
          }
          documentApi.batchEditHitHandling(id, obj, loading).then((res: any) => {
            MsgSuccess('设置成功')
            emit('refresh')
            dialogVisible.value = false
          })
        }
      }
    }
  })
}

defineExpose({ open })
</script>
<style lang="scss" scoped></style>
