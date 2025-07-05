<script setup lang="ts">
import { useInfoStore } from '@/stores/info'

const infoStore = useInfoStore()
</script>

<template>
  <v-snackbar 
    v-model="infoStore.visible"
    :color="infoStore.color || undefined"
    multi-line
    >
    {{ infoStore.message }}
  </v-snackbar>
</template>