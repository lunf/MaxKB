<template>
  <LayoutContainer :header="id ? '设置' : '创建应用'" back-to="-1" class="create-application">
    <el-row>
      <el-col :span="10">
        <div class="p-24 mb-16" style="padding-bottom: 0">
          <h4 class="title-decoration-1">应用信息</h4>
        </div>
        <div class="scrollbar-height-left">
          <el-scrollbar>
            <el-form
              ref="applicationFormRef"
              :model="applicationForm"
              :rules="rules"
              label-position="top"
              require-asterisk-position="right"
              class="p-24"
              style="padding-top: 0"
            >
              <el-form-item label="应用名称" prop="name">
                <el-input
                  v-model="applicationForm.name"
                  maxlength="64"
                  placeholder="请输入应用名称"
                  show-word-limit
                />
              </el-form-item>
              <el-form-item label="应用描述">
                <el-input
                  v-model="applicationForm.desc"
                  type="textarea"
                  placeholder="描述该应用的应用场景及用途，如：MaxKB 小助手回答用户提出的 MaxKB 产品使用问题"
                  :rows="3"
                  maxlength="500"
                  show-word-limit
                />
              </el-form-item>
              <el-form-item label="选择模型" prop="model_id">
                <el-select
                  v-model="applicationForm.model_id"
                  placeholder="请选择模型"
                  style="width: 100%"
                >
                  <el-option-group
                    v-for="(value, label) in modelOptions"
                    :key="value"
                    :label="realatedObject(providerOptions, label, 'provider')?.name"
                  >
                    <el-option
                      v-for="item in value"
                      :key="item.id"
                      :label="item.name"
                      :value="item.id"
                      class="flex-between"
                    >
                      <div class="flex">
                        <span
                          v-html="realatedObject(providerOptions, label, 'provider')?.icon"
                          class="model-icon mr-8"
                        ></span>
                        <span>{{ item.name }}</span>
                      </div>
                      <el-icon class="check-icon" v-if="item.id === applicationForm.model_id"
                        ><Check
                      /></el-icon>
                    </el-option>
                  </el-option-group>
                  <div class="border-t" style="padding: 8px 11px">
                    <el-button type="primary" link>
                      <el-icon class="mr-4"><Plus /></el-icon> 添加模型
                    </el-button>
                  </div>
                </el-select>
              </el-form-item>

              <el-form-item label="多轮对话" @click.prevent>
                <el-switch v-model="applicationForm.multiple_rounds_dialogue"></el-switch>
              </el-form-item>
              <el-form-item label="关联数据集">
                <template #label>
                  <div class="flex-between">
                    <span>关联数据集</span>
                    <el-button type="primary" link @click="openDatasetDialog">
                      <el-icon class="mr-4"><Plus /></el-icon> 添加
                    </el-button>
                  </div>
                </template>
                <div v-if="applicationForm.dataset_id_list.length == 0">
                  <el-text type="info">关联的数据集展示在这里</el-text>
                </div>
                <div class="w-full" v-else>
                  <el-row :gutter="12">
                    <el-col
                      :xs="24"
                      :sm="24"
                      :md="12"
                      :lg="12"
                      :xl="12"
                      class="mb-8"
                      v-for="(item, index) in applicationForm.dataset_id_list"
                      :key="index"
                    >
                      <el-card class="relate-dataset-card" shadow="never">
                        <div class="flex-between">
                          <div class="flex align-center">
                            <AppAvatar class="mr-12" shape="square" :size="32">
                              <img src="@/assets/icon_document.svg" style="width: 58%" alt="" />
                            </AppAvatar>
                            <div class="ellipsis-1">
                              {{ realatedObject(datasetList, item, 'id')?.name }}
                            </div>
                          </div>
                          <el-button text @click="removeDataset(item)">
                            <el-icon><Close /></el-icon>
                          </el-button>
                        </div>
                      </el-card>
                    </el-col>
                  </el-row>
                </div>
              </el-form-item>
              <el-form-item label="开场白">
                <el-input
                  v-model="applicationForm.prologue"
                  type="textarea"
                  placeholder="开始对话的欢迎语。您可以这样写：您好，我是 MaxKB 智能小助手，您可以向我提出 MaxKB 产品使用中遇到的任何问题。"
                  :rows="4"
                />
              </el-form-item>
              <el-form-item label="示例">
                <template v-for="(item, index) in exampleList" :key="index">
                  <el-input
                    v-model="exampleList[index]"
                    :placeholder="`用户提问 示例${index + 1}`"
                    class="mb-8"
                  />
                </template>
              </el-form-item>
            </el-form>
          </el-scrollbar>
        </div>
        <div class="text-right border-t p-16">
          <el-button @click="router.push({ path: `/application` })"> 取消 </el-button>
          <el-button type="primary" @click="submit" :disabled="loading"> 创建 </el-button>
        </div>
      </el-col>
      <el-col :span="14" class="p-24 border-l">
        <h4 class="title-decoration-1 mb-16">调试预览</h4>
        <div class="dialog-bg">
          <h4 class="p-24">{{ applicationForm?.name || '应用名称' }}</h4>
          <div class="scrollbar-height">
            <AiDialog :data="applicationForm"></AiDialog>
          </div>
        </div>
      </el-col>
    </el-row>
    <AddDatasetDialog ref="AddDatasetDialogRef" @addData="addDataset" :data="datasetList" />
  </LayoutContainer>
