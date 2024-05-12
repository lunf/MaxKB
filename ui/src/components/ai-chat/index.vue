<template>
  <div ref="aiChatRef" class="ai-chat" :class="log ? 'chart-log' : ''">
    <el-scrollbar ref="scrollDiv" @scroll="handleScrollTop">
      <div ref="dialogScrollbar" class="ai-chat__content p-24">
        <div class="item-content mb-16" v-if="!props.available || props.data?.prologue">
          <div class="avatar">
            <AppAvatar class="avatar-gradient">
              <img src="@/assets/icon_robot.svg" style="width: 75%" alt="" />
            </AppAvatar>
          </div>

          <div class="content">
            <el-card shadow="always" class="dialog-card">
              <template v-for="(item, index) in prologueList" :key="index">
                <div
                  v-if="item.type === 'question'"
                  @click="quickProblemHandle(item.str)"
                  class="problem-button ellipsis-2 mb-8"
                  :class="log ? 'disabled' : 'cursor'"
                >
                  <el-icon><EditPen /></el-icon>
                  {{ item.str }}
                </div>
                <MdPreview
                  v-else
                  class="mb-8"
                  ref="editorRef"
                  editorId="preview-only"
                  :modelValue="item.str"
                />
              </template>
            </el-card>
          </div>
        </div>
        <template v-for="(item, index) in chatList" :key="index">
          <!-- The problem -->
          <div class="item-content mb-16 lighter">
            <div class="avatar">
              <AppAvatar>
                <img src="@/assets/user-icon.svg" style="width: 54%" alt="" />
              </AppAvatar>
            </div>
            <div class="content">
              <div class="text break-all">
                {{ item.problem_text }}
              </div>
            </div>
          </div>
          <!-- Reply -->
          <div class="item-content mb-16 lighter">
            <div class="avatar">
              <AppAvatar class="avatar-gradient">
                <img src="@/assets/icon_robot.svg" style="width: 75%" alt="" />
              </AppAvatar>
            </div>

            <div class="content">
              <div class="flex" v-if="!item.answer_text">
                <el-card
                  v-if="item.write_ed === undefined || item.write_ed === true"
                  shadow="always"
                  class="dialog-card"
                >
                  Sorry to，Not found relevant content.，Please resume your question or provide more information.。
                </el-card>
                <el-card v-else-if="item.is_stop" shadow="always" class="dialog-card">
                  stopped answering.
                </el-card>
                <el-card v-else shadow="always" class="dialog-card">
                  in reply. <span class="dotting"></span>
                </el-card>
              </div>

              <el-card v-else shadow="always" class="dialog-card">
                <MdRenderer :source="item.answer_text"></MdRenderer>
                <div
                  v-if="(id && item.write_ed) || (props.data?.show_source && item.write_ed) || log"
                >
                  <el-divider> <el-text type="info">Source of Knowledge</el-text> </el-divider>
                  <div class="mb-8">
                    <el-space wrap>
                      <el-button
                        v-for="(dataset, index) in item.dataset_list"
                        :key="index"
                        type="primary"
                        plain
                        size="small"
                        @click="openParagraph(item, dataset.id)"
                        >{{ dataset.name }}</el-button
                      >
                    </el-space>
                  </div>

                  <div>
                    <el-button
                      class="mr-8"
                      type="primary"
                      plain
                      size="small"
                      @click="openParagraph(item)"
                      :disabled="!item.paragraph_list || item.paragraph_list?.length === 0"
                      >Reference to Section：{{ item.paragraph_list?.length || 0 }}</el-button
                    >
                    <el-tag type="info" effect="plain">
                      consumption tokens: {{ item?.message_tokens + item?.answer_tokens }}
                    </el-tag>
                    <el-tag class="ml-8" type="info" effect="plain">
                      It takes time: {{ item.run_time?.toFixed(2) }} s
                    </el-tag>
                  </div>
                </div>
              </el-card>
              <div class="flex-between mt-8" v-if="log">
                <LogOperationButton v-model:data="chatList[index]" :applicationId="appId" />
              </div>

              <div class="flex-between mt-8" v-else>
                <div>
                  <el-button
                    type="primary"
                    v-if="item.is_stop && !item.write_ed"
                    @click="startChat(item)"
                    link
                    >Continued</el-button
                  >
                  <el-button type="primary" v-else-if="!item.write_ed" @click="stopChat(item)" link
                    >Stop answering.</el-button
                  >
                </div>

                <div v-if="item.write_ed && props.appId">
                  <OperationButton
                    :data="item"
                    :applicationId="appId"
                    :chartId="chartOpenId"
                    @regeneration="regenerationChart(item)"
                  />
                </div>
              </div>
            </div>
          </div>
        </template>
      </div>
    </el-scrollbar>
    <div class="ai-chat__operate p-24" v-if="!log">
      <div class="operate-textarea flex">
        <el-input
          ref="quickInputRef"
          v-model="inputValue"
          placeholder="Please enter."
          :rows="1"
          type="textarea"
          :maxlength="1024"
          @keydown.enter="sendChatHandle($event)"
        />
        <div class="operate">
          <el-button
            text
            class="sent-button"
            :disabled="isDisabledChart || loading"
            @click="sendChatHandle"
          >
            <img v-show="isDisabledChart || loading" src="@/assets/icon_send.svg" alt="" />
            <img
              v-show="!isDisabledChart && !loading"
              src="@/assets/icon_send_colorful.svg"
              alt=""
            />
          </el-button>
        </div>
      </div>
    </div>
    <!-- The Knowledge Base dialog -->
    <ParagraphSourceDialog ref="ParagraphSourceDialogRef" />
  </div>
