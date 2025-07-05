<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useEntryStore } from '@/stores/entry'

const entryStore = useEntryStore()

// 直近1週間のEntry記録をチェック
const hasRecentEntries = computed(() => {
  const oneWeekAgo = new Date()
  oneWeekAgo.setDate(oneWeekAgo.getDate() - 7)
  
  return entryStore.entries.some(entry => {
    const entryDate = new Date(entry.reported_at)
    return entryDate >= oneWeekAgo
  })
})

// 直近のEntry記録数
const recentEntriesCount = computed(() => {
  const oneWeekAgo = new Date()
  oneWeekAgo.setDate(oneWeekAgo.getDate() - 7)
  
  return entryStore.entries.filter(entry => {
    const entryDate = new Date(entry.reported_at)
    return entryDate >= oneWeekAgo
  }).length
})

onMounted(async () => {
  try {
    await entryStore.fetchEntries()
  } catch (error) {
    // エラーハンドリングは必要に応じて追加
  }
})

</script>

<template>
  <v-container>
    <v-card>
      <v-card-title>
        <v-icon icon="mdi-home" class="me-2"></v-icon>
        ホーム
      </v-card-title>
      
      <v-card-text>
        <v-row>
          <v-col cols="12">
            <h3 class="text-h6 mb-4">直近1週間の記録状況</h3>
            
            <!-- 記録がある場合 -->
            <v-alert
              v-if="hasRecentEntries"
              type="success"
              variant="outlined"
              class="mb-4"
            >
              <v-icon icon="mdi-check-circle" slot="prepend"></v-icon>
              <strong>記録済み</strong>
              <div class="text-body-2 mt-1">
                直近1週間で{{ recentEntriesCount }}件の記録が投稿されています。
              </div>
            </v-alert>
            
            <!-- 記録がない場合 -->
            <v-alert
              v-else
              type="warning"
              variant="outlined"
              class="mb-4"
            >
              <v-icon icon="mdi-alert-circle" slot="prepend"></v-icon>
              <strong>記録がありません</strong>
              <div class="text-body-2 mt-1">
                直近1週間で記録が投稿されていません。記録を追加することをお勧めします。
              </div>
            </v-alert>
            
            <v-btn
              prepend-icon="mdi-plus"
              color="primary"
              variant="text"
              to="/entries"
            >
              記録を追加
            </v-btn>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<style scoped>

</style>