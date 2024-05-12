import Clipboard from 'vue-clipboard3'
import { MsgSuccess, MsgError } from '@/utils/message'
/*
  Copy the stick.
*/
export async function copyClick(info: string) {
  const { toClipboard } = Clipboard()
  try {
    await toClipboard(info)
    MsgSuccess('Successful copying')
  } catch (e) {
    console.error(e)
    MsgError('Copy failure.')
  }
}
