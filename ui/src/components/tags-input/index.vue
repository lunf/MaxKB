<template>
  <!-- The externaldiv -->
  <div ref="InputTag" class="tags-input">
    <div class="tags-container" v-if="tagsList.length">
      <!-- Tagged -->
      <el-tag
        v-for="(item, index) in tagsList"
        :key="index"
        @close="removeTag(index)"
        closable
        class="mr-8"
        type="info"
        >{{ item.username }}
      </el-tag>
    </div>
    <!-- The entrance box -->
    <el-autocomplete
      :placeholder="tagsList.length == 0 ? placeholder : ''"
      :validate-event="false"
      v-model="currentval"
      :fetch-suggestions="querySearchAsync"
      @select="handleSelect"
      :popper-class="noData ? 'platform-auto-complete' : ''"
    >
      <template #default="{ item }">
        <!-- Uncompatible information Uncompatible data -->
        <div class="default" v-if="noData">{{ item.default }}</div>
        <div class="value" v-else>{{ item.username }}</div>
      </template>
    </el-autocomplete>
    <!-- <el-input
      :validate-event="false"
      v-model="currentval"
      :placeholder="tagsList.length == 0 ? placeholder : ''"
      @keydown.enter="addTags"
    /> -->
  </div>
</template>
<script setup lang="ts">
import { ref, watch } from 'vue'
import UserApi from '@/api/user'
defineOptions({ name: 'TagsInput' })
const props = defineProps({
  tags: {
    /* Many of */
    type: Array<any>,
    default: () => []
  },
  placeholder: {
    type: String,
    default: 'Please enter.'
  },
  limit: {
    /* Maximum number of labels. */
    type: Number,
    default: -1
  }
})
const emit = defineEmits(['update:tags'])
const currentval = ref('')
const tagsList = ref<any[]>([])
const noData = ref(false) // Compatible with the data.

watch([tagsList, currentval], (val) => {
  emit('update:tags', val[0])
})

const querySearchAsync = (queryString: string, cb: (arg: any) => void) => {
  if (queryString) {
    let matchResults
    UserApi.getUserList(queryString).then((res) => {
      if (res.data.length === 0) {
        noData.value = true
        matchResults = [{ default: 'No matching data.' }]
      } else {
        noData.value = false
        matchResults = res.data
      }
      cb(matchResults)
    })
  } else {
    cb([])
  }
}

const handleSelect = (item: any) => {
  if (!tagsList.value.some((obj: any) => obj.id === item.id)) {
    tagsList.value.push(item)
  }
  currentval.value = ''
}

function removeTag(index: number) {
  tagsList.value.splice(index, 1)
}
</script>
<style lang="scss" scoped>
.tags-input {
  width: 100%;
  min-height: 70px;
  border: 1px solid var(--el-border-color);
  border-radius: var(--el-border-radius-base);
  &:hover {
    border: 1px solid var(--el-color-primary);
  }
  &:focus-within {
    border: 1px solid var(--el-color-primary);
  }
  :deep(.el-autocomplete) {
    width: 100%;
  }
  :deep(.el-input__wrapper) {
    background: none !important;
    box-shadow: none !important;
    border-radius: 0 !important;
    resize: none;
  }
  .tags-container {
    padding: 0 6px;
  }
}
</style>
