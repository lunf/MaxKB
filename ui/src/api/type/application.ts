import { type Dict } from '@/api/type/common'
import { type Ref } from 'vue'
interface ApplicationFormType {
  name?: string
  desc?: string
  model_id?: string
  multiple_rounds_dialogue?: boolean
  prologue?: string
  dataset_id_list?: string[]
  dataset_setting?: any
  model_setting?: any
  problem_optimization?: boolean
  icon?: string | undefined
}
interface chatType {
  id: string
  problem_text: string
  answer_text: string
  buffer: Array<String>
  /**
   * Writing to the end.
   */
  write_ed?: boolean
  /**
   * is suspended
   */
  is_stop?: boolean
  record_id: string
  vote_status: string
}

export class ChatRecordManage {
  id?: any
  ms: number
  chat: chatType
  is_close?: boolean
  write_ed?: boolean
  is_stop?: boolean
  loading?: Ref<boolean>
  constructor(chat: chatType, ms?: number, loading?: Ref<boolean>) {
    this.ms = ms ? ms : 10
    this.chat = chat
    this.loading = loading
    this.is_stop = false
    this.is_close = false
    this.write_ed = false
  }
  write() {
    this.chat.is_stop = false
    this.is_stop = false
    if (this.loading) {
      this.loading.value = true
    }
    this.id = setInterval(() => {
      if (this.chat.buffer.length > 20) {
        this.chat.answer_text =
          this.chat.answer_text + this.chat.buffer.splice(0, this.chat.buffer.length - 20).join('')
      } else if (this.is_close) {
        this.chat.answer_text = this.chat.answer_text + this.chat.buffer.splice(0).join('')
        this.chat.write_ed = true
        this.write_ed = true
        if (this.loading) {
          this.loading.value = false
        }
        if (this.id) {
          clearInterval(this.id)
        }
      } else {
        const s = this.chat.buffer.shift()
        if (s !== undefined) {
          this.chat.answer_text = this.chat.answer_text + s
        }
      }
    }, this.ms)
  }
  stop() {
    clearInterval(this.id)
    this.is_stop = true
    this.chat.is_stop = true
    if (this.loading) {
      this.loading.value = false
    }
  }
  close() {
    this.is_close = true
  }
  append(answer_text_block: string) {
    for (let index = 0; index < answer_text_block.length; index++) {
      this.chat.buffer.push(answer_text_block[index])
    }
  }
}

export class ChatManagement {
  static chatMessageContainer: Dict<ChatRecordManage> = {}

  static addChatRecord(chat: chatType, ms: number, loading?: Ref<boolean>) {
    this.chatMessageContainer[chat.id] = new ChatRecordManage(chat, ms, loading)
  }
  static append(chatRecordId: string, content: string) {
    const chatRecord = this.chatMessageContainer[chatRecordId]
    if (chatRecord) {
      chatRecord.append(content)
    }
  }
  /**
   * Continued from the cache area. Write the data.
   * @param chatRecordId Dialogue recordsid
   */
  static write(chatRecordId: string) {
    const chatRecord = this.chatMessageContainer[chatRecordId]
    if (chatRecord) {
      chatRecord.write()
    }
  }
  /**
   * Wait after all data output is completed. It will close the flow.
   * @param chatRecordId Dialogue recordsid
   * @returns boolean
   */
  static close(chatRecordId: string) {
    const chatRecord = this.chatMessageContainer[chatRecordId]
    if (chatRecord) {
      chatRecord.close()
    }
  }
  /**
   * Stop the output. Immediately close the timely task output
   * @param chatRecordId Dialogue recordsid
   * @returns boolean
   */
  static stop(chatRecordId: string) {
    const chatRecord = this.chatMessageContainer[chatRecordId]
    if (chatRecord) {
      chatRecord.stop()
    }
  }
  /**
   * To determine whether the output is completed.
   * @param chatRecordId Dialogue recordsid
   * @returns boolean
   */
  static isClose(chatRecordId: string) {
    const chatRecord = this.chatMessageContainer[chatRecordId]
    return chatRecord ? chatRecord.is_close && chatRecord.write_ed : false
  }
  /**
   * Deciding whether to stop output.
   * @param chatRecordId Dialogue recordsid
   * @returns
   */
  static isStop(chatRecordId: string) {
    const chatRecord = this.chatMessageContainer[chatRecordId]
    return chatRecord ? chatRecord.is_stop : false
  }
  /**
   * Removing useless data That is beingcloseFall andstopThe data
   */
  static clean() {
    for (const key in Object.keys(this.chatMessageContainer)) {
      if (this.chatMessageContainer[key].is_close) {
        delete this.chatMessageContainer[key]
      }
    }
  }
}
export type { ApplicationFormType, chatType }
