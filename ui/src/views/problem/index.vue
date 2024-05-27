<template>
  <LayoutContainer header="The problem">
    <div class="main-calc-height">
      <div class="p-24">
        <div class="flex-between">
          <div>
            <el-button type="primary" @click="createProblem">Creating problems.</el-button>
            <el-button @click="deleteMulDocument" :disabled="multipleSelection.length === 0"
              >Mass removal.</el-button
            >
          </div>

          <el-input
            v-model="filterText"
            placeholder="Search of content"
            prefix-icon="Search"
            class="w-240"
            @change="getList"
            clearable
          />
        </div>
        <app-table
          ref="multipleTableRef"
          class="mt-16"
          :data="problemData"
          :pagination-config="paginationConfig"
          quick-create
          quickCreateName="The problem"
          quickCreatePlaceholder="Create problems quickly."
          :quickCreateMaxlength="256"
          @sizeChange="handleSizeChange"
          @changePage="getList"
          @cell-mouse-enter="cellMouseEnter"
          @cell-mouse-leave="cellMouseLeave"
          @creatQuick="creatQuickHandle"
          @row-click="rowClickHandle"
          @selection-change="handleSelectionChange"
          :row-class-name="setRowClass"
          v-loading="loading"
          :row-key="(row: any) => row.id"
        >
          <el-table-column type="selection" width="55" :reserve-selection="true" />
          <el-table-column prop="content" label="The problem" min-width="280">
            <template #default="{ row }">
              <ReadWrite
                @change="editName($event, row.id)"
                :data="row.content"
                :showEditIcon="row.id === currentMouseId"
                :maxlength="256"
              />
            </template>
          </el-table-column>
          <el-table-column prop="paragraph_count" label="Related numbers" align="right" min-width="100">
            <template #default="{ row }">
              <el-link type="primary" @click.stop="rowClickHandle(row)" v-if="row.paragraph_count">
                {{ row.paragraph_count }}
              </el-link>
              <span v-else>
                {{ row.paragraph_count }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="create_time" label="Creating time." width="170">
            <template #default="{ row }">
              {{ datetimeFormat(row.create_time) }}
            </template>
          </el-table-column>
          <el-table-column prop="update_time" label="Updated time" width="170">
            <template #default="{ row }">
              {{ datetimeFormat(row.update_time) }}
            </template>
          </el-table-column>
          <el-table-column label="Operations" align="left">
            <template #default="{ row }">
              <div>
                <span class="mr-4">
                  <el-tooltip effect="dark" content="Related Sections" placement="top">
                    <el-button type="primary" text @click.stop="relateProblem(row)">
                      <el-icon><Connection /></el-icon>
                    </el-button>
                  </el-tooltip>
                </span>
                <span>
                  <el-tooltip effect="dark" content="removed" placement="top">
                    <el-button type="primary" text @click.stop="deleteProblem(row)">
                      <el-icon><Delete /></el-icon>
                    </el-button>
                  </el-tooltip>
                </span>
              </div>
            </template>
          </el-table-column>
        </app-table>
      </div>
    </div>
    <CreateProblemDialog ref="CreateProblemDialogRef" @refresh="refresh" />
    <DetailProblemDrawer
      :next="nextChatRecord"
      :pre="preChatRecord"
      ref="DetailProblemRef"
      v-model:currentId="currentClickId"
      v-model:currentContent="currentContent"
      :pre_disable="pre_disable"
      :next_disable="next_disable"
      @refresh="refresh"
    />
    <RelateProblemDialog ref="RelateProblemDialogRef" @refresh="refresh" />
  </LayoutContainer>
</template>
<script setup lang="ts">
import { ref, onMounted, reactive, onBeforeUnmount, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElTable } from 'element-plus'
import problemApi from '@/api/problem'
import CreateProblemDialog from './component/CreateProblemDialog.vue'
import DetailProblemDrawer from './component/DetailProblemDrawer.vue'
import RelateProblemDialog from './component/RelateProblemDialog.vue'
import { datetimeFormat } from '@/utils/time'
import { MsgSuccess, MsgConfirm, MsgError } from '@/utils/message'
import type { Dict } from '@/api/type/common'
import useStore from '@/stores'

const route = useRoute()
const {
  params: { id } // The knowledge baseid
} = route as any

const { problem } = useStore()

const RelateProblemDialogRef = ref()
const DetailProblemRef = ref()
const CreateProblemDialogRef = ref()
const loading = ref(false)

// The problem needs to be modified.id
const currentMouseId = ref('')
// Now click open.drawerofid
const currentClickId = ref('')
const currentContent = ref('')

const paginationConfig = reactive({
  current_page: 1,
  page_size: 10,
  total: 0
})

const filterText = ref('')
const problemData = ref<any[]>([])
const problemIndexMap = computed<Dict<number>>(() => {
  return problemData.value
    .map((row, index) => ({
      [row.id]: index
    }))
    .reduce((pre, next) => ({ ...pre, ...next }), {})
})

const multipleTableRef = ref<InstanceType<typeof ElTable>>()
const multipleSelection = ref<any[]>([])

function relateProblem(row: any) {
  RelateProblemDialogRef.value.open(row.id)
}

function createProblem() {
  CreateProblemDialogRef.value.open()
}

const handleSelectionChange = (val: any[]) => {
  multipleSelection.value = val
}

/*
  Create empty documents quickly.
*/
function creatQuickHandle(val: string) {
  loading.value = true
  const obj = [val]
  problem
    .asyncPostProblem(id, obj)
    .then((res) => {
      getList()
      MsgSuccess('Creating Success')
    })
    .catch(() => {
      loading.value = false
    })
}

function deleteMulDocument() {
  const arr: string[] = []
  multipleSelection.value.map((v) => {
    if (v) {
      arr.push(v.id)
    }
  })
  problemApi.delMulProblem(id, arr, loading).then(() => {
    MsgSuccess('Removal of success.')
    getList()
  })
}

function deleteProblem(row: any) {
  MsgConfirm(
    `Remove the problem. ${row.content} ?`,
    `Delete the problem related. ${row.paragraph_count} A section will be cancelled. Please be careful. `,
    {
      confirmButtonText: 'removed',
      confirmButtonClass: 'danger'
    }
  )
    .then(() => {
      problemApi.delProblems(id, row.id, loading).then(() => {
        MsgSuccess('Remove Success')
        getList()
      })
    })
    .catch(() => {})
}

function editName(val: string, problemId: string) {
  if (val) {
    const obj = {
      content: val
    }
    problemApi.putProblems(id, problemId, obj, loading).then(() => {
      getList()
      MsgSuccess('Changes are Successful')
    })
  } else {
    MsgError('The problem cannot be empty.！')
  }
}

function cellMouseEnter(row: any) {
  currentMouseId.value = row.id
}
function cellMouseLeave() {
  currentMouseId.value = ''
}

/**
 * Next page
 */
const nextChatRecord = () => {
  let index = problemIndexMap.value[currentClickId.value] + 1
  if (index >= problemData.value.length) {
    if (
      index + (paginationConfig.current_page - 1) * paginationConfig.page_size >=
      paginationConfig.total - 1
    ) {
      return
    }
    paginationConfig.current_page = paginationConfig.current_page + 1
    getList().then(() => {
      index = 0
      currentClickId.value = problemData.value[index].id
      currentContent.value = problemData.value[index].content
    })
  } else {
    currentClickId.value = problemData.value[index].id
    currentContent.value = problemData.value[index].content
  }
}
const pre_disable = computed(() => {
  let index = problemIndexMap.value[currentClickId.value] - 1
  return index < 0 && paginationConfig.current_page <= 1
})

const next_disable = computed(() => {
  let index = problemIndexMap.value[currentClickId.value] + 1
  return (
    index >= problemData.value.length &&
    index + (paginationConfig.current_page - 1) * paginationConfig.page_size >=
      paginationConfig.total - 1
  )
})
/**
 * The previous page
 */
const preChatRecord = () => {
  let index = problemIndexMap.value[currentClickId.value] - 1

  if (index < 0) {
    if (paginationConfig.current_page <= 1) {
      return
    }
    paginationConfig.current_page = paginationConfig.current_page - 1
    getList().then((ok) => {
      index = paginationConfig.page_size - 1
      currentClickId.value = problemData.value[index].id
      currentContent.value = problemData.value[index].content
    })
  } else {
    currentClickId.value = problemData.value[index].id
    currentContent.value = problemData.value[index].content
  }
}

function rowClickHandle(row: any) {
  if (row.paragraph_count) {
    currentClickId.value = row.id
    currentContent.value = row.content
    DetailProblemRef.value.open()
  }
}

const setRowClass = ({ row }: any) => {
  return currentClickId.value === row?.id ? 'highlight' : ''
}

function handleSizeChange() {
  paginationConfig.current_page = 1
  getList()
}

function getList() {
  return problem
    .asyncGetProblem(
      id as string,
      paginationConfig,
      filterText.value && { content: filterText.value },
      loading
    )
    .then((res: any) => {
      problemData.value = res.data.records
      paginationConfig.total = res.data.total
    })
}

function refresh() {
  paginationConfig.current_page = 1
  getList()
}

onMounted(() => {
  getList()
})

onBeforeUnmount(() => {})
</script>
<style lang="scss" scoped></style>
