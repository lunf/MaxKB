<template>
  <el-form
    @submit.prevent
    ref="ruleFormRef"
    label-width="130px"
    label-suffix=":"
    v-loading="loading"
    v-bind="$attrs"
  >
    <slot :form_value="formValue"></slot>
    <template v-for="item in formFieldList" :key="item.field">
      <FormItem
        ref="formFieldRef"
        :key="item.field"
        v-if="show(item)"
        @change="change(item, $event)"
        v-bind:modelValue="formValue[item.field]"
        :formfield="item"
        :trigger="trigger"
        :view="view"
        :initDefaultData="initDefaultData"
        :defaultItemWidth="defaultItemWidth"
        :other-params="otherParams"
        :form-value="formValue"
        :formfield-list="formFieldList"
        :parent_field="parent_field"
      >
      </FormItem>
    </template>
  </el-form>
</template>
<script lang="ts" setup>
import type { Dict } from '@/api/type/common'
import FormItem from '@/components/dynamics-form/FormItem.vue'
import type { FormField } from '@/components/dynamics-form/type'
import { ref, onMounted, watch, type Ref } from 'vue'
import type { FormInstance } from 'element-plus'
import triggerApi from '@/api/provider'
import type Result from '@/request/Result'
import _ from 'lodash'

defineOptions({ name: 'dynamicsForm' })

const props = withDefaults(
  defineProps<{
    // Page rendering data
    render_data: Promise<Result<Array<FormField>>> | string | Array<FormField>
    // Other parameters required for the call interface
    otherParams?: any
    // Only to read.
    view?: boolean
    // Each width.
    defaultItemWidth?: string

    parent_field?: string

    modelValue?: Dict<any>
  }>(),
  { view: false, defaultItemWidth: '75%', otherParams: () => {} }
)

const formValue = ref<Dict<any>>({})

const loading = ref<boolean>(false)

const formFieldList = ref<Array<FormField>>([])

const ruleFormRef = ref<FormInstance>()

const formFieldRef = ref<Array<InstanceType<typeof FormItem>>>([])
/**
 * Currently fieldShould show
 * @param field
 */
const show = (field: FormField) => {
  if (field.relation_show_field_dict) {
    let keys = Object.keys(field.relation_show_field_dict)
    for (const index in keys) {
      const key = keys[index]
      let v = _.get(formValue.value, key)
      if (v && v !== undefined && v !== null) {
        let values = field.relation_show_field_dict[key]
        if (values && values.length > 0) {
          return values.includes(v)
        } else {
          return true
        }
      } else {
        return false
      }
    }
  }
  return true
}

const emit = defineEmits(['update:modelValue'])
/**
 * Modification of the form field
 * @param field
 * @param value
 */
const change = (field: FormField, value: any) => {
  formValue.value[field.field] = value
}

watch(
  formValue,
  () => {
    emit('update:modelValue', formValue.value)
  },
  { deep: true }
)

/**
 * the trigger.,User receives subforms or The option down.
 * @param field
 * @param loading
 */
const trigger = (field: FormField, loading: Ref<boolean>) => {
  if (field.provider && field.method) {
    return triggerApi
      .trigger(
        field.provider,
        field.method,
        {
          ...props.otherParams,
          ...formValue.value
        },
        loading
      )
      .then((ok) => {
        if (field.trigger_type === 'CHILD_FORMS') {
          field.children = ok.data as Array<FormField>
        } else {
          field.option_list = ok.data as Array<any>
        }
      })
  }
  return Promise.resolve([])
}
/**
 * Initialization of data
 */
const initDefaultData = (formField: FormField) => {
  if (
    formField.default_value &&
    (formValue.value[formField.field] === undefined ||
      formValue.value[formField.field] === null ||
      !formValue.value[formField.field])
  ) {
    formValue.value[formField.field] = formField.default_value
  }
}

onMounted(() => {
  render(props.render_data, {})
})

const render = (
  render_data: string | Array<FormField> | Promise<Result<Array<FormField>>>,
  data?: Dict<any>
) => {
  if (typeof render_data == 'string') {
    triggerApi.get(render_data, {}, loading).then((ok) => {
      formFieldList.value = ok.data
    })
  } else if (render_data instanceof Array) {
    formFieldList.value = render_data
  } else {
    render_data.then((ok) => {
      formFieldList.value = ok.data
    })
  }
  if (data) {
    formValue.value = data
  }
}
/**
 * Examination functions
 */
const validate = () => {
  return Promise.all([
    ...formFieldRef.value.map((item) => item.validate()),
    ruleFormRef.value ? ruleFormRef.value.validate() : Promise.resolve()
  ])
}

// Exposure to obtain the current form data function
defineExpose({
  initDefaultData,
  validate,
  render,
  ruleFormRef
})
</script>
<style lang="scss" scope></style>
