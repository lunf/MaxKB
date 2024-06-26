<template>
  <el-dialog
    v-model="dialogVisible"
    width="600px"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    :destroy-on-close="true"
    :before-close="close"
  >
    <template #header="{ close, titleId, titleClass }">
      <el-breadcrumb separator=">">
        <el-breadcrumb-item
          ><span class="active-breadcrumb">{{
            `The Editor ${providerValue?.name}`
          }}</span></el-breadcrumb-item
        >
      </el-breadcrumb>
    </template>

    <DynamicsForm
      v-loading="formLoading"
      v-model="form_data"
      :render_data="model_form_field"
      :model="form_data"
      ref="dynamicsFormRef"
      label-position="top"
      require-asterisk-position="right"
    >
      <template #default>
        <el-form-item prop="name" :rules="base_form_data_rule.name">
          <template #label>
            <div class="flex align-center" style="display: inline-flex">
              <div class="flex-between mr-4">
                <span>Name of model </span>
              </div>
              <el-tooltip effect="dark" placement="right">
                <template #content>
                  <p>MaxKB Customized Model Name</p>
                </template>
                <AppIcon iconName="app-warning" class="app-warning-icon"></AppIcon>
              </el-tooltip>
            </div>
          </template>
          <el-input
            v-model="base_form_data.name"
            maxlength="20"
            show-word-limit
            placeholder="Please set a name for the basic model."
          />
        </el-form-item>
        <el-form-item prop="model_type" :rules="base_form_data_rule.model_type">
          <template #label>
            <span>Type of Model</span>
          </template>
          <el-select
            v-loading="model_type_loading"
            @change="list_base_model($event)"
            v-model="base_form_data.model_type"
            class="w-full m-2"
            placeholder="Please select the model type."
          >
            <el-option
              v-for="item in model_type_list"
              :key="item.value"
              :label="item.key"
              :value="item.value"
            ></el-option>
          </el-select>
        </el-form-item>
        <el-form-item prop="model_name" :rules="base_form_data_rule.model_name">
          <template #label>
            <div class="flex align-center" style="display: inline-flex">
              <div class="flex-between mr-4">
                <span>The Basic Model </span>
              </div>
              <el-tooltip effect="dark" placement="right">
                <template #content>
                  <p>If the download option does not list what you want to add.LLMThe model, Customize the input model name after returning to the car.</p>
                  <p>Attention, The basic model needs to match the model name of the supplier.</p>
                </template>
                <AppIcon iconName="app-warning" class="app-warning-icon"></AppIcon>
              </el-tooltip>
            </div>
          </template>
          <el-select
            @change="getModelForm($event)"
            v-loading="base_model_loading"
            v-model="base_form_data.model_name"
            class="w-full m-2"
            placeholder="Please select the basic model."
            filterable
            allow-create
            default-first-option
          >
            <el-option v-for="item in base_model_list" :key="item.name" :value="item.name">
              <template #default>
                <div class="flex align-center" style="display: inline-flex">
                  <div class="flex-between mr-4">
                    <span>{{ item.name }} </span>
                  </div>
                  <el-tooltip effect="dark" placement="right" v-if="item.desc">
                    <template #content>
                      <p>{{ item.desc }}</p>
                    </template>
                    <AppIcon iconName="app-warning" class="app-warning-icon"></AppIcon>
                  </el-tooltip>
                </div>
              </template>
            </el-option>
          </el-select>
        </el-form-item>
      </template>
    </DynamicsForm>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="close">cancelled</el-button>
        <el-button type="primary" @click="submit" :loading="loading"> Modified </el-button>
      </span>
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { ref, computed } from 'vue'
import type { Provider, BaseModel, Model } from '@/api/type/model'
import type { Dict, KeyValue } from '@/api/type/common'
import ModelApi from '@/api/model'
import type { FormField } from '@/components/dynamics-form/type'
import DynamicsForm from '@/components/dynamics-form/index.vue'
import type { FormRules } from 'element-plus'
import { MsgSuccess } from '@/utils/message'
import { QuestionFilled } from '@element-plus/icons-vue'
import AppIcon from '@/components/icons/AppIcon.vue'

const providerValue = ref<Provider>()
const dynamicsFormRef = ref<InstanceType<typeof DynamicsForm>>()
const emit = defineEmits(['change', 'submit'])
const loading = ref<boolean>(false)
const formLoading = ref<boolean>(false)
const model_type_loading = ref<boolean>(false)
const base_model_loading = ref<boolean>(false)
const model_type_list = ref<Array<KeyValue<string, string>>>([])
const modelValue = ref<Model>()
const base_model_list = ref<Array<BaseModel>>([])
const model_form_field = ref<Array<FormField>>([])
const dialogVisible = ref<boolean>(false)

const base_form_data_rule = ref<FormRules>({
  name: { required: true, trigger: 'blur', message: 'The name cannot be empty.' },
  model_type: { required: true, trigger: 'change', message: 'Models cannot be empty.' },
  model_name: { required: true, trigger: 'change', message: 'The basic model cannot be empty.' }
})

const base_form_data = ref<{
  name: string

  model_type: string

  model_name: string
}>({ name: '', model_type: '', model_name: '' })

const credential_form_data = ref<Dict<any>>({})

const form_data = computed({
  get: () => {
    return { ...credential_form_data.value, ...base_form_data.value }
  },
  set: (event: any) => {
    credential_form_data.value = event
  }
})

const getModelForm = (model_name: string) => {
  if (providerValue.value) {
    ModelApi.getModelCreateForm(
      providerValue.value.provider,
      form_data.value.model_type,
      model_name
    ).then((ok) => {
      model_form_field.value = ok.data
      if (modelValue.value) {
        // Rendering dynamic forms
        dynamicsFormRef.value?.render(model_form_field.value, modelValue.value.credential)
      }
    })
  }
}
const list_base_model = (model_type: any) => {
  if (providerValue.value) {
    ModelApi.listBaseModel(providerValue.value.provider, model_type, base_model_loading).then(
      (ok) => {
        base_model_list.value = ok.data
      }
    )
  }
}
const open = (provider: Provider, model: Model) => {
  modelValue.value = model
  ModelApi.getModelById(model.id, formLoading).then((ok) => {
    modelValue.value = ok.data
    ModelApi.listModelType(model.provider, model_type_loading).then((ok) => {
      model_type_list.value = ok.data
      list_base_model(model.model_type)
    })
    providerValue.value = provider

    base_form_data.value = {
      name: model.name,
      model_type: model.model_type,
      model_name: model.model_name
    }
    form_data.value = model.credential
    getModelForm(model.model_name)
  })
  dialogVisible.value = true
}

const close = () => {
  base_form_data.value = { name: '', model_type: '', model_name: '' }
  dynamicsFormRef.value?.ruleFormRef?.resetFields()
  credential_form_data.value = {}
  dialogVisible.value = false
}

const submit = () => {
  dynamicsFormRef.value?.validate().then(() => {
    if (modelValue.value) {
      ModelApi.updateModel(
        modelValue.value.id,
        {
          ...base_form_data.value,
          credential: credential_form_data.value
        },
        loading
      ).then((ok) => {
        MsgSuccess('Modeling is successful.')
        close()
        emit('submit')
      })
    }
  })
}

defineExpose({ open, close })
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
