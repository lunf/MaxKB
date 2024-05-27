<template>
  <LayoutContainer
    :header="id ? 'set up' : 'Creating Applications'"
    :back-to="id ? '' : '-1'"
    class="create-application"
  >
    <el-row v-loading="loading">
      <el-col :span="10">
        <div class="p-24 mb-16" style="padding-bottom: 0">
          <h4 class="title-decoration-1">Application of information</h4>
        </div>
        <div class="scrollbar-height-left">
          <el-scrollbar>
            <el-form
              hide-required-asterisk
              ref="applicationFormRef"
              :model="applicationForm"
              :rules="rules"
              label-position="top"
              require-asterisk-position="right"
              class="p-24"
              style="padding-top: 0"
            >
              <el-form-item prop="name">
                <template #label>
                  <div class="flex-between">
                    <span>Application Name <span class="danger">*</span></span>
                  </div>
                </template>
                <el-input
                  v-model="applicationForm.name"
                  maxlength="64"
                  placeholder="Please enter the application name."
                  show-word-limit
                />
              </el-form-item>
              <el-form-item label="Application Description">
                <el-input
                  v-model="applicationForm.desc"
                  type="textarea"
                  placeholder="Description of the application scenes and purposes，as：MaxKB The assistant responds to the user’s proposed MaxKB Problems with product use"
                  :rows="3"
                  maxlength="256"
                  show-word-limit
                />
              </el-form-item>

              <el-form-item label="AI The model" prop="model_id">
                <template #label>
                  <div class="flex-between">
                    <span>AI The model </span>
                  </div>
                </template>
                <el-select
                  v-model="applicationForm.model_id"
                  placeholder="Please choose AI The model"
                  class="w-full"
                  popper-class="select-model"
                  :clearable="true"
                >
                  <el-option-group
                    v-for="(value, label) in modelOptions"
                    :key="value"
                    :label="relatedObject(providerOptions, label, 'provider')?.name"
                  >
                    <el-option
                      v-for="item in value.filter((v: any) => v.status === 'SUCCESS')"
                      :key="item.id"
                      :label="item.name"
                      :value="item.id"
                      class="flex-between"
                    >
                      <div class="flex">
                        <span
                          v-html="relatedObject(providerOptions, label, 'provider')?.icon"
                          class="model-icon mr-8"
                        ></span>
                        <span>{{ item.name }}</span>
                      </div>
                      <el-icon class="check-icon" v-if="item.id === applicationForm.model_id"
                        ><Check
                      /></el-icon>
                    </el-option>
                    <!-- Unusable -->
                    <el-option
                      v-for="item in value.filter((v: any) => v.status !== 'SUCCESS')"
                      :key="item.id"
                      :label="item.name"
                      :value="item.id"
                      class="flex-between"
                      disabled
                    >
                      <div class="flex">
                        <span
                          v-html="relatedObject(providerOptions, label, 'provider')?.icon"
                          class="model-icon mr-8"
                        ></span>
                        <span>{{ item.name }}</span>
                        <span class="danger">（Unusable）</span>
                      </div>
                      <el-icon class="check-icon" v-if="item.id === applicationForm.model_id"
                        ><Check
                      /></el-icon>
                    </el-option>
                  </el-option-group>
                  <template #footer>
                    <div class="w-full text-left cursor" @click="openCreateModel()">
                      <el-button type="primary" link>
                        <el-icon class="mr-4"><Plus /></el-icon> Adding the model.
                      </el-button>
                    </div>
                  </template>
                </el-select>
              </el-form-item>
              <el-form-item label="Suggestions" prop="model_setting.prompt">
                <template #label>
                  <div class="flex align-center">
                    <div class="flex-between mr-4">
                      <span>Suggestions <span class="danger">*</span></span>
                    </div>
                    <el-tooltip effect="dark" placement="right">
                      <template #content
                        >By adjusting the words.，You can guide the big model chat direction.，The tip word will be fixed at the beginning of the above.。<br />You can use the variable.：{data}
                        carrying information in the knowledge base.；{question}Questions Asked by Users。</template
                      >
                      <AppIcon iconName="app-warning" class="app-warning-icon"></AppIcon>
                    </el-tooltip>
                  </div>
                </template>
                <el-input
                  v-model="applicationForm.model_setting.prompt"
                  :rows="6"
                  type="textarea"
                  maxlength="2048"
                  :placeholder="defaultPrompt"
                />
              </el-form-item>
              <el-form-item label="multiple rounds of dialogue." @click.prevent>
                <el-switch
                  size="small"
                  v-model="applicationForm.multiple_rounds_dialogue"
                ></el-switch>
              </el-form-item>
              <el-form-item label="The Knowledge Base">
                <template #label>
                  <div class="flex-between">
                    <span>The Knowledge Base</span>
                    <div>
                      <el-button type="primary" link @click="openParamSettingDialog">
                        <AppIcon iconName="app-operation" class="mr-4"></AppIcon>The parameter set.
                      </el-button>
                      <el-button type="primary" link @click="openDatasetDialog">
                        <el-icon class="mr-4"><Plus /></el-icon>Added
                      </el-button>
                    </div>
                  </div>
                </template>
                <div class="w-full">
                  <el-text type="info" v-if="applicationForm.dataset_id_list?.length === 0"
                    >Related Knowledge Base Show here.</el-text
                  >
                  <el-row :gutter="12" v-else>
                    <el-col
                      :xs="24"
                      :sm="24"
                      :md="24"
                      :lg="12"
                      :xl="12"
                      class="mb-8"
                      v-for="(item, index) in applicationForm.dataset_id_list"
                      :key="index"
                    >
                      <el-card class="relate-dataset-card" shadow="never">
                        <div class="flex-between">
                          <div class="flex align-center">
                            <AppAvatar
                              v-if="relatedObject(datasetList, item, 'id')?.type === '1'"
                              class="mr-8 avatar-purple"
                              shape="square"
                              :size="32"
                            >
                              <img src="@/assets/icon_web.svg" style="width: 58%" alt="" />
                            </AppAvatar>

                            <AppAvatar v-else class="mr-12" shape="square" :size="32">
                              <img src="@/assets/icon_document.svg" style="width: 58%" alt="" />
                            </AppAvatar>
                            <div class="ellipsis">
                              {{ relatedObject(datasetList, item, 'id')?.name }}
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
              <el-form-item label="Opening White.">
                <MdEditor
                  class="prologue-md-editor"
                  v-model="applicationForm.prologue"
                  :preview="false"
                  :toolbars="[]"
                  :footers="[]"
                />
              </el-form-item>
              <el-form-item @click.prevent>
                <template #label>
                  <div class="flex align-center">
                    <span class="mr-4">Problems optimized</span>
                    <el-tooltip
                      effect="dark"
                      content="Optimization of current issues based on history chat，It is better to match knowledge.。"
                      placement="right"
                    >
                      <AppIcon iconName="app-warning" class="app-warning-icon"></AppIcon>
                    </el-tooltip>
                  </div>
                </template>
                <el-switch size="small" v-model="applicationForm.problem_optimization"></el-switch>
              </el-form-item>
            </el-form>
          </el-scrollbar>
        </div>
        <div class="text-right border-t p-16">
          <el-button v-if="!id" @click="router.push({ path: `/application` })"> cancelled </el-button>
          <el-button type="primary" @click="submit(applicationFormRef)" :disabled="loading">
            {{ id ? 'Save' : 'Create' }}
          </el-button>
        </div>
      </el-col>
      <el-col :span="14" class="p-24 border-l">
        <h4 class="title-decoration-1 mb-16">The Preview.</h4>
        <div class="dialog-bg">
          <h4 class="p-24">{{ applicationForm?.name || 'Application Name' }}</h4>
          <div class="scrollbar-height">
            <AiChat :data="applicationForm"></AiChat>
          </div>
        </div>
      </el-col>
    </el-row>

    <ParamSettingDialog ref="ParamSettingDialogRef" @refresh="refreshParam" />
    <AddDatasetDialog
      ref="AddDatasetDialogRef"
      @addData="addDataset"
      :data="datasetList"
      @refresh="refresh"
      :loading="datasetLoading"
    />

    <!-- Added Models -->
    <CreateModelDialog
      ref="createModelRef"
      @submit="getModel"
      @change="openCreateModel($event)"
    ></CreateModelDialog>
    <SelectProviderDialog ref="selectProviderRef" @change="openCreateModel($event)" />
  </LayoutContainer>
