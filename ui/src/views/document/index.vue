<template>
  <LayoutContainer header="Documents">
    <div class="main-calc-height">
      <div class="p-24">
        <div class="flex-between">
          <div>
            <el-button
              v-if="datasetDetail.type === '0'"
              type="primary"
              @click="router.push({ path: '/dataset/upload', query: { id: id } })"
              >uploaded documents.</el-button
            >
            <el-button v-if="datasetDetail.type === '1'" type="primary" @click="importDoc"
              >Introduction of documents</el-button
            >
            <el-button @click="syncDataset" v-if="datasetDetail.type === '1'">synchronizing knowledge.</el-button>
            <el-button
              @click="syncMulDocument"
              :disabled="multipleSelection.length === 0"
              v-if="datasetDetail.type === '1'"
              >synchronizing documents.</el-button
            >
            <el-button @click="openDatasetDialog()" :disabled="multipleSelection.length === 0">
              Migration
            </el-button>
            <el-button @click="openBatchEditDocument" :disabled="multipleSelection.length === 0">
              Setup
            </el-button>
            <el-button @click="deleteMulDocument" :disabled="multipleSelection.length === 0">
              Delete
            </el-button>
          </div>

          <el-input
            v-model="filterText"
            placeholder="by Name of documentation Searching"
            prefix-icon="Search"
            class="w-240"
            @change="getList"
            clearable
          />
        </div>
        <app-table
          ref="multipleTableRef"
          class="mt-16"
          :data="documentData"
          :pagination-config="paginationConfig"
          :quick-create="datasetDetail.type === '0'"
          @sizeChange="handleSizeChange"
          @changePage="getList"
          @cell-mouse-enter="cellMouseEnter"
          @cell-mouse-leave="cellMouseLeave"
          @creatQuick="creatQuickHandle"
          @row-click="rowClickHandle"
          @selection-change="handleSelectionChange"
          v-loading="loading"
          :row-key="(row: any) => row.id"
          :storeKey="storeKey"
        >
          <el-table-column type="selection" width="55" :reserve-selection="true" />
          <el-table-column prop="name" label="Name of document" min-width="280">
            <template #default="{ row }">
              <ReadWrite
                @change="editName($event, row.id)"
                :data="row.name"
                :showEditIcon="row.id === currentMouseId"
              />
            </template>
          </el-table-column>
          <el-table-column prop="char_length" label="Number of characters" align="right">
            <template #default="{ row }">
              {{ numberFormat(row.char_length) }}
            </template>
          </el-table-column>
          <el-table-column prop="paragraph_count" label="Parts" align="right" />
          <el-table-column prop="status" label="The document state." min-width="90">
            <template #default="{ row }">
              <el-text v-if="row.status === '1'">
                <el-icon class="success"><SuccessFilled /></el-icon> Successful
              </el-text>
              <el-text v-else-if="row.status === '2'">
                <el-icon class="danger"><CircleCloseFilled /></el-icon> Failure
              </el-text>
              <el-text v-else-if="row.status === '0'">
                <el-icon class="is-loading primary"><Loading /></el-icon> In the import.
              </el-text>
            </template>
          </el-table-column>
          <el-table-column label="Activated state">
            <template #default="{ row }">
              <div @click.stop>
                <el-switch
                  size="small"
                  v-model="row.is_active"
                  @change="changeState($event, row)"
                />
              </div>
            </template>
          </el-table-column>
          <el-table-column width="130">
            <template #header>
              <div>
                <span>Method of Treatment</span>
                <el-dropdown trigger="click" @command="dropdownHandle">
                  <el-button style="margin-top: 1px" link :type="filterMethod ? 'primary' : ''">
                    <el-icon><Filter /></el-icon>
                  </el-button>
                  <template #dropdown>
                    <el-dropdown-menu style="width: 100px">
                      <el-dropdown-item
                        :class="filterMethod ? '' : 'is-active'"
                        command=""
                        class="justify-center"
                        >All of</el-dropdown-item
                      >
                      <template v-for="(value, key) of hitHandlingMethod" :key="key">
                        <el-dropdown-item
                          :class="filterMethod === key ? 'is-active' : ''"
                          class="justify-center"
                          :command="key"
                          >{{ value }}</el-dropdown-item
                        >
                      </template>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </div>
            </template>
            <template #default="{ row }">
              {{ hitHandlingMethod[row.hit_handling_method] }}
            </template>
          </el-table-column>
          <el-table-column prop="create_time" label="Creating time." width="175">
            <template #default="{ row }">
              {{ datetimeFormat(row.create_time) }}
            </template>
          </el-table-column>
          <el-table-column prop="update_time" label="Updated time" width="175">
            <template #default="{ row }">
              {{ datetimeFormat(row.update_time) }}
            </template>
          </el-table-column>
          <el-table-column label="Operations" align="left" width="110">
            <template #default="{ row }">
              <div v-if="datasetDetail.type === '0'">
                <span v-if="row.status === '2'" class="mr-4">
                  <el-tooltip effect="dark" content="Repeated" placement="top">
                    <el-button type="primary" text @click.stop="refreshDocument(row)">
                      <el-icon><RefreshRight /></el-icon>
                    </el-button>
                  </el-tooltip>
                </span>
                <span class="mr-4">
                  <el-tooltip effect="dark" content="set up" placement="top">
                    <el-button type="primary" text @click.stop="settingDoc(row)">
                      <el-icon><Setting /></el-icon>
                    </el-button>
                  </el-tooltip>
                </span>
                <span @click.stop>
                  <el-dropdown trigger="click">
                    <el-button text>
                      <el-icon><MoreFilled /></el-icon>
                    </el-button>
                    <template #dropdown>
                      <el-dropdown-menu>
                        <el-dropdown-item @click="openDatasetDialog(row)">
                          <AppIcon iconName="app-migrate"></AppIcon>
                          Migration</el-dropdown-item
                        >
                        <el-dropdown-item icon="Delete" @click.stop="deleteDocument(row)"
                          >removed</el-dropdown-item
                        >
                      </el-dropdown-menu>
                    </template>
                  </el-dropdown>
                </span>
              </div>
              <div v-if="datasetDetail.type === '1'">
                <el-tooltip
                  effect="dark"
                  content="synchronized"
                  placement="top"
                  v-if="datasetDetail.type === '1'"
                >
                  <el-button type="primary" text @click.stop="refreshDocument(row)">
                    <el-icon><Refresh /></el-icon>
                  </el-button>
                </el-tooltip>
                <span @click.stop>
                  <el-dropdown trigger="click">
                    <el-button text>
                      <el-icon><MoreFilled /></el-icon>
                    </el-button>
                    <template #dropdown>
                      <el-dropdown-menu>
                        <el-dropdown-item icon="Setting" @click="settingDoc(row)"
                          >set up</el-dropdown-item
                        >
                        <el-dropdown-item @click="openDatasetDialog(row)">
                          <AppIcon iconName="app-migrate"></AppIcon>
                          Migration</el-dropdown-item
                        >
                        <el-dropdown-item icon="Delete" @click.stop="deleteDocument(row)"
                          >removed</el-dropdown-item
                        >
                      </el-dropdown-menu>
                    </template>
                  </el-dropdown>
                </span>
              </div>
            </template>
          </el-table-column>
        </app-table>
      </div>
      <ImportDocumentDialog ref="ImportDocumentDialogRef" :title="title" @refresh="refresh" />
      <SyncWebDialog ref="SyncWebDialogRef" @refresh="refresh" />
      <!-- Select knowledge base -->
      <SelectDatasetDialog ref="SelectDatasetDialogRef" @refresh="refresh" />
    </div>
  </LayoutContainer>
