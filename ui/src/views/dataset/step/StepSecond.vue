<template>
  <div class="set-rules">
    <el-row>
      <el-col :span="10" class="p-24">
        <h4 class="title-decoration-1 mb-16">Set the section rules.</h4>
        <div class="set-rules__right">
          <el-scrollbar>
            <div class="left-height" @click.stop>
              <el-radio-group v-model="radio" class="set-rules__radio">
                <el-card shadow="never" class="mb-16" :class="radio === '1' ? 'active' : ''">
                  <el-radio value="1" size="large">
                    <p class="mb-4">Intelligent section.（Recommended)</p>
                    <el-text type="info">I don’t know how to set sections rules recommend using smart sections.</el-text>
                  </el-radio>
                </el-card>
                <el-card shadow="never" class="mb-16" :class="radio === '2' ? 'active' : ''">
                  <el-radio value="2" size="large">
                    <p class="mb-4">The Higher Section</p>
                    <el-text type="info"
                      >Users can set sections identifier themselves according to the document standards.、The length and the cleaning rules.
                    </el-text>
                  </el-radio>

                  <el-card
                    v-if="radio === '2'"
                    shadow="never"
                    class="card-never mt-16"
                    style="margin-left: 30px"
                  >
                    <div class="set-rules__form">
                      <div class="form-item mb-16">
                        <div class="title flex align-center mb-8">
                          <span style="margin-right: 4px">Parts of identification.</span>
                          <el-tooltip
                            effect="dark"
                            content="Divide according to the selected symbol.，The result of the division exceeding the length of the section will be cut to the length of the section.。"
                            placement="right"
                          >
                            <AppIcon iconName="app-warning" class="app-warning-icon"></AppIcon>
                          </el-tooltip>
                        </div>
                        <div @click.stop>
                          <el-select
                            v-model="form.patterns"
                            multiple
                            allow-create
                            default-first-option
                            filterable
                            placeholder="Please choose"
                          >
                            <el-option
                              v-for="(item, index) in splitPatternList"
                              :key="index"
                              :label="item.key"
                              :value="item.value"
                            >
                            </el-option>
                          </el-select>
                        </div>
                      </div>
                      <div class="form-item mb-16">
                        <div class="title mb-8">Part length</div>
                        <el-slider
                          v-model="form.limit"
                          show-input
                          :show-input-controls="false"
                          :min="50"
                          :max="4096"
                        />
                      </div>
                      <div class="form-item mb-16">
                        <div class="title mb-8">Automatic cleaning.</div>
                        <el-switch size="small" v-model="form.with_filter" />
                        <div style="margin-top: 4px">
                          <el-text type="info">Remove repeated excess symbol space.、The empty、The Tabel</el-text>
                        </div>
                      </div>
                    </div>
                  </el-card>
                </el-card>
              </el-radio-group>
            </div>
          </el-scrollbar>
          <div class="text-right">
            <el-button @click="splitDocument">Create a Preview.</el-button>
          </div>
        </div>
      </el-col>

      <el-col :span="14" class="p-24 border-l">
        <div v-loading="loading">
          <h4 class="title-decoration-1 mb-8">Section Preview</h4>
          <ParagraphPreview v-model:data="paragraphList" />
        </div>
      </el-col>
    </el-row>
  </div>
</template>
<script setup lang="ts">
import { ref, computed, onMounted, reactive, watch } from 'vue'
import ParagraphPreview from '@/views/dataset/component/ParagraphPreview.vue'
import documentApi from '@/api/document'
import useStore from '@/stores'
import type { KeyValue } from '@/api/type/common'
const { dataset } = useStore()
const documentsFiles = computed(() => dataset.documentsFiles)
const splitPatternList = ref<Array<KeyValue<string, string>>>([])

const radio = ref('1')
const loading = ref(false)
const paragraphList = ref<any[]>([])
const patternLoading = ref<boolean>(false)

const form = reactive<{
  patterns: Array<string>
  limit: number
  with_filter: boolean
  [propName: string]: any
}>({
  patterns: [],
  limit: 500,
  with_filter: true
})

function splitDocument() {
  loading.value = true
  let fd = new FormData()
  documentsFiles.value.forEach((item) => {
    if (item?.raw) {
      fd.append('file', item?.raw)
    }
  })
  if (radio.value === '2') {
    Object.keys(form).forEach((key) => {
      if (key == 'patterns') {
        form.patterns.forEach((item) => fd.append('patterns', item))
      } else {
        fd.append(key, form[key])
      }
    })
  }
  documentApi
    .postSplitDocument(fd)
    .then((res: any) => {
      paragraphList.value = res.data
      loading.value = false
    })
    .catch(() => {
      loading.value = false
    })
}

const initSplitPatternList = () => {
  documentApi.listSplitPattern(patternLoading).then((ok) => {
    splitPatternList.value = ok.data
  })
}

watch(radio, () => {
  if (radio.value === '2') {
    initSplitPatternList()
  }
})

onMounted(() => {
  splitDocument()
})

defineExpose({
  paragraphList
})
</script>
<style scoped lang="scss">
.set-rules {
  width: 100%;

  .left-height {
    max-height: calc(var(--create-dataset-height) - 70px);
    overflow-x: hidden;
  }

  &__radio {
    width: 100%;
    display: block;

    .el-radio {
      white-space: break-spaces;
      width: 100%;
      height: 100%;
      line-height: 22px;
      color: var(--app-text-color);
    }

    :deep(.el-radio__label) {
      padding-left: 30px;
      width: 100%;
    }
    :deep(.el-radio__input) {
      position: absolute;
      top: 16px;
    }
    .active {
      border: 1px solid var(--el-color-primary);
    }
  }

  &__form {
    .title {
      font-size: 14px;
      font-weight: 400;
    }
  }
}
</style>
