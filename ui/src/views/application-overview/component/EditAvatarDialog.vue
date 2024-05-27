<template>
  <el-dialog title="set up Logo" v-model="dialogVisible">
    <el-radio-group v-model="radioType" class="radio-block mb-16">
      <div>
        <el-radio value="default">
          <p>presumed Logo</p>
          <AppAvatar
            v-if="detail?.name"
            :name="detail?.name"
            pinyinColor
            class="mt-8 mb-8"
            shape="square"
            :size="32"
          />
        </el-radio>
      </div>
      <div class="mt-8">
        <el-radio value="custom">
          <p>Customized upload</p>
          <div class="flex mt-8">
            <AppAvatar
              v-if="fileURL"
              shape="square"
              :size="32"
              style="background: none"
              class="mr-16"
            >
              <img :src="fileURL" alt="" />
            </AppAvatar>
            <el-upload
              ref="uploadRef"
              action="#"
              :auto-upload="false"
              :show-file-list="false"
              accept="image/*"
              :on-change="onChange"
            >
              <el-button icon="Upload" :disabled="radioType !== 'custom'">uploaded</el-button>
            </el-upload>
          </div>
          <div class="el-upload__tip info mt-16">
            recommended size. 32*32, supported ico、png , The size does not exceed200KB
          </div>
        </el-radio>
      </div>
    </el-radio-group>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click.prevent="dialogVisible = false"> Cancel </el-button>
        <el-button type="primary" @click="submit" :loading="loading"> Save </el-button>
      </span>
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import overviewApi from '@/api/application-overview'
import { cloneDeep } from 'lodash'
import { MsgSuccess, MsgError } from '@/utils/message'
import { defaultIcon, isAppIcon } from '@/utils/application'
import useStore from '@/stores'

const { application } = useStore()

const route = useRoute()
const {
  params: { id } //Applicationsid
} = route

const emit = defineEmits(['refresh'])

const iconFile = ref<any>(null)
const fileURL = ref<any>(null)

const dialogVisible = ref<boolean>(false)
const loading = ref(false)
const detail = ref<any>(null)
const radioType = ref('default')

watch(dialogVisible, (bool) => {
  if (!bool) {
    iconFile.value = null
    fileURL.value = null
  }
})

const open = (data: any) => {
  radioType.value = isAppIcon(data.icon) ? 'custom' : 'default'
  fileURL.value = isAppIcon(data.icon) ? data.icon : null
  detail.value = cloneDeep(data)
  dialogVisible.value = true
}

const onChange = (file: any) => {
  //1、Deciding whether the file size is legal. The limitation of documents cannot be greater than 200KB
  const isLimit = file?.size / 1024 < 200
  if (!isLimit) {
    MsgError('The file is greater. 200KB')
    return false
  }
  iconFile.value = file
  fileURL.value = URL.createObjectURL(file.raw)
}

function submit() {
  if (radioType.value === 'default') {
    application.asyncPutApplication(id as string, { icon: defaultIcon }, loading).then((res) => {
      emit('refresh')
      MsgSuccess('Setup Success')
      dialogVisible.value = false
    })
  } else if (radioType.value === 'custom' && iconFile.value) {
    let fd = new FormData()
    fd.append('file', iconFile.value.raw)
    overviewApi.putAppIcon(id as string, fd, loading).then((res: any) => {
      emit('refresh')
      MsgSuccess('Setup Success')
      dialogVisible.value = false
    })
  } else {
    MsgError('Please upload a picture.')
  }
}

defineExpose({ open })
</script>
<style lang="scss" scope></style>