</template>
<script setup lang="ts">
import { reactive, ref, watch, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { groupBy } from 'lodash'
import AiDialog from '@/components/ai-dialog/index.vue'
import AddDatasetDialog from './components/AddDatasetDialog.vue'
import type { FormInstance, FormRules } from 'element-plus'
import type { ApplicationFormType } from '@/api/type/application'
import type { Provider } from '@/api/type/model'
import { realatedObject } from '@/utils/utils'
import useStore from '@/stores'
const { model, dataset } = useStore()

const router = useRouter()
const route = useRoute()
const {
  params: { id }
} = route as any

const applicationFormRef = ref<FormInstance>()
const AddDatasetDialogRef = ref()

const loading = ref(false)
const exampleList = ref(['', ''])
const applicationForm = reactive<ApplicationFormType>({
  name: '',
  desc: '',
  model_id: '',
  multiple_rounds_dialogue: false,
  prologue: '',
  example: [],
  dataset_id_list: []
})

const rules = reactive<FormRules<ApplicationFormType>>({
  name: [{ required: true, message: '请输入应用名称', trigger: 'blur' }],
  model_id: [
    {
      required: true,
      message: '请选择模型',
      trigger: 'change'
    }
  ]
})
const modelOptions = ref<any>(null)
const providerOptions = ref<Array<Provider>>([])
const datasetList = ref([])

watch(exampleList.value, () => {
  applicationForm.example = exampleList.value.filter((v) => v)
})

function submit() {
  loading.value = true

  // const documents = [] as any[]
  // StepSecondRef.value.paragraphList.map((item: any) => {
  //   documents.push({
  //     name: item.name,
  //     paragraphs: item.content
  //   })
  // })
  // const obj = { ...baseInfo.value, documents } as datasetData
  // if (id) {
  //   documentApi
  //     .postDocument(id, documents)
  //     .then((res) => {
  //       MsgSuccess('提交成功')
  //       clearStore()
  //       router.push({ path: `/dataset/${id}/document` })
  //     })
  //     .catch(() => {
  //       loading.value = false
  //     })
  // } else {
  //   datasetApi
  //     .postDateset(obj)
  //     .then((res) => {
  //       successInfo.value = res.data
  //       active.value = 2
  //       clearStore()
  //       loading.value = false
  //     })
  //     .catch(() => {
  //       loading.value = false
  //     })
  // }
}

function removeDataset(id: String) {
  applicationForm.dataset_id_list.splice(applicationForm.dataset_id_list.indexOf(id), 1)
}
function addDataset(val: Array<string>) {
  applicationForm.dataset_id_list = val
}
function openDatasetDialog() {
  AddDatasetDialogRef.value.open(applicationForm.dataset_id_list)
}

function getDataset() {
  loading.value = true
  dataset
    .asyncGetAllDateset()
    .then((res: any) => {
      datasetList.value = res.data
      loading.value = false
    })
    .catch(() => {
      loading.value = false
    })
}

function getModel() {
  loading.value = true
  model
    .asyncGetModel()
    .then((res: any) => {
      modelOptions.value = groupBy(res?.data, 'provider')
      loading.value = false
    })
    .catch(() => {
      loading.value = false
    })
}

function getProvider() {
  loading.value = true
  model
    .asyncGetProvider()
    .then((res: any) => {
      providerOptions.value = res?.data
      loading.value = false
    })
    .catch(() => {
      loading.value = false
    })
}

onMounted(() => {
  getProvider()
  getModel()
  getDataset()
})
</script>
<style lang="scss" scoped>
.create-application {
  .relate-dataset-card {
    color: var(--app-text-color);
    border-radius: 4px;
  }
  .dialog-bg {
    border-radius: 8px;
    background: var(--dialog-bg-gradient-color);
    overflow: hidden;
    box-sizing: border-box;
  }
  .scrollbar-height-left {
    height: calc(var(--app-main-height) - 127px);
  }
  .scrollbar-height {
    height: calc(var(--app-main-height) - 150px);
  }
}
.model-icon {
  width: 20px;
}
.check-icon {
  position: absolute;
  right: 10px;
}
</style>