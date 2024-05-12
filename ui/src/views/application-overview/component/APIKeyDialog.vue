<template>
  <el-dialog title="API Key" v-model="dialogVisible" width="800">
    <el-button type="primary" class="mb-16" @click="createApiKey"> Created </el-button>
    <el-table :data="apiKey" class="mb-16" :loading="loading">
      <el-table-column prop="secret_key" label="API Key">
        <template #default="{ row }">
          <span class="vertical-middle lighter break-all">
            {{ row.secret_key }}
          </span>
          <el-button type="primary" text @click="copyClick(row.secret_key)">
            <AppIcon iconName="app-copy"></AppIcon>
          </el-button>
        </template>
      </el-table-column>
      <el-table-column label="state of" width="60">
        <template #default="{ row }">
          <div @click.stop>
            <el-switch size="small" v-model="row.is_active" @change="changeState($event, row)" />
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="name" label="Date of Creation" width="170">
        <template #default="{ row }">
          {{ datetimeFormat(row.create_time) }}
        </template>
      </el-table-column>
      <el-table-column label="Operations" align="left" width="80">
        <template #default="{ row }">
          <span class="mr-4">
            <el-tooltip effect="dark" content="Setup" placement="top">
              <el-button type="primary" text @click.stop="settingApiKey(row)">
                <el-icon><Setting /></el-icon>
              </el-button>
            </el-tooltip>
          </span>
          <el-tooltip effect="dark" content="Delete" placement="top">
            <el-button type="primary" text @click="deleteApiKey(row)">
              <el-icon><Delete /></el-icon>
            </el-button>
          </el-tooltip>
        </template>
      </el-table-column>
    </el-table>
    <SettingAPIKeyDialog ref="SettingAPIKeyDialogRef" @refresh="refresh" />
  </el-dialog>
</template>
<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { copyClick } from '@/utils/clipboard'
import overviewApi from '@/api/application-overview'
import SettingAPIKeyDialog from './SettingAPIKeyDialog.vue'
import { datetimeFormat } from '@/utils/time'
import { MsgSuccess, MsgConfirm } from '@/utils/message'
const route = useRoute()
const {
  params: { id }
} = route

const emit = defineEmits(['addData'])

const SettingAPIKeyDialogRef = ref()
const dialogVisible = ref<boolean>(false)
const loading = ref(false)
const apiKey = ref<any>(null)

watch(dialogVisible, (bool) => {
  if (!bool) {
    apiKey.value = null
  }
})

function settingApiKey(row: any) {
  SettingAPIKeyDialogRef.value.open(row)
}

function deleteApiKey(row: any) {
  MsgConfirm(
    `is removed.API Key：${row.secret_key} ?`,
    `It cannot be used after deletion. API Key Calling the interface.，Please be careful.`,
    {
      confirmButtonText: 'removed',
      confirmButtonClass: 'danger'
    }
  )
    .then(() => {
      overviewApi.delAPIKey(id as string, row.id, loading).then(() => {
        MsgSuccess('Remove Success')
        getApiKeyList()
      })
    })
    .catch(() => {})
}

function changeState(bool: Boolean, row: any) {
  const obj = {
    is_active: bool
  }
  const str = bool ? 'Activate Success' : 'Prohibited success.'
  overviewApi.putAPIKey(id as string, row.id, obj, loading).then((res) => {
    MsgSuccess(str)
    getApiKeyList()
  })
}

function createApiKey() {
  overviewApi.postAPIKey(id as string, loading).then((res) => {
    getApiKeyList()
  })
}

const open = () => {
  getApiKeyList()
  dialogVisible.value = true
}

function getApiKeyList() {
  overviewApi.getAPIKey(id as string, loading).then((res) => {
    apiKey.value = res.data
  })
}

function refresh() {
  getApiKeyList()
}

defineExpose({ open })
</script>
<style lang="scss" scope>
.embed-dialog {
  .code {
    color: var(--app-text-color) !important;
    background: var(--app-layout-bg-color);
    font-weight: 400;
    font-size: 13px;
    white-space: pre;
    height: 180px;
  }
}
</style>