</template>
<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, computed } from 'vue'
import { useRouter, useRoute, onBeforeRouteLeave, onBeforeRouteUpdate } from 'vue-router'
import { ElTable } from 'element-plus'
import documentApi from '@/api/document'
import ImportDocumentDialog from './component/ImportDocumentDialog.vue'
import SyncWebDialog from '@/views/dataset/component/SyncWebDialog.vue'
import SelectDatasetDialog from './component/SelectDatasetDialog.vue'
import { numberFormat } from '@/utils/utils'
import { datetimeFormat } from '@/utils/time'
import { hitHandlingMethod } from './utils'
import { MsgSuccess, MsgConfirm, MsgError } from '@/utils/message'
import useStore from '@/stores'
const router = useRouter()
const route = useRoute()
const {
  params: { id } // idfordatasetID
} = route as any

const { common, dataset, document } = useStore()

const storeKey = 'documents'

onBeforeRouteUpdate((to: any, from: any) => {
  common.savePage(storeKey, null)
  common.saveCondition(storeKey, null)
})
onBeforeRouteLeave((to: any, from: any) => {
  if (to.name !== 'Paragraph') {
    common.savePage(storeKey, null)
    common.saveCondition(storeKey, null)
  } else {
    common.saveCondition(storeKey, {
      filterText: filterText.value,
      filterMethod: filterMethod.value
    })
  }
})
const beforePagination = computed(() => common.paginationConfig[storeKey])
const beforeSearch = computed(() => common.search[storeKey])

