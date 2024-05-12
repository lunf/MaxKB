<template>
  <LayoutContainer :header="documentDetail?.name" back-to="-1" class="document-detail">
    <template #header>
      <el-text type="info" v-if="documentDetail?.type === '1'"
        >（The document address.：<el-link :href="documentDetail?.meta?.source_url" target="_blank">{{
          documentDetail?.meta?.source_url
        }}</el-link
        >）</el-text
      >
      <div class="document-detail__header">
        <el-button @click="addParagraph" type="primary" :disabled="loading"> Adding sections. </el-button>
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
                <CardBox
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
                      <span> {{ numberFormat(item?.content.length) || 0 }} one The characters </span>
                      <el-tooltip effect="dark" content="removed" placement="top">
                        <el-button text @click.stop="deleteParagraph(item)" class="delete-button">
                          <el-icon><Delete /></el-icon>
                        </el-button>
                      </el-tooltip>
                    </div>
                  </template>
                </CardBox>
              </el-col>
            </el-row>
          </InfiniteScroll>
        </div>
      </el-scrollbar>
    </div>
    <ParagraphDialog ref="ParagraphDialogRef" :title="title" @refresh="refresh" />
  </LayoutContainer>
</template>
<script setup lang="ts">
import { reactive, ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import documentApi from '@/api/document'
import paragraphApi from '@/api/paragraph'
import ParagraphDialog from './component/ParagraphDialog.vue'
import { numberFormat } from '@/utils/utils'
import { MsgSuccess, MsgConfirm } from '@/utils/message'
import useStore from '@/stores'
const { paragraph } = useStore()
const route = useRoute()
const {
  params: { id, documentId }
} = route as any

const ParagraphDialogRef = ref()
const loading = ref(false)
const changeStateloading = ref(false)
const documentDetail = ref<any>({})
const paragraphDetail = ref<any[]>([])
const title = ref('')
const search = ref('')
const searchType = ref('title')

const paginationConfig = reactive({
  current_page: 1,
  page_size: 20,
  total: 0
})

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
  MsgConfirm(`Remove the paragraph.：${row.title || '-'} ?`, `It cannot be restored after deletion.，Please be careful.。`, {
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
}
</style>
