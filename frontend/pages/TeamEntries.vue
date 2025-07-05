<script setup lang="ts">
import { useTeamEntryStore } from '@/stores/team-entry'
import { onMounted } from 'vue'

const teamEntryStore = useTeamEntryStore()

onMounted(async () => {
  try {
    await teamEntryStore.fetchTeamEntries()
  } catch (error) {
    // エラーハンドリングは必要に応じて追加
  }
})
</script>

<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <v-card-title>TeamEntries</v-card-title>
      </v-col>
    </v-row>

    <v-row>
      <v-col v-for="team in teamEntryStore.teamEntries" :key="team.id" cols="12" md="6">
        <v-card elevation="2" class="mb-4">
          <v-card-title class="bg-primary text-white">
            <v-icon left>mdi-account-group</v-icon>
            {{ team.name }}
          </v-card-title>

          <v-card-text class="pa-0">
            <v-list>
              <v-list-item v-for="user in team.users" :key="user.id" class="px-4 py-2">
                <v-list-item-title class="font-weight-medium d-flex align-center">
                  <v-avatar size="32" color="secondary" class="mr-3">
                    <v-icon>mdi-account</v-icon>
                  </v-avatar>
                  {{ user.name }}
                  <v-spacer />
                  <div class="d-flex gap-2">
                    <v-chip v-if="user.entries.stress_values.length > 0"
                      variant="text" prepend-icon="mdi-alert-circle" size="small">
                      {{ user.entries.stress_values[user.entries.stress_values.length - 1] }}
                    </v-chip>
                    <v-chip v-if="user.entries.motivation_values.length > 0"
                      variant="text" prepend-icon="mdi-heart" size="small">
                      {{ user.entries.motivation_values[user.entries.motivation_values.length - 1] }}
                    </v-chip>
                  </div>
                </v-list-item-title>
                <div class="w-100">
                  <!-- ストレススコアグラフ -->
                  <v-list-item-subtitle class="mb-2 d-flex align-center">
                    <v-icon size="small" class="mr-1">mdi-alert-circle</v-icon>
                    stress
                  </v-list-item-subtitle>
                  <v-sheet color="grey-lighten-5" rounded class="pa-2 mb-4">
                    <v-sparkline :gradient="['#f72047', '#ffd200', '#1feaea']" :line-width="3"
                      :labels="user.entries.labels" :model-value="user.entries.stress_values" :smooth="16" stroke-linecap="round"
                      padding="8" max="100" min="0" height="80" show-labels></v-sparkline>
                  </v-sheet>

                  <!-- モチベーションスコアグラフ -->
                  <v-list-item-subtitle class="mb-2 d-flex align-center">
                    <v-icon size="small" class="mr-1">mdi-heart</v-icon>
                    motivation
                  </v-list-item-subtitle>
                  <v-sheet color="grey-lighten-5" rounded class="pa-2">
                    <v-sparkline :gradient="['#f72047', '#ffd200', '#1feaea']" :line-width="3"
                      :labels="user.entries.labels" :model-value="user.entries.motivation_values" :smooth="16" stroke-linecap="round"
                      padding="8" max="100" min="0" height="80" show-labels></v-sparkline>
                  </v-sheet>
                </div>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<style scoped>
</style>