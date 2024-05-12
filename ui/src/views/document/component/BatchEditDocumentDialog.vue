<template>
  <el-dialog
    title="set up"
    v-model="dialogVisible"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    :destroy-on-close="true"
    width="400"
  >
    <el-form
      label-position="top"
      ref="webFormRef"
      :rules="rules"
      :model="form"
      require-asterisk-position="right"
    >
      <el-form-item>
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
const documentList = ref<Array<string>>([])
const form = ref<any>({
  hit_handling_method: 'optimization'
})

const rules = reactive({
  source_url: [{ required: true, message: 'Please enter the document address.', trigger: 'blur' }]
})

const dialogVisible = ref<boolean>(false)

const open = (list: Array<string>) => {
  documentList.value = list
  dialogVisible.value = true
}

const submit = async (formEl: FormInstance | undefined) => {
  if (!formEl) return
  await formEl.validate((valid, fields) => {
    if (valid) {
      const obj = {
        hit_handling_method: form.value.hit_handling_method,
        id_list: documentList.value
      }
      documentApi.batchEditHitHandling(id, obj, loading).then((res: any) => {
        MsgSuccess('Setup Success')
        emit('refresh')
        dialogVisible.value = false
      })
    }
  })
}

defineExpose({ open })
</script>
<style lang="scss" scoped></style>
