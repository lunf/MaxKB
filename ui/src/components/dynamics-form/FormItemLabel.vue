<template>
  {{ formField.label }}
</template>
<script setup lang="ts">
import type { FormField } from '@/components/dynamics-form/type'
const props = defineProps<{
  // FormsItem
  formField: FormField
}>()
</script>
<style lang="scss" scoped></style>
