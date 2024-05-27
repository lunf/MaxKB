<template>
  <el-scrollbar>
    <div class="upload-document p-24">
      <!-- Basic information -->
      <BaseForm ref="BaseFormRef" v-if="isCreate" />
      <el-form
        v-if="isCreate"
        ref="webFormRef"
        :rules="rules"
        :model="form"
        label-position="top"
        require-asterisk-position="right"
      >
        <el-form-item label="Type of Knowledge Base" required>
          <el-radio-group v-model="form.type" class="card__radio" @change="radioChange">
            <el-row :gutter="20">
              <el-col :span="12">
                <el-card shadow="never" class="mb-16" :class="form.type === '0' ? 'active' : ''">
                  <el-radio value="0" size="large">
                    <div class="flex align-center">
                      <AppAvatar class="mr-8" shape="square" :size="32">
                        <img src="@/assets/icon_document.svg" style="width: 58%" alt="" />
                      </AppAvatar>
                      <div>
                        <p class="mb-4">General Types</p>
                        <el-text type="info">You can build a knowledge base by uploading files or manually enrolling.</el-text>
                      </div>
                    </div>
                  </el-radio>
                </el-card>
              </el-col>
              <el-col :span="12">
                <el-card shadow="never" class="mb-16" :class="form.type === '1' ? 'active' : ''">
                  <el-radio value="1" size="large">
                    <div class="flex align-center">
                      <AppAvatar class="mr-8 avatar-purple" shape="square" :size="32">
                        <img src="@/assets/icon_web.svg" style="width: 58%" alt="" />
                      </AppAvatar>
                      <div>
                        <p class="mb-4">Web The site</p>
                        <el-text type="info">Building a knowledge base through a web site link synchronization </el-text>
                      </div>
                    </div>
                  </el-radio>
                </el-card>
              </el-col>
            </el-row>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="Web root address" prop="source_url" v-if="form.type === '1'">
          <el-input
            v-model="form.source_url"
            placeholder="Please enter. Web root address"
            @blur="form.source_url = form.source_url.trim()"
          />
        </el-form-item>
        <el-form-item label="The Selector" v-if="form.type === '1'">
          <el-input
            v-model="form.selector"
            placeholder="I think body, can enter. .classname/#idname/tagname"
            @blur="form.selector = form.selector.trim()"
          />
        </el-form-item>
      </el-form>

      <!-- uploaded documents. -->
      <UploadComponent ref="UploadComponentRef" v-if="form.type === '0'" />
    </div>
  </el-scrollbar>
</template>
<script setup lang="ts">
import { ref, onMounted, reactive, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import BaseForm from '@/views/dataset/component/BaseForm.vue'
import UploadComponent from '@/views/dataset/component/UploadComponent.vue'
import { isAllPropertiesEmpty } from '@/utils/utils'
import datasetApi from '@/api/dataset'
import { MsgError, MsgSuccess } from '@/utils/message'
import useStore from '@/stores'
const { dataset } = useStore()

const route = useRoute()
const router = useRouter()
const {
  params: { type }
} = route
const isCreate = type === 'create'
const BaseFormRef = ref()
const UploadComponentRef = ref()
const webFormRef = ref()
const loading = ref(false)

const form = ref<any>({
  type: '0',
  source_url: '',
  selector: ''
})

const rules = reactive({
  source_url: [{ required: true, message: 'Please enter. Web root address', trigger: 'blur' }]
})

watch(form.value, (value) => {
  if (isAllPropertiesEmpty(value)) {
    dataset.saveWebInfo(null)
  } else {
    dataset.saveWebInfo(value)
  }
})

function radioChange() {
  dataset.saveDocumentsFile([])
  form.value.source_url = ''
  form.value.selector = ''
}

const onSubmit = async () => {
  if (isCreate) {
    if (form.value.type === '0') {
      if ((await BaseFormRef.value?.validate()) && (await UploadComponentRef.value.validate())) {
        if (UploadComponentRef.value.form.fileList.length > 50) {
          MsgError('Increased every time.50A document.！')
          return false
        } else {
          /*
        storesSave the data.
      */
          dataset.saveBaseInfo(BaseFormRef.value.form)
          dataset.saveDocumentsFile(UploadComponentRef.value.form.fileList)
          return true
        }
      } else {
        return false
      }
    } else {
      if (await BaseFormRef.value?.validate()) {
        await webFormRef.value.validate((valid: any) => {
          if (valid) {
            const obj = { ...BaseFormRef.value.form, ...form.value }
            datasetApi.postWebDataset(obj, loading).then((res) => {
              MsgSuccess('Submitted Success')
              dataset.saveBaseInfo(null)
              dataset.saveWebInfo(null)
              router.push({ path: `/dataset/${res.data.id}/document` })
            })
          } else {
            return false
          }
        })
      } else {
        return false
      }
    }
  } else {
    if (await UploadComponentRef.value.validate()) {
      /*
        storesSave the data.
      */
      dataset.saveDocumentsFile(UploadComponentRef.value.form.fileList)
      return true
    } else {
      return false
    }
  }
}

onMounted(() => {})

defineExpose({
  onSubmit,
  loading
})
</script>
<style scoped lang="scss">
.upload-document {
  width: 70%;
  margin: 0 auto;
  margin-bottom: 20px;
}
</style>
