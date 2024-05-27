<template>
  <LayoutContainer :header="documentDetail?.name" back-to="-1" class="document-detail">
    <template #header>
      <el-text type="info" v-if="documentDetail?.type === '1'"
        >(The document address :<el-link :href="documentDetail?.meta?.source_url" target="_blank">{{
          documentDetail?.meta?.source_url
        }}</el-link
        >)</el-text
      >
      <div class="document-detail__header">
        <el-button @click="batchSelectedHandle(true)" v-if="isBatch === false">
          Bulk selection
        </el-button>
        <el-button @click="batchSelectedHandle(false)" v-if="isBatch === true">
          Cancel selection
        </el-button>
        <el-button
          @click="addParagraph"
          type="primary"
          :disabled="loading"
          v-if="isBatch === false"
        >
          Add segment
        </el-button>
      </div>
    </template>
    <div
      class="document-detail__main p-16"
      v-loading="(paginationConfig.current_page === 1 && loading) || changeStateloading"
    >
      <div class="flex-between p-8">
        <span>{{ paginationConfig.total }} Paragraphs</span>
        <el-input
          v-model="search"
          placeholder="Searching"
          class="input-with-select"
          style="width: 260px"
          @change="searchHandle"
          clearable
        >
          <template #prepend>
            <el-select v-model="searchType" placeholder="Select" style="width: 80px">
              <el-option label="The title" value="title" />
              <el-option label="The content" value="content" />
            </el-select>
          </template>
        </el-input>
      </div>
      <el-scrollbar>
        <div class="document-detail-height">
          <el-empty v-if="paragraphDetail.length == 0" description="No data" />

          <InfiniteScroll
            v-else
            :size="paragraphDetail.length"
            :total="paginationConfig.total"
            :page_size="paginationConfig.page_size"
            v-model:current_page="paginationConfig.current_page"
            @load="getParagraphList"
            :loading="loading"
          >
            <el-row>
              <el-col
                :xs="24"
                :sm="12"
                :md="8"
                :lg="6"
                :xl="6"
                v-for="(item, index) in paragraphDetail"
                :key="index"
                class="p-8"
              >
                <!-- Batch operation card -->
                <CardBox
                  v-if="isBatch === true"
                  shadow="hover"
                  :title="item.title || '-'"
                  :description="item.content"
                  class="document-card cursor"
                  :class="multipleSelection.includes(item.id) ? 'selected' : ''"
                  :showIcon="false"
                  @click="selectHandle(item.id)"
                >
                  <div class="active-button" @click.stop></div>

                  <template #footer>
                    <div class="footer-content flex-between">
                      <span> {{ numberFormat(item?.content.length) || 0 }} 个 字符 </span>
                    </div>
                  </template>
                </CardBox>
                <!-- Non-batch operation card -->
                <CardBox
                  v-else
                  shadow="hover"
                  :title="item.title || '-'"
                  :description="item.content"
                  class="document-card cursor"
                  :class="item.is_active ? '' : 'disabled'"
                  :showIcon="false"
                  @click="editParagraph(item)"
                >
                  <div class="active-button" @click.stop>
                    <el-switch
                      v-model="item.is_active"
                      @change="changeState($event, item)"
                      size="small"
                    />
                  </div>

                  <template #footer>
                    <div class="footer-content flex-between">
                      <span> {{ numberFormat(item?.content.length) || 0 }} characters </span>

                      <span @click.stop>
                        <el-dropdown trigger="click">
                          <el-button text>
                            <el-icon><MoreFilled /></el-icon>
                          </el-button>
                          <template #dropdown>
                            <el-dropdown-menu>
                              <el-dropdown-item @click="openSelectDocumentDialog(item)">
                                <AppIcon iconName="app-migrate"></AppIcon>
                                Migrate</el-dropdown-item
                              >
                              <el-dropdown-item icon="Delete" @click.stop="deleteParagraph(item)"
                                >Delete</el-dropdown-item
                              >
                            </el-dropdown-menu>
                          </template>
                        </el-dropdown>
                      </span>
                    </div>
                  </template>
                </CardBox>
              </el-col>
            </el-row>
          </InfiniteScroll>
        </div>
      </el-scrollbar>

      <div class="mul-operation border-t w-full" v-if="isBatch === true">
        <el-button :disabled="multipleSelection.length === 0" @click="openSelectDocumentDialog()">
          Migrate
        </el-button>

        <el-button :disabled="multipleSelection.length === 0" @click="deleteMulParagraph">
          Delete
        </el-button>
        <span class="ml-8"> 已选 {{ multipleSelection.length }} 项 </span>
      </div>
    </div>
    <ParagraphDialog ref="ParagraphDialogRef" :title="title" @refresh="refresh" />
    <SelectDocumentDialog ref="SelectDocumentDialogRef" @refresh="refreshMigrateParagraph" />
  </LayoutContainer>
