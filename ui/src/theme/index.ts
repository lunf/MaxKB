import type {
  ThemeSetting,
  InferData,
  KeyValueData,
  UpdateInferData,
  UpdateKeyValueData
} from './type'
import { TinyColor } from '@ctrl/tinycolor'
// Introduction of default assumption data
import inferData from './defaultInferData'
// Introduction of defaultkeyValueThe data
import keyValueData from './defaultKeyValueData'
// Introduction of objects.
import setting from './setting'
import type { App } from 'vue'
declare global {
  interface ChildNode {
    innerText: string
  }
}
class Theme {
  /**
   * Subject settings
   */
  themeSetting: ThemeSetting
  /**
   * Key value data
   */
  keyValue: KeyValueData
  /**
   * External data
   */
  inferData: Array<InferData>
  /**
   *Is it the first initiation?
   */
  isFirstWriteStyle: boolean
  /**
   * mixed white.
   */
  colorWhite: string
  /**
   * mixed black.
   */
  colorBlack: string

  constructor(themeSetting: ThemeSetting, keyValue: KeyValueData, inferData: Array<InferData>) {
    this.themeSetting = themeSetting
    this.keyValue = keyValue
    this.inferData = inferData
    this.isFirstWriteStyle = true
    this.colorWhite = '#ffffff'
    this.colorBlack = '#000000'
    this.initDefaultTheme()
  }

  /**
   * Connected
   * @param setting Subject settings
   * @param names   All the values needed.
   * @returns       Data after compilation.
   */
  getVarName = (setting: ThemeSetting, ...names: Array<string>) => {
    return (
      setting.startDivision + setting.namespace + setting.division + names.join(setting.division)
    )
  }

  /**
   * Convert external data.
   * @param setting      Subject setting.
   * @param inferData    External data
   * @returns
   */
  mapInferMainStyle = (setting: ThemeSetting, inferData: InferData) => {
    const key: string = this.getVarName(
      setting,
      inferData.setting ? inferData.setting.type : setting.colorInferSetting.type,
      inferData.key
    )
    return {
      [key]: inferData.value,
      ...this.mapInferDataStyle(setting, inferData)
    }
  }
  /**
   * Convert external data.
   * @param setting    set up
   * @param inferData External data
   */
  mapInferData = (setting: ThemeSetting, inferData: Array<InferData>) => {
    return inferData
      .map((itemData) => {
        return this.mapInferMainStyle(setting, itemData)
      })
      .reduce((pre, next) => {
        return { ...pre, ...next }
      }, {})
  }
  /**
   * Convert external data.
   * @param setting      Subject setting.
   * @param inferData    External data
   * @returns
   */
  mapInferDataStyle = (setting: ThemeSetting, inferData: InferData) => {
    const inferSetting = inferData.setting ? inferData.setting : setting.colorInferSetting
    if (inferSetting.type === 'color') {
      return Object.keys(inferSetting)
        .map((key: string) => {
          if (key === 'light' || key === 'dark') {
            return inferSetting[key]
              .map((l: any) => {
                const varName = this.getVarName(
                  setting,
                  inferSetting.type,
                  inferData.key,
                  key,
                  l.toString()
                )
                return {
                  [varName]: new TinyColor(inferData.value)
                    .mix(key === 'light' ? this.colorWhite : this.colorBlack, l * 10)
                    .toHexString()
                }
              })
              .reduce((pre: any, next: any) => {
                return { ...pre, ...next }
              }, {})
          }
          return {}
        })
        .reduce((pre, next) => {
          return { ...pre, ...next }
        }, {})
    }
    return {}
  }

