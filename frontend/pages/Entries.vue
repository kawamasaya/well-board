<script setup lang="ts">
import { onMounted, ref, shallowRef } from 'vue'
import { useEntryStore } from '@/stores/entry'
import { useAuthStore } from '@/stores/auth'
import { useTeamStore } from '@/stores/team'
import { useInfoStore } from '@/stores/info'
import { useDate } from 'vuetify'
import { validationRules } from '@/utils/validation'

const authStore = useAuthStore()
const teamStore = useTeamStore()
const entryStore = useEntryStore()
const infoStore = useInfoStore()
const adapter = useDate()

const dataTable = {
  headers: [
    { title: '報告日', align: 'start' as const, key: 'reported_at' },
    { title: 'team', align: 'start' as const, key: 'team' },
    { title: 'Q&A', align: 'start' as const, key: 'q_and_a' },
    { title: 'stress', align: 'end' as const, key: 'stress_score' },
    { title: 'motivation', align: 'end' as const, key: 'motivation_score' },
  ],
}

const DEFAULT_RECORD = {
  team: null as number | null,
  reported_at: new Date(),
  questions: {},
  answers: {}
}

const record = ref({ ...DEFAULT_RECORD })
const dialog = shallowRef(false)
const isEditing = shallowRef(false)
const entryFormRef = ref<any>(null)

function updateQuestions(teamId: number) {
  const selectedTeam = teamStore.teams.find(team => team.id === teamId)
  record.value.questions = selectedTeam?.questions || {}
  // 回答もリセット
  record.value.answers = {}
}


onMounted(async () => {
  try {
    await entryStore.fetchEntries()
  } catch (error) {
    // エラーハンドリングは必要に応じて追加
  }
})

function format(date: Date) {
  return adapter.toISO(date)
}

// チーム選択が変更されたときのハンドラ
function onTeamChange(teamId: number | null) {
  if (teamId) {
    updateQuestions(teamId)
  }
}

async function add() {
  try {
    isEditing.value = false
    record.value = { ...DEFAULT_RECORD }
    await teamStore.fetchTeams()

    // 初期チームの質問を設定
    if (authStore.user?.teams?.[0]) {
      record.value.team = authStore.user.teams[0]
      updateQuestions(authStore.user.teams[0])
    }
    dialog.value = true
  } catch (error) {
    // エラーハンドリングは必要に応じて追加
  }
}

async function save() {
  const { valid } = await entryFormRef.value.validate()
  if (!valid) {
    infoStore.add("入力内容を確認してください", "error")
    return
  }
  
  if (!record.value.team) {
    infoStore.add("チームを選択してください", "error")
    return
  }
  
  try {
    // チームが選択されていることを確認済みなので、型アサーションで安全にキャスト
    const entryData = {
      ...record.value,
      team: record.value.team!  // non-null assertion
    }
    await entryStore.addEntries(entryData)

    dialog.value = false

    // 記録一覧を再取得
    await entryStore.fetchEntries()
  } catch (error) {
    // エラーハンドリングは必要に応じて追加
  }
}
</script>

<template>
  <v-container>
    <v-card>
      <v-card-title>
        Entries
      </v-card-title>
      <v-data-table 
        :headers="dataTable.headers" 
        :items="entryStore.entries" 
        class="elevation-1" 
        item-value="id"
        :items-per-page="5" 
        :items-per-page-options="[5, 10, 25]"
      >
        <template v-slot:top>
          <v-toolbar flat>
            <v-toolbar-title>
              <v-icon color="medium-emphasis" icon="mdi-book-multiple" size="x-small" start></v-icon>

            </v-toolbar-title>

            <v-btn class="me-2" prepend-icon="mdi-plus" rounded="lg" text="Add" @click="add"></v-btn>
          </v-toolbar>
        </template>

        <template v-slot:item.reported_at="{ item }">
          <div class="d-flex align-center">
            <v-icon icon="mdi-calendar" size="small" class="me-2"></v-icon>
            <span class="text-body-1">{{ item.reported_at }}</span>
          </div>
        </template>

        <template v-slot:item.team="{ item }">
            {{ item.team.name }}
        </template>

        <template v-slot:item.q_and_a="{ item }">
          <v-expansion-panels variant="accordion" class="my-2">
            <v-expansion-panel>
              <v-expansion-panel-title>
                <v-icon icon="mdi-comment-question-outline" class="me-2"></v-icon>
                質問・回答を表示 ({{ Object.keys((item as any).questions || {}).length }}件)
              </v-expansion-panel-title>
              <v-expansion-panel-text>
                <div v-for="(value, key) in (item as any).questions" :key="key" class="mb-3">
                  <v-card variant="outlined" class="pa-3">
                    <v-card-title class="text-subtitle-2 pb-2">
                      <v-icon icon="mdi-help-circle" size="small" class="me-1"></v-icon>
                      質問{{ key }}
                    </v-card-title>
                    <v-card-text class="pt-0">
                      <p class="text-body-2 mb-2">{{ value }}</p>
                      <v-divider class="my-2"></v-divider>
                      <div class="d-flex align-center">
                        <v-icon icon="mdi-account-voice" size="small" class="me-1"></v-icon>
                        <span class="text-subtitle-2 me-2">回答:</span>
                        <span v-if="item.answers && item.answers[key]" class="text-body-2">
                          {{ item.answers[key] }}
                        </span>
                        <v-chip v-else color="grey" size="small" variant="outlined">未回答</v-chip>
                      </div>
                    </v-card-text>
                  </v-card>
                </div>
              </v-expansion-panel-text>
            </v-expansion-panel>
          </v-expansion-panels>
        </template>
        
      </v-data-table>
    </v-card>
  </v-container>



  <v-dialog v-model="dialog" max-width="500">
    <v-card :title="`${isEditing ? 'Edit' : 'Add'} a Report`">
      <v-card-text>
        <v-form ref="entryFormRef">
          <v-row>
            <v-col cols="12" md="6">
              <VDateInput v-model="record.reported_at" label="Report Date" :display-format="format" max-width="368">
              </VDateInput>
            </v-col>

            <v-col cols="12" md="6">
              <v-select 
                v-model="record.team" 
                :items="teamStore.teams" 
                label="Team" 
                item-title="name" 
                item-value="id"
                :rule="validationRules.entryTeam"
                @update:modelValue="onTeamChange"
              ></v-select>
            </v-col>

          </v-row>

          <v-list-item v-for="(question, key) in record.questions" v-if="record.questions" :key="key" class="mb-4">
            <v-list-item-title>質問 {{ key }}: {{ question }}</v-list-item-title>
            <v-text-field 
              v-model="record.answers[key]" 
              :label="'回答 ' + key"
            ></v-text-field>
          </v-list-item>
        </v-form>
      </v-card-text>
          
      <v-divider></v-divider>

      <v-card-actions class="bg-surface-light">
        <v-btn text="CANCEL" variant="plain" @click="dialog = false"></v-btn>

        <v-spacer></v-spacer>

        <v-btn text="SAVE" @click="save"></v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<style scoped>
.v-data-table {
  border-radius: 8px;
}

.v-expansion-panel {
  margin: 4px 0;
}

.v-chip {
  text-shadow: none;
}
</style>