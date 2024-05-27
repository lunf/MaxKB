<template>
  <el-dialog
    title="synchronizing knowledge."
    v-model="dialogVisible"
    width="600px"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    :destroy-on-close="true"
  >
    <p class="mb-8">Method of synchronization</p>
    <el-radio-group v-model="method" class="card__radio">
      <el-card shadow="never" class="mb-16" :class="method === 'replace' ? 'active' : ''">
        <el-radio value="replace" size="large">
          <p class="mb-4">Replacement of Sync.</p>
          <el-text type="info">Recovered Web Site Documents, Replace documents in the local knowledge base</el-text>
        </el-radio>
      </el-card>

      <el-card shadow="never" class="mb-16" :class="method === 'complete' ? 'active' : ''">
        <el-radio value="complete" size="large">
          <p class="mb-4">Total synchronization.</p>
          <el-text type="info">Remove all documents from the local knowledge base. Recovered Web Site Documents</el-text>
        </el-radio>
      </el-card>
    </el-radio-group>
    <p class="danger">Attention:All synchronizations will remove existing data to re-accept new data. Please be careful. </p>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click.prevent="dialogVisible = false"> cancelled </el-button>
        <el-button type="primary" @click="submit" :loading="loading"> Certainly </el-button>
      </span>
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { ref, watch } from 'vue'

import { MsgSuccess } from '@/utils/message'

import useStore from '@/stores'
const { dataset } = useStore()

const emit = defineEmits(['refresh'])
const loading = ref<boolean>(false)
const method = ref('replace')
const datasetId = ref('')

const dialogVisible = ref<boolean>(false)

watch(dialogVisible, (bool) => {
  if (!bool) {
    method.value = 'replace'
  }
})

const open = (id: string) => {
  datasetId.value = id
  dialogVisible.value = true
}

const submit = () => {
  dataset.asyncSyncDataset(datasetId.value, method.value, loading).then((res: any) => {
    emit('refresh', res.data)
    dialogVisible.value = false
  })
}

defineExpose({ open })
</script>
<style lang="scss" scoped>
.select-provider {
  font-size: 16px;
  color: rgba(100, 106, 115, 1);
  font-weight: 400;
  line-height: 24px;
  cursor: pointer;
  &:hover {
    color: var(--el-color-primary);
  }
}
.active-breadcrumb {
  font-size: 16px;
  color: rgba(31, 35, 41, 1);
  font-weight: 500;
  line-height: 24px;
}
</style>