</template>
<script setup lang="ts">
import { ref, nextTick, computed, watch, reactive } from 'vue'
import { useRoute } from 'vue-router'
import LogOperationButton from './LogOperationButton.vue'
import OperationButton from './OperationButton.vue'
import ParagraphSourceDialog from './ParagraphSourceDialog.vue'
import applicationApi from '@/api/application'
import logApi from '@/api/log'
import { ChatManagement, type chatType } from '@/api/type/application'
import { randomId } from '@/utils/utils'
import useStore from '@/stores'
import MdRenderer from '@/components/markdown-renderer/MdRenderer.vue'
import { MdPreview } from 'md-editor-v3'
import { MsgError } from '@/utils/message'
import { debounce } from 'lodash'
defineOptions({ name: 'AiChat' })
const route = useRoute()
const {
  params: { accessToken, id }
} = route as any
const props = defineProps({
  data: {
    type: Object,
    default: () => {}
  },
  appId: String, // Only share the link.
  log: Boolean,
  record: {
    type: Array<chatType[]>,
    default: () => []
  },
  // Application is available.
  available: {
    type: Boolean,
    default: true
  }
})
const { application } = useStore()

const ParagraphSourceDialogRef = ref()
const aiChatRef = ref()
const quickInputRef = ref()
const scrollDiv = ref()
const dialogScrollbar = ref()
const loading = ref(false)
const inputValue = ref('')
const chartOpenId = ref('')
const chatList = ref<any[]>([])

const isDisabledChart = computed(
  () => !(inputValue.value.trim() && (props.appId || props.data?.name))
)
const isMdArray = (val: string) => val.match(/^-\s.*/m)
const prologueList = computed(() => {
  const temp = props.available
    ? props.data?.prologue
    : 'Sorry to，Currently beingined.，cannot provide services.，Please try again later.！'
  let arr: any = []
  const lines = temp?.split('\n')
  lines?.forEach((str: string, index: number) => {
    if (isMdArray(str)) {
      arr[index] = {
        type: 'question',
        str: str.replace(/^-\s+/, '')
      }
    } else {
      arr[index] = {
        type: 'md',
        str
      }
    }
  })
  return arr
})

watch(
  () => props.data,
  () => {
    chartOpenId.value = ''
  },
  { deep: true }
)

watch(
  () => props.record,
  (value) => {
    if (props.log) {
      chatList.value = value
    }
  },
  {
    immediate: true
  }
)

function openParagraph(row: any, id?: string) {
  ParagraphSourceDialogRef.value.open(row, id)
}

function quickProblemHandle(val: string) {
  if (!loading.value && props.data?.name) {
    handleDebounceClick(val)
  }
}

const handleDebounceClick = debounce((val) => {
  chatMessage(null, val)
}, 200)

function sendChatHandle(event: any) {
  if (!event.ctrlKey) {
    // If you do not press the combination key.ctrl，It will stop the default event.
    event.preventDefault()
    if (!isDisabledChart.value && !loading.value && !event.isComposing) {
      if (inputValue.value.trim()) {
        chatMessage()
      }
    }
  } else {
    // Pressing at the same time.ctrl+Back to the car key.，It will change.
    inputValue.value += '\n'
  }
}
const stopChat = (chat: chatType) => {
  ChatManagement.stop(chat.id)
}
const startChat = (chat: chatType) => {
  ChatManagement.write(chat.id)
}
/**
 * Dialogue
 */