const SyncWebDialogRef = ref()
const loading = ref(false)
let interval: any
const filterText = ref('')
const filterMethod = ref<string | number>('')
const documentData = ref<any[]>([])
const currentMouseId = ref(null)
const datasetDetail = ref<any>({})

const paginationConfig = ref({
  current_page: 1,
  page_size: 10,
  total: 0
})

const ImportDocumentDialogRef = ref()
const multipleTableRef = ref<InstanceType<typeof ElTable>>()
const multipleSelection = ref<any[]>([])
const title = ref('')

const SelectDatasetDialogRef = ref()

function openDatasetDialog(row?: any) {
  const arr: string[] = []
  if (row) {
    arr.push(row.id)
  } else {
    multipleSelection.value.map((v) => {
      if (v) {
        arr.push(v.id)
      }
    })
  }

  SelectDatasetDialogRef.value.open(arr)
}

function dropdownHandle(val: string) {
  filterMethod.value = val
  getList()
}

function syncDataset() {
  SyncWebDialogRef.value.open(id)
}

function importDoc() {
  title.value = 'Introduction of documents'
  ImportDocumentDialogRef.value.open()
}
function settingDoc(row: any) {
  title.value = 'set up'
  ImportDocumentDialogRef.value.open(row)
}

const handleSelectionChange = (val: any[]) => {
  multipleSelection.value = val
}

function openBatchEditDocument() {
  title.value = '设置'
  const arr: string[] = multipleSelection.value.map((v) => v.id)
  ImportDocumentDialogRef.value.open(null, arr)
}

/**
 * Initial Question.
 */
const initInterval = () => {
  interval = setInterval(() => {
    getList(true)
  }, 6000)
}

/**
 * Closing the query.
 */
const closeInterval = () => {
  if (interval) {
    clearInterval(interval)
  }
}
function refreshDocument(row: any) {
  if (row.type === '1') {
    if (row.meta?.source_url) {
      MsgConfirm(`Confirm synchronized documents.?`, `Synchronization will remove existing data to regain new data.，Please be careful.。`, {
        confirmButtonText: 'synchronized',
        confirmButtonClass: 'danger'
      })
        .then(() => {
          documentApi.putDocumentRefresh(row.dataset_id, row.id).then((res) => {
            getList()
          })
        })
        .catch(() => {})
    } else {
      MsgConfirm(`The Tip`, `cannot synchronize.，Please set up the document. URLAddressed`, {
        confirmButtonText: 'confirmed',
        type: 'warning'
      })
        .then(() => {})
        .catch(() => {})
    }
  } else {
    documentApi.putDocumentRefresh(row.dataset_id, row.id).then((res) => {
      getList()
    })
  }
}

