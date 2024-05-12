<template>
  <div>
    <el-button v-hasPermission="'USER:DELETE'">User removes permissions</el-button>
    <el-button v-hasPermission="'USER:READ'">Users only read permissions.</el-button>
    <el-button v-hasPermission="new Role('USER')">The ordinary user role.</el-button>
    <el-button v-hasPermission="[new Role('ADMIN'), new Role('USER')]"
      >Ordinary user or administrator</el-button
    >
    <el-button v-hasPermission="{ permission: ['USER:READ', new Role('USER')], compare: 'AND' }"
      >Ordinary characters and users only read permits</el-button
    >

    The first page
  </div>
</template>
<script setup lang="ts">
import { Role } from '@/utils/permission/type'
</script>
<style lang="scss" scoped></style>
