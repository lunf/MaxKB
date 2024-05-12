<template>
  <div style="width: 1024px">
    <DynamicsForm v-model="form_data" :render_data="damo_data" ref="dynamicsFormRef">
      <template #default="scope">
        <el-form-item label="Other fields">
          <el-input v-model="scope.form_value['zha']" /> </el-form-item
      ></template>
    </DynamicsForm>
    <el-button @click="click">Let me test.</el-button>
  </div>
</template>
<script setup lang="ts">
import type { FormField } from '@/components/dynamics-form/type'
import DynamicsForm from '@/components/dynamics-form/index.vue'
import { ref } from 'vue'
import type { Dict } from '@/api/type/common'
const damo_data: Array<FormField> = [
  { field: 'name', input_type: 'PasswordInput', label: 'User Name', required: false },
  {
    field: 'array_object_card_field',
    input_type: 'ArrayObjectCard',
    label: 'Testing',
    trigger_type: 'CHILD_FORMS',
    attrs: { 'label-width': '120px', 'label-suffix': ':ssss', 'label-position': 'top' },
    required: false,
    children: [
      { field: 'name1', input_type: 'TextInput', label: 'User Name1' },
      { field: 'name2', input_type: 'TextInput', label: 'User Name2' },
      { field: 'name3', input_type: 'TextInput', label: 'User Name3' }
    ]
  },
  {
    field: 'object_card_field',
    input_type: 'ObjectCard',
    label: 'Testing',
    trigger_type: 'CHILD_FORMS',
    attrs: { 'label-width': '120px', 'label-suffix': ':ssss', 'label-position': 'left' },
    required: false,
    children: [
      { field: 'name1', input_type: 'TextInput', label: 'User Name1' },
      { field: 'name2', input_type: 'TextInput', label: 'User Name2' },
      { field: 'name3', input_type: 'TextInput', label: 'User Name3' }
    ]
  },
  {
    field: 'tab_card_field',
    input_type: 'TabCard',
    label: 'Testing',
    trigger_type: 'CHILD_FORMS',
    attrs: { 'label-width': '120px', 'label-suffix': ':ssss', 'label-position': 'left' },
    required: false,
    relation_trigger_field_dict: {
      'array_object_card_field.0.name1': ['111']
    },
    props_info: { tabs_label: 'Users' },
    children: [
      { field: 'name1', input_type: 'TextInput', label: 'User Name1' },
      { field: 'name2', input_type: 'TextInput', label: 'User Name2' },
      { field: 'name3', input_type: 'TextInput', label: 'User Name3' }
    ]
  },
  {
    field: 'single_select_field',
    input_type: 'SingleSelect',
    label: 'Testing of Selection',
    required: true,
    attrs: { placeholder: 'Please choose' },
    option_list: [
      {
        key: 'Tested',
        value: 'test'
      },
      {
        key: 'Tested1',
        value: 'test1'
      }
    ]
  },
  {
    field: 'multi_select_field',
    input_type: 'MultiSelect',
    default_value: ['test1'],
    relation_show_field_dict: {
      'object_card_field.name1': []
    },
    label: 'Testing a lot.',
    required: true,
    attrs: { placeholder: 'Please choose' },
    option_list: [
      {
        key: 'Tested',
        value: 'test'
      },
      {
        key: 'Tested1',
        value: 'test1'
      }
    ]
  },
  {
    field: 'radio_field',
    input_type: 'Radio',
    label: 'Testing of Selection',
    required: true,
    attrs: { placeholder: 'Please choose' },
    option_list: [
      {
        key: 'Tested',
        value: 'test'
      },
      {
        key: 'Tested1',
        value: 'test1'
      }
    ]
  },
  {
    field: 'radio_button_field',
    input_type: 'RadioButton',
    label: 'Testing of Selection',
    required: true,
    attrs: { placeholder: 'Please choose' },
    option_list: [
      {
        key: 'Tested',
        value: 'test'
      },
      {
        key: 'Tested1',
        value: 'test1'
      }
    ]
  },
  {
    field: 'radio_card_field',
    input_type: 'RadioCard',
    label: 'Testing of Selection1',
    required: true,
    attrs: { placeholder: 'Please choose' },
    option_list: [
      {
        key: 'Tested',
        value: 'test'
      },
      {
        key: 'Tested111111',
        value: 'test1'
      }
    ]
  },
  {
    field: 'table_radio_field',
    input_type: 'TableRadio',
    label: 'Selected forms',
    required: true,
    attrs: { placeholder: 'Please choose' },
    props_info: {
      active_msg: 'Currently elected',
      table_columns: [
        {
          property: '`${row.key}${row.number}`',
          label: 'The name',
          type: 'eval'
        },
        {
          property: 'ProgressTableItem',
          label: 'Number of values',
          type: 'component',
          value_field: 'number',
          attrs: {
            color: [
              { color: '#f56c6c', percentage: 20 },
              { color: '#e6a23c', percentage: 40 },
              { color: '#5cb87a', percentage: 60 },
              { color: '#1989fa', percentage: 80 },
              { color: '#6f7ad3', percentage: 100 }
            ]
          },
          props_info: {
            view_card: [
              {
                type: 'eval',
                title: 'Tested',
                value_field:
                  '`${parseFloat(row.number).toLocaleString("zh-CN",{style: "decimal",maximumFractionDigits:1})}%&nbsp;&nbsp;&nbsp;`'
              },
              {
                type: 'eval',
                title: 'The name',
                value_field: '`${row.key}&nbsp;&nbsp;&nbsp;`'
              }
            ]
          }
        }
      ],
      style: { width: '500px' }
    },
    option_list: [
      {
        key: 'Tested',
        value: 'test',
        number: 10
      },
      {
        key: 'Tested111111',
        value: 'test1',
        number: 100
      }
    ]
  },
  {
    field: 'table_checkbox_field',
    input_type: 'TableCheckbox',
    label: 'Number of selected',
    required: true,
    attrs: { placeholder: 'Please choose' },
    props_info: {
      active_msg: 'Currently elected',
      table_columns: [
        {
          property: '`${row.key}${row.number}`',
          label: 'The name',
          type: 'eval'
        },
        {
          property: 'ProgressTableItem',
          label: 'Number of values',
          type: 'component',
          value_field: 'number',
          attrs: {
            color: [
              { color: '#f56c6c', percentage: 20 },
              { color: '#e6a23c', percentage: 40 },
              { color: '#5cb87a', percentage: 60 },
              { color: '#1989fa', percentage: 80 },
              { color: '#6f7ad3', percentage: 100 }
            ]
          },
          props_info: {
            view_card: [
              {
                type: 'eval',
                title: 'Tested',
                value_field:
                  '`${parseFloat(row.number).toLocaleString("zh-CN",{style: "decimal",maximumFractionDigits:1})}%&nbsp;&nbsp;&nbsp;`'
              },
              {
                type: 'eval',
                title: 'The name',
                value_field: '`${row.key}&nbsp;&nbsp;&nbsp;`'
              }
            ]
          }
        }
      ],
      style: { width: '500px' }
    },
    option_list: [
      {
        key: 'Tested',
        value: 'test',
        number: 10
      },
      {
        key: 'Tested111111',
        value: 'test1',
        number: 100
      }
    ]
  }
]
const form_data = ref<Dict<any>>({})
const dynamicsFormRef = ref<InstanceType<typeof DynamicsForm>>()
const click = () => {
  dynamicsFormRef.value?.validate()
}
</script>
<style lang="scss" scope></style>
