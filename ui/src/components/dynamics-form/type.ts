import type { Dict } from '@/api/type/common'

interface ViewCardItem {
  /**
   * Type of
   */
  type: 'eval' | 'default'
  /**
   * The title
   */
  title: string
  /**
   * Value Different according to type. Value is different. default= row[value_field] eval `${parseFloat(row.number).toLocaleString("zh-CN",{style: "decimal",maximumFractionDigits:1})}%&nbsp;&nbsp;&nbsp;`
   */
  value_field: string
}

interface TableColumn {
  /**
   * Fields|Name of components|Calculable template characters.
   */
  property: string
  /**
   *The headline
   */
  label: string
  /**
   * Table Data Fields
   */
  value_field?: string

  attrs?: Attrs
  /**
   * Type of
   */
  type: 'eval' | 'component' | 'default'

  props_info?: PropsInfo
}
interface ColorItem {
  /**
   * The Color#f56c6c
   */
  color: string
  /**
   * Progress
   */
  percentage: number
}
interface Attrs {
  /**
   * Suggestions
   */
  placeholder?: string
  /**
   * The length of the label，for example '50px'。 as Form The direct subelement. form-item We will inherit the value.。 can be used auto。
   */
  labelWidth?: string
  /**
   * Posts tagged in the form.
   */
  labelSuffix?: string
  /**
   * Location of the star.。
   */
  requireAsteriskPosition?: 'left' | 'right'

  color?: Array<ColorItem>

  [propName: string]: any
}
interface PropsInfo {
  /**
   * Choose the table.card
   */
  view_card?: Array<ViewCardItem>
  /**
   * Selection of Table
   */
  table_columns?: Array<TableColumn>
  /**
   * selected message
   */
  active_msg?: string

  /**
   * The component style.
   */
  style?: Dict<any>

  /**
   * el-form-item Style
   */
  item_style?: Dict<any>
  /**
   * Forms of Examination This andelementLike the test.
   */
  rules?: Dict<any>
  /**
   * presumed No advice for a vacuum school.
   */
  err_msg?: string
  /**
   *tabswhen used.
   */
  tabs_label?: string

  [propName: string]: any
}

interface FormField {
  field: string
  /**
   * Type of Input Box
   */
  input_type: string
  /**
   * The Tip
   */
  label?: string
  /**
   * Is it must fill.
   */
  required?: boolean
  /**
   * The default value
   */
  default_value?: any
  /**
   *  {field:field_value_list} stated in fieldis worth ,and worth it.field_value_listIn the show.
   */
  relation_show_field_dict?: Dict<Array<any>>
  /**
   * {field:field_value_list} stated in fieldis worth ,and worth it.field_value_listIn the middle Implementation of functions The data
   */
  relation_trigger_field_dict?: Dict<Array<any>>
  /**
   * Type of executor  OPTION_LISTrequestedOption_listThe data CHILD_FORMSApplication form
   */
  trigger_type?: 'OPTION_LIST' | 'CHILD_FORMS'
  /**
   * The frontattrThe data
   */
  attrs?: Attrs
  /**
   * Other additional information
   */
  props_info?: PropsInfo
  /**
   * Selected fields.field
   */
  text_field?: string
  /**
   * Lower Choice value
   */
  value_field?: string
  /**
   * Selected data.
   */
  option_list?: Array<any>
  /**
   * Suppliers
   */
  provider?: string
  /**
   * Execution of functions.
   */
  method?: string

  children?: Array<FormField>
}
export type { FormField }