function getChartOpenId(chat?: any) {
  loading.value = true
  const obj = props.data
  if (props.appId) {
    return applicationApi
      .getChatOpen(props.appId)
      .then((res) => {
        chartOpenId.value = res.data
        chatMessage(chat)
      })
      .catch((res) => {
        if (res.response.status === 403) {
          application.asyncAppAuthentication(accessToken).then(() => {
            getChartOpenId()
          })
        } else {
          loading.value = false
          return Promise.reject(res)
        }
      })
  } else {
    return applicationApi
      .postChatOpen(obj)
      .then((res) => {
        chartOpenId.value = res.data
        chatMessage(chat)
      })
      .catch((res) => {
        loading.value = false
        return Promise.reject(res)
      })
  }
}
/**
 * Get a transfer function.,Processing of flow data
 * @param chat    Record of each conversation.
 * @param reader  flow data
 * @param stream  Is it flow data?
 */
const getWrite = (chat: any, reader: any, stream: boolean) => {
  let tempResult = ''
  /**
   *
   * @param done  Is it ended
   * @param value Value
   */
  const write_stream = ({ done, value }: { done: boolean; value: any }) => {
    try {
      if (done) {
        ChatManagement.close(chat.id)
        return
      }
      const decoder = new TextDecoder('utf-8')
      let str = decoder.decode(value, { stream: true })
      // Explain here. start The data flow is not backward.chunkReturn to What we want to get.chunkisdata:{xxx}\n\n But it may be obtained. data:{ -> xxx}\n\n In the whole, it is fetchNot guaranteed each.chunkEveryone saysdata:Started \n\nended
      tempResult += str
      const split = tempResult.match(/data:.*}\n\n/g)
      if (split) {
        str = split.join('')
        tempResult = tempResult.replace(str, '')
      } else {
        return reader.read().then(write_stream)
      }
      // Explain here. end
      if (str && str.startsWith('data:')) {
        if (split) {
          for (const index in split) {
            const chunk = JSON?.parse(split[index].replace('data:', ''))
            chat.chat_id = chunk.chat_id
            chat.record_id = chunk.id
            const content = chunk?.content
            if (content) {
              ChatManagement.append(chat.id, content)
            }
            if (chunk.is_end) {
              // Successful processing. Successful return.
              return Promise.resolve()
            }
          }
        }
      }
    } catch (e) {
      return Promise.reject(e)
    }
    return reader.read().then(write_stream)
  }
  /**
   * Processed json Reply
   * @param param0
   */
  const write_json = ({ done, value }: { done: boolean; value: any }) => {
    if (done) {
      const result_block = JSON.parse(tempResult)
      if (result_block.code === 500) {
        return Promise.reject(result_block.message)
      } else {
        if (result_block.content) {
          ChatManagement.append(chat.id, result_block.content)
        }
      }
      ChatManagement.close(chat.id)
      return
    }
    if (value) {
      const decoder = new TextDecoder('utf-8')
      tempResult += decoder.decode(value)
    }
    return reader.read().then(write_json)
  }
  return stream ? write_stream : write_json
}
const errorWrite = (chat: any, message?: string) => {
  ChatManagement.addChatRecord(chat, 50, loading)
  ChatManagement.write(chat.id)
  ChatManagement.append(chat.id, message || 'Sorry to，Currently beingined.，cannot provide services.，Please try again later.！')
  ChatManagement.close(chat.id)
}
function chatMessage(chat?: any, problem?: string, re_chat?: boolean) {
  loading.value = true
  if (!chat) {
    chat = reactive({
      id: randomId(),
      problem_text: problem ? problem : inputValue.value.trim(),
      answer_text: '',
      buffer: [],
      write_ed: false,
      is_stop: false,
      record_id: '',
      vote_status: '-1'
    })
    chatList.value.push(chat)
    ChatManagement.addChatRecord(chat, 50, loading)
    ChatManagement.write(chat.id)
    inputValue.value = ''
    nextTick(() => {
      // Turn the rotating line to the bottom.
      scrollDiv.value.setScrollTop(getMaxHeight())
    })
  }
  if (!chartOpenId.value) {
    getChartOpenId(chat).catch((e) => {
      errorWrite(chat)
    })
  } else {
    const obj = {
      message: chat.problem_text,
      re_chat: re_chat || false
    }
    // Dialogue
    applicationApi
      .postChatMessage(chartOpenId.value, obj)
      .then((response) => {
        if (response.status === 401) {
          application
            .asyncAppAuthentication(accessToken)
            .then(() => {
              chatMessage(chat)
            })
            .catch((err) => {
              errorWrite(chat)
            })
        } else if (response.status === 460) {
          return Promise.reject('Unable to identify user identity.')
        } else if (response.status === 461) {
          return Promise.reject('Sorry to，Your questions have reached the maximum limit.，Please come again tomorrow.！')
        } else {
          nextTick(() => {
            // Turn the rotating line to the bottom.
            scrollDiv.value.setScrollTop(getMaxHeight())
          })
          const reader = response.body.getReader()
          // Processing flow data
          const write = getWrite(
            chat,
            reader,
            response.headers.get('Content-Type') !== 'application/json'
          )
          return reader.read().then(write)
        }
      })
      .then(() => {
        return (id || props.data?.show_source) && getSourceDetail(chat)
      })
      .finally(() => {
        ChatManagement.close(chat.id)
      })
      .catch((e: any) => {
        errorWrite(chat, e + '')
      })
  }
}

