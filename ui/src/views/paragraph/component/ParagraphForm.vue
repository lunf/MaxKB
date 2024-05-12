<template>
  <el-form
    ref="paragraphFormRef"
    :model="form"
    label-position="top"
    require-asterisk-position="right"
    :rules="rules"
    @submit.prevent
  >
    <el-form-item label="Section title">
      <el-input v-if="isEdit" v-model="form.title" placeholder="Please enter the section title."> </el-input>
      <span class="lighter" v-else>{{ form.title || '-' }}</span>
    </el-form-item>
    <el-form-item label="Part of content." prop="content">
      <!-- <el-input
        v-if="isEdit"
        v-model="form.content"
        placeholder="Please enter the section."
        maxlength="4096"
        show-word-limit
        :rows="8"
        type="textarea"
      > 
     </el-input>-->
      <MarkdownEditor
        v-if="isEdit"
        v-model="form.content"
        placeholder="Please enter the section."
        :maxLength="4096"
        :preview="false"
        :toolbars="toolbars"
        style="height: 300px"
        @onUploadImg="onUploadImg"
      />
      <MdPreview
        v-else
        ref="editorRef"
        editorId="preview-only"
        :modelValue="form.content"
        class="maxkb-md"
      />
      <!-- <span v-else class="break-all lighter">{{ form.content }}</span> -->
    </el-form-item>
  </el-form>
</template>
<script setup lang="ts">
import { ref, reactive, onUnmounted, watch, nextTick } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import { MdPreview } from 'md-editor-v3'
import MarkdownEditor from '@/components/markdown-editor/index.vue'
import imageApi from '@/api/image'
const props = defineProps({
  data: {
    type: Object,
    default: () => {}
  },
  isEdit: Boolean
})

const toolbars = [
  'bold',
  'underline',
  'italic',
  '-',
  'title',
  'strikeThrough',
  'sub',
  'sup',
  'quote',
  'unorderedList',
  'orderedList',
  'task',
  '-',
  'codeRow',
  'code',
  'link',
  'image',
  'table',
  'mermaid',
  'katex',
  '-',
  'revoke',
  'next',
  '=',
  'pageFullscreen',
  'preview',
  'htmlPreview'
] as any[]

const editorRef = ref()

const form = ref<any>({
  title: '',
  content: ''
})

const rules = reactive<FormRules>({
  content: [
    { required: true, message: 'Please enter the section.', trigger: 'blur' },
    { max: 4096, message: 'Not more than the content. 4096 One word.', trigger: 'blur' }
  ]
})

const paragraphFormRef = ref<FormInstance>()

watch(
  () => props.data,
  (value) => {
    if (value && JSON.stringify(value) !== '{}') {
      form.value.title = value.title
      form.value.content = value.content
    }
  },
  {
    immediate: true
  }
)
watch(
  () => props.isEdit,
  (value) => {
    if (!value) {
      paragraphFormRef.value?.clearValidate()
    }
  },
  {
    immediate: true
  }
)

/*
  Forms of Examination
*/
function validate() {
  if (!paragraphFormRef.value) return
  return paragraphFormRef.value.validate((valid: any) => {
    return valid
  })
}

const onUploadImg = async (files: any, callback: any) => {
  const res = await Promise.all(
    files.map((file: any) => {
      return new Promise((rev, rej) => {
        const fd = new FormData()
        fd.append('file', file)

        imageApi
          .postImage(fd)
          .then((res: any) => {
            rev(res)
          })
          .catch((error) => rej(error))
      })
    })
  )

  callback(res.map((item) => item.data))
}

onUnmounted(() => {
  form.value = {
    title: '',
    content: ''
  }
})

defineExpose({
  validate,
  form
})
</script>
<style scoped lang="scss"></style>
