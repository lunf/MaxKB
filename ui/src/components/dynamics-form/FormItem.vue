<template>
  <el-form-item
    v-loading="loading"
    :style="formItemStyle"
    :label="formfield.label"
    :prop="formfield.field"
    :key="formfield.field"
    :rules="rules"
  >
    <template #label v-if="formfield.label">
      <FormItemLabel :form-field="formfield"></FormItemLabel>
    </template>
    <component
      ref="componentFormRef"
      :view="view"
      v-model="itemValue"
      :is="formfield.input_type"
      :form-field="formfield"
      :other-params="otherParams"
      :style="componentStyle"
      :field="formfield.field"
      v-bind="attrs"
      :formfield-list="formfieldList"
    ></component>
  </el-form-item>
</template>
<script setup lang="ts">
import { ref, computed, onMounted, type Ref } from 'vue'
import type { FormField } from '@/components/dynamics-form/type'
import FormItemLabel from './FormItemLabel.vue'
import type { Dict } from '@/api/type/common'
import bus from '@/bus'
const props = defineProps<{
  // Double linked value.
  modelValue: any

  // FormsItem
  formfield: FormField
  // Only to read.
  view: boolean
  // Other parameters required for the call interface
  otherParams: any
  // obtainedOptions
  trigger: (formItem: FormField, loading: Ref<boolean>) => Promise<any>
  // Initialization of data
  initDefaultData: (formItem: FormField) => void
  // Each width.
  defaultItemWidth: string
  // Forms collect data
  formValue: Dict<any>

  formfieldList: Array<FormField>

  parent_field?: string
}>()

const emit = defineEmits(['change'])

const loading = ref<boolean>(false)

const itemValue = computed({
  get: () => {
    return props.modelValue
  },
  set: (value: any) => {
    emit('change', value)
    if (props.parent_field) {
      bus.emit(props.parent_field + '.' + props.formfield.field, value)
    } else {
      bus.emit(props.formfield.field, value)
    }
  }
})
const componentFormRef = ref<any>()

const props_info = computed(() => {
  return props.formfield.props_info ? props.formfield.props_info : {}
})
/**
 * Forms item style
 */
const formItemStyle = computed(() => {
  return props_info.value.item_style ? props_info.value.item_style : {}
})

/**
 * Forms errors.Msg
 */
const errMsg = computed(() => {
  return props_info.value.err_msg ? props_info.value.err_msg : props.formfield.label + 'cannot be empty.'
})

/**
 * Examination
 */
const rules = computed(() => {
  return props_info.value.rules
    ? props_info.value.rules
    : {
        message: errMsg.value,
        trigger: 'blur',
        required: props.formfield.required === false ? false : true
      }
})

/**
 * The component style.
 */
const componentStyle = computed(() => {
  return props_info.value.style ? props_info.value.style : {}
})

/**
 * The componentattrs
 */
const attrs = computed(() => {
  return props.formfield.attrs ? props.formfield.attrs : {}
})

onMounted(() => {
  props.initDefaultData(props.formfield)
  if (props.formfield.provider && props.formfield.method) {
    props.trigger(props.formfield, loading)
  }
  // Listen to field changes.
  const trigger_field_dict = props.formfield.relation_trigger_field_dict
  if (trigger_field_dict) {
    const keys = Object.keys(trigger_field_dict)
    keys.forEach((key) => {
      const value = trigger_field_dict[key]
      // Added Relationship
      bus.on(key, (v: any) => {
        if (value && value.length > 0) {
          if (value.includes(v)) {
            props.trigger(props.formfield, loading)
          }
        } else {
          props.trigger(props.formfield, loading)
        }
      })
    })
  }
})

const validate = () => {
  if (props.formfield.trigger_type === 'CHILD_FORMS' && componentFormRef.value) {
    return componentFormRef.value.validate()
  }
  return Promise.resolve()
}
defineExpose({ validate })
</script>
<style lang="scss" scoped></style>