function rowClickHandle(row: any) {
  router.push({ path: `/dataset/${id}/${row.id}` })
}

/*
  Create empty documents quickly.
*/
function creatQuickHandle(val: string) {
  loading.value = true
  const obj = [{ name: val }]
  document
    .asyncPostDocument(id, obj)
    .then(() => {
      getList()
      MsgSuccess('Creating Success')
    })
    .catch(() => {
      loading.value = false
    })
}

function syncMulDocument() {
  const arr: string[] = []
  multipleSelection.value.map((v) => {
    if (v) {
      arr.push(v.id)
    }
  })
  documentApi.delMulSyncDocument(id, arr, loading).then(() => {
    MsgSuccess('Successful synchronization of documents')
    getList()
  })
}

function deleteMulDocument() {
  const arr: string[] = []
  multipleSelection.value.map((v) => {
    if (v) {
      arr.push(v.id)
    }
  })
  documentApi.delMulDocument(id, arr, loading).then(() => {
    MsgSuccess('Removal of success.')
    getList()
  })
}

function deleteDocument(row: any) {
  MsgConfirm(
    `Remove the document.：${row.name} ?`,
    `Under this document. ${row.paragraph_count} Parts will be removed.，Please be careful.。`,
    {
      confirmButtonText: 'removed',
      confirmButtonClass: 'danger'
    }
  )
    .then(() => {
      documentApi.delDocument(id, row.id, loading).then(() => {
        MsgSuccess('Remove Success')
        getList()
      })
    })
    .catch(() => {})
}

/*
  Updated Name or Status
*/
function updateData(documentId: string, data: any, msg: string) {
  documentApi.putDocument(id, documentId, data, loading).then((res) => {
    const index = documentData.value.findIndex((v) => v.id === documentId)
    documentData.value.splice(index, 1, res.data)
    MsgSuccess(msg)
  })
}

function changeState(bool: Boolean, row: any) {
  const obj = {
    is_active: bool
  }
  const str = bool ? 'Activate Success' : 'Prohibited success.'
  currentMouseId.value && updateData(row.id, obj, str)
}

function editName(val: string, id: string) {
  if (val) {
    const obj = {
      name: val
    }
    updateData(id, obj, 'Changes are Successful')
  } else {
    MsgError('The document name cannot be empty.！')
  }
}

function cellMouseEnter(row: any) {
  currentMouseId.value = row.id
}
function cellMouseLeave() {
  currentMouseId.value = null
}

function handleSizeChange() {
  paginationConfig.value.current_page = 1
  getList()
}

function getList(bool?: boolean) {
  const param = {
    ...(filterText.value && { name: filterText.value }),
    ...(filterMethod.value && { hit_handling_method: filterMethod.value })
  }
  documentApi
    .getDocument(id as string, paginationConfig.value, param, bool ? undefined : loading)
    .then((res) => {
      documentData.value = res.data.records
      paginationConfig.value.total = res.data.total
    })
}

function getDetail() {
  dataset.asyncGetDatasetDetail(id, loading).then((res: any) => {
    datasetDetail.value = res.data
  })
}

function refresh() {
  paginationConfig.value.current_page = 1
  getList()
}

onMounted(() => {
  getDetail()
  if (beforePagination.value) {
    paginationConfig.value = beforePagination.value
  }
  if (beforeSearch.value) {
    filterText.value = beforeSearch.value['filterText']
    filterMethod.value = beforeSearch.value['filterMethod']
  }
  getList()
  // Starting timely tasks
  initInterval()
})

onBeforeUnmount(() => {
  // Delete timely tasks.
  closeInterval()
})
</script>
<style lang="scss" scoped></style>
