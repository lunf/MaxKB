<template>
  <el-row :gutter="16">
    <el-col
      :xs="12"
      :sm="12"
      :md="12"
      :lg="6"
      :xl="6"
      v-for="(item, index) in statisticsType"
      :key="index"
      class="mb-16"
    >
      <el-card shadow="never">
        <div class="flex align-center ml-8 mr-8">
          <el-avatar :size="40" shape="square" :style="{ background: item.background }">
            <appIcon :iconName="item.icon" :style="{ fontSize: '24px', color: item.color }" />
          </el-avatar>
          <div class="ml-12">
            <p class="color-secondary lighter mb-4">{{ item.name }}</p>
            <div v-if="item.id !== 'starCharts'" class="flex align-baseline">
              <h2>{{ numberFormat(item.sum?.[0]) }}</h2>
              <span v-if="item.sum.length > 1" class="ml-12" style="color: #f54a45"
                >+{{ numberFormat(item.sum?.[1]) }}</span
              >
            </div>
            <div v-else class="flex align-center mr-8">
              <AppIcon iconName="app-like-color"></AppIcon>
              <h2 class="ml-4">{{ item.sum?.[0] }}</h2>
              <AppIcon class="ml-12" iconName="app-oppose-color"></AppIcon>
              <h2 class="ml-4">{{ item.sum?.[1] }}</h2>
            </div>
          </div>
        </div>
      </el-card>
    </el-col>
  </el-row>
  <el-row :gutter="16">
    <el-col
      :xs="24"
      :sm="24"
      :md="24"
      :lg="12"
      :xl="12"
      v-for="(item, index) in statisticsType"
      :key="index"
      class="mb-16"
    >
      <el-card shadow="never">
        <div class="p-8">
          <AppCharts height="316px" :id="item.id" type="line" :option="item.option" />
        </div>
      </el-card>
    </el-col>
  </el-row>
</template>
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import AppCharts from '@/components/app-charts/index.vue'
import { getAttrsArray, getSum, numberFormat } from '@/utils/utils'
const props = defineProps({
  data: {
    type: Array,
    default: () => []
  }
})
const statisticsType = computed(() => [
  {
    id: 'customerCharts',
    name: 'The total number of users',
    icon: 'app-user',
    background: '#EBF1FF',
    color: '#3370FF',
    sum: [
      getSum(getAttrsArray(props.data, 'customer_num') || 0),
      getSum(getAttrsArray(props.data, 'customer_added_count') || 0)
    ],
    option: {
      title: 'The total number of users',
      xData: getAttrsArray(props.data, 'day'),
      yData: [
        {
          name: 'The total number of users',
          type: 'line',
          area: true,
          data: getAttrsArray(props.data, 'customer_num')
        },
        {
          name: 'Added number of users',
          type: 'line',
          area: true,
          data: getAttrsArray(props.data, 'customer_added_count')
        }
      ]
    }
  },
  {
    id: 'chatRecordCharts',
    name: 'Number of Questions',
    icon: 'app-question',
    background: '#FFF3E5',
    color: '#FF8800',
    sum: [getSum(getAttrsArray(props.data, 'chat_record_count') || 0)],
    option: {
      title: 'Number of Questions',
      xData: getAttrsArray(props.data, 'day'),
      yData: [
        {
          type: 'line',
          data: getAttrsArray(props.data, 'chat_record_count')
        }
      ]
    }
  },
  {
    id: 'tokensCharts',
    name: 'Tokens The total number',
    icon: 'app-tokens',
    background: '#E5FBF8',
    color: '#00D6B9',
    sum: [getSum(getAttrsArray(props.data, 'tokens_num') || 0)],
    option: {
      title: 'Tokens The total number',
      xData: getAttrsArray(props.data, 'day'),
      yData: [
        {
          type: 'line',
          data: getAttrsArray(props.data, 'tokens_num')
        }
      ]
    }
  },
  {
    id: 'starCharts',
    name: 'User satisfaction',
    icon: 'app-user-stars',
    background: '#FEEDEC',
    color: '#F54A45',
    sum: [
      getSum(getAttrsArray(props.data, 'star_num') || 0),
      getSum(getAttrsArray(props.data, 'trample_num') || 0)
    ],
    option: {
      title: 'User satisfaction',
      xData: getAttrsArray(props.data, 'day'),
      yData: [
        {
          name: 'agreed',
          type: 'line',
          data: getAttrsArray(props.data, 'star_num')
        },
        {
          name: 'opposed',
          type: 'line',
          data: getAttrsArray(props.data, 'trample_num')
        }
      ]
    }
  }
])
</script>
<style lang="scss" scoped></style>