</template>
<script setup lang="ts">
import { reactive, ref, watch, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { groupBy } from 'lodash'
import ParamSettingDialog from './components/ParamSettingDialog.vue'
import AddDatasetDialog from './components/AddDatasetDialog.vue'
import CreateModelDialog from '@/views/template/component/CreateModelDialog.vue'
import SelectProviderDialog from '@/views/template/component/SelectProviderDialog.vue'
import { MdEditor } from 'md-editor-v3'
import applicationApi from '@/api/application'
import type { FormInstance, FormRules } from 'element-plus'
import type { ApplicationFormType } from '@/api/type/application'
import type { Provider } from '@/api/type/model'
import { relatedObject } from '@/utils/utils'
import { MsgSuccess } from '@/utils/message'
import useStore from '@/stores'

const { model, dataset, application, user } = useStore()

const router = useRouter()
const route = useRoute()
const {
  params: { id }
} = route as any

const defaultPrompt = `known information：
{data}
Reply to Request：
- Use a simple and professional language to answer user questions.。
- If you do not know the answer.，Please answer“No information found in the knowledge base.，Consulting relevant technical support or reference to official documents for operation”。
- Avoid mentioning the knowledge you gain from known information.。
- Please make sure the answer is consistent with the information described in the information.。
- Please use Markdown Optimization of Answer Formats。
- Images in known information.、Link address and script language please return directly。
- Please use the same language to answer the question.。
The problem：
{question}
`

const ParamSettingDialogRef = ref<InstanceType<typeof ParamSettingDialog>>()
const createModelRef = ref<InstanceType<typeof CreateModelDialog>>()
const selectProviderRef = ref<InstanceType<typeof SelectProviderDialog>>()

const applicationFormRef = ref<FormInstance>()
const AddDatasetDialogRef = ref()

const loading = ref(false)
const datasetLoading = ref(false)
const applicationForm = ref<ApplicationFormType>({
  name: '',
  desc: '',
  model_id: '',
  multiple_rounds_dialogue: false,
  prologue: `Hello to，I am MaxKB The Little Assistant，You can present to me. MaxKB Use of Problems。
- MaxKB What are the main functions?？
- MaxKB What major language models are supported？
- MaxKB What types of documents are supported？`,
  dataset_id_list: [],
  dataset_setting: {
    top_n: 3,
    similarity: 0.6,
    max_paragraph_char_number: 5000,
    search_mode: 'embedding',
    no_references_setting: {
      status: 'ai_questioning',
      value: '{question}'
    }
  },
  model_setting: {
    prompt: defaultPrompt
  },
  problem_optimization: false
})

const rules = reactive<FormRules<ApplicationFormType>>({
  name: [{ required: true, message: 'Please enter the application name.', trigger: 'blur' }],
  model_id: [
    {
      required: false,
      message: 'Please select the model.',
      trigger: 'change'
    }
  ],
  'model_setting.prompt': [{ required: true, message: 'Please enter the instructions.', trigger: 'blur' }]
})
const modelOptions = ref<any>(null)
const providerOptions = ref<Array<Provider>>([])
const datasetList = ref([])

const submit = async (formEl: FormInstance | undefined) => {
  if (!formEl) return
  await formEl.validate((valid, fields) => {
    if (valid) {
      if (id) {
        application.asyncPutApplication(id, applicationForm.value, loading).then((res) => {
          MsgSuccess('Updating success.')
        })
      } else {
        applicationApi.postApplication(applicationForm.value, loading).then((res) => {
          MsgSuccess('Creating Success')
          router.push({ path: `/application` })
        })
      }
    }
  })
}

const openParamSettingDialog = () => {
  ParamSettingDialogRef.value?.open(applicationForm.value.dataset_setting)
}

function refreshParam(data: any) {
  applicationForm.value.dataset_setting = data
}

const openCreateModel = (provider?: Provider) => {
  if (provider && provider.provider) {
    createModelRef.value?.open(provider)
  } else {
    selectProviderRef.value?.open()
  }
}

function removeDataset(id: any) {
  if (applicationForm.value.dataset_id_list) {
    applicationForm.value.dataset_id_list.splice(
      applicationForm.value.dataset_id_list.indexOf(id),
      1
    )
  }
}
function addDataset(val: Array<string>) {
  applicationForm.value.dataset_id_list = val
}
function openDatasetDialog() {
  AddDatasetDialogRef.value.open(applicationForm.value.dataset_id_list)
}

function getDetail() {
  application.asyncGetApplicationDetail(id, loading).then((res: any) => {
    applicationForm.value = res.data
    applicationForm.value.model_id = res.data.model
  })
}

function getDataset() {
  if (id) {
    application.asyncGetApplicationDataset(id, datasetLoading).then((res: any) => {
      datasetList.value = res.data
    })
  } else {
    dataset.asyncGetAllDataset(datasetLoading).then((res: any) => {
      datasetList.value = res.data?.filter((v: any) => v.user_id === user.userInfo?.id)
    })
  }
}

function getModel() {
  loading.value = true
  if (id) {
    applicationApi
      .getApplicationModel(id)
      .then((res: any) => {
        modelOptions.value = groupBy(res?.data, 'provider')
        loading.value = false
      })
      .catch(() => {
        loading.value = false
      })
  } else {
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

function refresh() {
  getDataset()
}

onMounted(() => {
  getProvider()
  getModel()
  getDataset()
  if (id) {
    getDetail()
  }
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
.prologue-md-editor {
  height: 150px;
}
</style>