</template>
<script setup lang="ts">
import { reactive, ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import documentApi from '@/api/document'
import paragraphApi from '@/api/paragraph'
import ParagraphDialog from './component/ParagraphDialog.vue'
import SelectDocumentDialog from './component/SelectDocumentDialog.vue'
import { numberFormat } from '@/utils/utils'
import { MsgSuccess, MsgConfirm } from '@/utils/message'
import useStore from '@/stores'
const { paragraph } = useStore()
const route = useRoute()
const {
  params: { id, documentId }
} = route as any

const SelectDocumentDialogRef = ref()
const ParagraphDialogRef = ref()
const loading = ref(false)
const changeStateloading = ref(false)
const documentDetail = ref<any>({})
const paragraphDetail = ref<any[]>([])
const title = ref('')
const search = ref('')
const searchType = ref('title')

// 批量操作
const isBatch = ref(false)
const multipleSelection = ref<any[]>([])

const paginationConfig = reactive({
  current_page: 1,
  page_size: 20,
  total: 0
})

function refreshMigrateParagraph() {
  paragraphDetail.value = paragraphDetail.value.filter(
    (v) => !multipleSelection.value.includes(v.id)
  )
  multipleSelection.value = []
  MsgSuccess('Migration and deletion successful')
}

function openSelectDocumentDialog(row?: any) {
  if (row) {
    multipleSelection.value = [row.id]
  }
  SelectDocumentDialogRef.value.open(multipleSelection.value)
}
function deleteMulParagraph() {
  MsgConfirm(
    `Delete ${multipleSelection.value.length} segments in batches?`,
    `It cannot be recovered after deletion, please operate with caution. `,
    {
      confirmButtonText: 'Delete',
      confirmButtonClass: 'danger'
    }
  )
    .then(() => {
      paragraphApi
        .delMulParagraph(id, documentId, multipleSelection.value, changeStateloading)
        .then(() => {
          paragraphDetail.value = paragraphDetail.value.filter(
            (v) => !multipleSelection.value.includes(v.id)
          )
          multipleSelection.value = []
          MsgSuccess('Batch deletion successful')
        })
    })
    .catch(() => {})
}

function batchSelectedHandle(bool: boolean) {
  isBatch.value = bool
  multipleSelection.value = []
}

function selectHandle(id: string) {
  if (multipleSelection.value.includes(id)) {
    multipleSelection.value.splice(multipleSelection.value.indexOf(id), 1)
  } else {
    multipleSelection.value.push(id)
  }
}

function searchHandle() {
  paginationConfig.current_page = 1
  paragraphDetail.value = []
  getParagraphList()
}

function changeState(bool: Boolean, row: any) {
  const obj = {
    is_active: bool
  }
  paragraph.asyncPutParagraph(id, documentId, row.id, obj, changeStateloading).then((res) => {})
}

function deleteParagraph(row: any) {
  MsgConfirm(`Remove the paragraph. ${row.title || '-'} ?`, `It cannot be restored after deletion. Please be careful. `, {
    confirmButtonText: 'removed',
    confirmButtonClass: 'danger'
  })
    .then(() => {
      paragraph.asyncDelParagraph(id, documentId, row.id, loading).then(() => {
        const index = paragraphDetail.value.findIndex((v) => v.id === row.id)
        paragraphDetail.value.splice(index, 1)
        MsgSuccess('Remove Success')
      })
    })
    .catch(() => {})
}

function addParagraph() {
  title.value = 'Adding sections.'
  ParagraphDialogRef.value.open()
}
function editParagraph(row: any) {
  title.value = 'Section Details'
  ParagraphDialogRef.value.open(row)
}

function getDetail() {
  loading.value = true
  documentApi
    .getDocumentDetail(id, documentId)
    .then((res) => {
      documentDetail.value = res.data
      loading.value = false
    })
    .catch(() => {
      loading.value = false
    })
}

function getParagraphList() {
  paragraphApi
    .getParagraph(
      id,
      documentId,
      paginationConfig,
      search.value && { [searchType.value]: search.value },
      loading
    )
    .then((res) => {
      paragraphDetail.value = [...paragraphDetail.value, ...res.data.records]
      paginationConfig.total = res.data.total
    })
}

function refresh(data: any) {
  if (data) {
    const index = paragraphDetail.value.findIndex((v) => v.id === data.id)
    paragraphDetail.value.splice(index, 1, data)
  } else {
    paginationConfig.current_page = 1
    paragraphDetail.value = []
    getParagraphList()
  }
}

onMounted(() => {
  getDetail()
  getParagraphList()
})
</script>
<style lang="scss" scoped>
.document-detail {
  &__header {
    position: absolute;
    right: calc(var(--app-base-px) * 3);
  }

  .document-detail-height {
    height: calc(var(--app-main-height) - 75px);
  }
  .document-card {
    height: 210px;
    background: var(--app-layout-bg-color);
    border: 1px solid var(--app-layout-bg-color);
    &.selected {
      background: #ffffff;
      &:hover {
        background: #ffffff;
      }
    }
    &:hover {
      background: #ffffff;
      border: 1px solid var(--el-border-color);
    }
    &.disabled {
      background: var(--app-layout-bg-color);
      border: 1px solid var(--app-layout-bg-color);
      :deep(.description) {
        color: var(--app-border-color-dark);
      }
      :deep(.title) {
        color: var(--app-border-color-dark);
      }
    }
    :deep(.content) {
      -webkit-line-clamp: 5 !important;
      height: 110px !important;
    }
    .active-button {
      position: absolute;
      right: 16px;
      top: 16px;
    }
  }

  &__main {
    position: relative;
    box-sizing: border-box;
    .mul-operation {
      position: absolute;
      bottom: 0;
      left: 0;
      padding: 16px 24px;
      box-sizing: border-box;
      background: #ffffff;
    }
  }
}
</style>