function regenerationChart(item: chatType) {
  inputValue.value = item.problem_text
  chatMessage(null, '', true)
}

function getSourceDetail(row: any) {
  logApi.getRecordDetail(id || props.appId, row.chat_id, row.record_id, loading).then((res) => {
    const exclude_keys = ['answer_text', 'id']
    Object.keys(res.data).forEach((key) => {
      if (!exclude_keys.includes(key)) {
        row[key] = res.data[key]
      }
    })
  })
  return true
}

/**
 * Roll the distance to the top height.
 */
const scrollTop = ref(0)

const scorll = ref(true)

const getMaxHeight = () => {
  return dialogScrollbar.value!.scrollHeight
}
const handleScrollTop = ($event: any) => {
  scrollTop.value = $event.scrollTop
  if (
    dialogScrollbar.value.scrollHeight - (scrollTop.value + scrollDiv.value.wrapRef.offsetHeight) <=
    30
  ) {
    scorll.value = true
  } else {
    scorll.value = false
  }
}

const handleScroll = () => {
  if (!props.log && scrollDiv.value) {
    // Interior height is less than external height. You need to roll out.
    if (scrollDiv.value.wrapRef.offsetHeight < dialogScrollbar.value.scrollHeight) {
      // If the current roll line is at the lowest distance. Set the distance. Rolling track followed.
      if (scorll.value) {
        scrollDiv.value.setScrollTop(getMaxHeight())
      }
    }
  }
}

watch(
  chatList,
  () => {
    handleScroll()
  },
  { deep: true, immediate: true }
)
</script>
<style lang="scss" scoped>
.ai-chat {
  --padding-left: 40px;
  height: 100%;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  position: relative;
  color: var(--app-text-color);
  box-sizing: border-box;
  &.chart-log {
    .ai-chat__content {
      padding-bottom: 0;
    }
  }
  &__content {
    padding-top: 0;
    padding-bottom: 96px;
    box-sizing: border-box;

    .avatar {
      float: left;
    }
    .content {
      padding-left: var(--padding-left);
      :deep(ol) {
        margin-left: 16px !important;
      }
    }
    .text {
      padding: 6px 0;
    }
    .problem-button {
      width: 100%;
      border: none;
      border-radius: 8px;
      background: var(--app-layout-bg-color);
      height: 46px;
      padding: 0 12px;
      line-height: 46px;
      box-sizing: border-box;
      color: var(--el-text-color-regular);
      -webkit-line-clamp: 1;
      word-break: break-all;
      &:hover {
        background: var(--el-color-primary-light-9);
      }
      &.disabled {
        &:hover {
          background: var(--app-layout-bg-color);
        }
      }
      :deep(.el-icon) {
        color: var(--el-color-primary);
      }
    }
  }
  &__operate {
    background: #f3f7f9;
    position: absolute;
    bottom: 0;
    left: 0;
    width: 100%;
    box-sizing: border-box;
    z-index: 10;
    &:before {
      background: linear-gradient(0deg, #f3f7f9 0%, rgba(243, 247, 249, 0) 100%);
      content: '';
      position: absolute;
      width: 100%;
      top: -16px;
      left: 0;
      height: 16px;
    }
    .operate-textarea {
      box-shadow: 0px 6px 24px 0px rgba(31, 35, 41, 0.08);
      background-color: #ffffff;
      border-radius: 8px;
      border: 1px solid #ffffff;
      box-sizing: border-box;

      &:has(.el-textarea__inner:focus) {
        border: 1px solid var(--el-color-primary);
      }

      :deep(.el-textarea__inner) {
        border-radius: 8px !important;
        box-shadow: none;
        resize: none;
        padding: 12px 16px;
        box-sizing: border-box;
      }
      .operate {
        padding: 6px 10px;
        .sent-button {
          max-height: none;
          .el-icon {
            font-size: 24px;
          }
        }
        :deep(.el-loading-spinner) {
          margin-top: -15px;
          .circular {
            width: 31px;
            height: 31px;
          }
        }
      }
    }
  }
  .dialog-card {
    border: none;
    border-radius: 8px;
  }
}
</style>