  /**
   *
   * @param themeSetting Subject settings
   * @param keyValueData Key value data
   * @returns            Key value data after screening
   */
  mapKeyValue = (themeSetting: ThemeSetting, keyValueData: KeyValueData) => {
    return Object.keys(keyValueData)
      .map((key: string) => {
        return {
          [this.updateKeyBySetting(key, themeSetting)]: keyValueData[key]
        }
      })
      .reduce((pre, next) => {
        return { ...pre, ...next }
      }, {})
  }
  /**
   * Modified according to the file.Key
   * @param key          key
   * @param themeSetting Subject settings
   * @returns
   */
  updateKeyBySetting = (key: string, themeSetting: ThemeSetting) => {
    return key.startsWith(themeSetting.startDivision)
      ? key
      : key.startsWith(themeSetting.namespace)
      ? themeSetting.startDivision + key
      : key.startsWith(themeSetting.division)
      ? themeSetting.startDivision + themeSetting.namespace
      : themeSetting.startDivision + themeSetting.namespace + themeSetting.division + key
  }
  /**
   *
   * @param setting    Subject settings
   * @param keyValue   Topic Key Value for Data
   * @param inferData External data
   * @returns Key values after the data
   */
  tokeyValueStyle = () => {
    return {
      ...this.mapInferData(this.themeSetting, this.inferData),
      ...this.mapKeyValue(this.themeSetting, this.keyValue)
    }
  }

  /**
   * willkeyValueThe object is converted toS
   * @param keyValue
   * @returns
   */
  toString = (keyValue: KeyValueData) => {
    const inner = Object.keys(keyValue)
      .map((key: string) => {
        return key + ':' + keyValue[key] + ';'
      })
      .join('')
    return `@charset "UTF-8";:root{${inner}}`
  }

  /**
   *
   * @param elNewStyle New variable style.
   */
  writeNewStyle = (elNewStyle: string) => {
    if (this.isFirstWriteStyle) {
      const style = document.createElement('style')
      style.innerText = elNewStyle
      document.head.appendChild(style)
      this.isFirstWriteStyle = false
    } else {
      if (document.head.lastChild) {
        document.head.lastChild.innerText = elNewStyle
      }
    }
  }

  /**
   * Modify the data and write.dom
   * @param updateInferData   Smooth Data Modification
   * @param updateKeyvalueData keyValueData Modification
   */
  updateWrite = (updateInferData?: UpdateInferData, updateKeyvalueData?: UpdateKeyValueData) => {
    this.update(updateInferData, updateKeyvalueData)
    const newStyle = this.tokeyValueStyle()
    const newStyleString = this.toString(newStyle)
    this.writeNewStyle(newStyleString)
  }

  /**
   * Modification of data
   * @param inferData
   * @param keyvalueData
   */
  update = (updateInferData?: UpdateInferData, updateKeyvalueData?: UpdateKeyValueData) => {
    if (updateInferData) {
      this.updateInferData(updateInferData)
    }
    if (updateKeyvalueData) {
      this.updateOrCreateKeyValueData(updateKeyvalueData)
    }
  }

  /**
   * Modifying external data Data can only be modified.,cannot be added.
   * @param inferData
   */
  updateInferData = (updateInferData: UpdateInferData) => {
    Object.keys(updateInferData).forEach((key) => {
      const findInfer = this.inferData.find((itemInfer) => {
        return itemInfer.key === key
      })
      if (findInfer) {
        findInfer.value = updateInferData[key]
      } else {
        this.inferData.push({ key, value: updateInferData[key] })
      }
    })
  }

  /**
   * Initial Theme
   */
  initDefaultTheme = () => {
    this.updateWrite()
  }
  /**
   * ModifiedKeyValueThe data
   * @param keyvalueData keyValueThe data
   */
  updateOrCreateKeyValueData = (updateKeyvalueData: UpdateKeyValueData) => {
    Object.keys(updateKeyvalueData).forEach((key) => {
      const newKey = this.updateKeyBySetting(key, this.themeSetting)
      this.keyValue[newKey] = updateKeyvalueData[newKey]
    })
  }
}

const install = (app: App) => {
  app.config.globalProperties.theme = new Theme(setting, keyValueData, inferData)
}
export default { install }
