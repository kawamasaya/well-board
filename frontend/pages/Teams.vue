<script setup lang="ts">
import { computed, onMounted, ref, shallowRef } from 'vue'
import { useTeamStore } from '@/stores/team'
import { useUserStore } from '@/stores/user'
import { useInfoStore } from '@/stores/info'
import type { QuestionSet, TeamDetail } from '@/types'
import { validationRules } from '@/utils/validation'

const teamStore = useTeamStore()
const userStore = useUserStore()
const infoStore = useInfoStore()

const dataTable = {
  headers: [
    { title: 'チーム', align: 'start' as const, key: 'name' },
    { title: '質問内容', align: 'start' as const, key: 'questions' },
    { title: 'マネージャー', align: 'start' as const, key: 'managers' },
    { title: 'アクション', key: 'actions', sortable: false, align: 'center' as const }
  ]
}

const DEFAULT_RECORD = {
  name: '',
  questions: {},
  managers: [] as number[]
}

const record = ref({ ...DEFAULT_RECORD })
const dialog = shallowRef(false)
const isEditing = shallowRef(false)
const editingTeamId = ref<number | null>(null)
const deleteDialog = shallowRef(false)
const deletingTeam = ref<TeamDetail | null>(null)
const teamFormRef = ref<any>(null)

// 質問リスト（固定3つ）
const questionsList = ref([
  { id: 1, text: '' },
  { id: 2, text: '' },
  { id: 3, text: '' }
])

// 質問リストをquestions オブジェクトに変換
const questionsObject = computed((): QuestionSet => {
  const questions: QuestionSet = {}
  questionsList.value.forEach((question, index) => {
    if (question.text.trim()) {
      questions[(index + 1).toString()] = question.text.trim()
    }
  })
  return questions
})

onMounted(async () => {
  try {
    await teamStore.fetchTeams()
  } catch (error) {
    // エラーハンドリングは必要に応じて追加
  }
})

async function add() {
  try {
    await userStore.fetchUsers()
    isEditing.value = false
    record.value = { ...DEFAULT_RECORD }
    // 質問リストを初期化
    questionsList.value = [
      { id: 1, text: '' },
      { id: 2, text: '' },
      { id: 3, text: '' }
    ]
    record.value.managers = []
    dialog.value = true
  } catch (error) {
    // エラーハンドリングは必要に応じて追加
  }
}

async function save() {

  const { valid } = await teamFormRef.value.validate()
  if (!valid) {
    infoStore.add("入力内容を確認してください", "error")
    return
  }

  try {
    // 質問リストを questions オブジェクトに変換
    record.value.questions = questionsObject.value

    if (isEditing.value && editingTeamId.value) {
      // 編集の場合
      await teamStore.updateTeam(editingTeamId.value, record.value)
    } else {
      // 新規作成の場合
      await teamStore.addTeam(record.value)
    }

    dialog.value = false
    // チーム一覧を再取得
    await teamStore.fetchTeams()
  } catch (error) {
    // エラーハンドリングは必要に応じて追加
  }
}

// 質問数を取得
function getQuestionCount(questions?: QuestionSet) {
  if (!questions || typeof questions !== 'object') return 0
  return Object.keys(questions).length
}

// マネージャー候補（ADMINまたはMANAGERのみ）
const managerCandidates = computed(() => {
  return userStore.users.filter(user => user.role && user.role <= 3) // ADMIN=2, MANAGER=3
})

// チーム編集
async function editTeam(team: TeamDetail) {
  try {
    await userStore.fetchUsers()
    isEditing.value = true
    editingTeamId.value = team.id
    record.value = {
      name: team.name,
      questions: team.questions ? { ...team.questions } : {},
      managers: (team.managers || []).map(manager => typeof manager === 'number' ? manager : manager.id)
    }

    // 質問リストに既存の質問を設定
    const questions = team.questions || {}
    questionsList.value = [
      { id: 1, text: (typeof questions['1'] === 'string' ? questions['1'] : '') || '' },
      { id: 2, text: (typeof questions['2'] === 'string' ? questions['2'] : '') || '' },
      { id: 3, text: (typeof questions['3'] === 'string' ? questions['3'] : '') || '' }
    ]

    dialog.value = true
  } catch (error) {
    // エラーハンドリングは必要に応じて追加
  }
}

// チーム削除確認ダイアログを表示
function deleteTeam(team: TeamDetail) {
  deletingTeam.value = team
  deleteDialog.value = true
}

// チーム削除を実行
async function confirmDelete() {
  if (!deletingTeam.value) return

  try {
    await teamStore.deleteTeam(deletingTeam.value.id)
    deleteDialog.value = false
    deletingTeam.value = null
    // チーム一覧を再取得
    await teamStore.fetchTeams()
  } catch (error) {
    // エラーハンドリングは必要に応じて追加
  }
}

// チーム削除をキャンセル
function cancelDelete() {
  deleteDialog.value = false
  deletingTeam.value = null
}

</script>

<template>
  <v-container>
    <v-card>
      <v-card-title>
        Teams
      </v-card-title>
      <v-data-table 
        :headers="dataTable.headers" 
        :items="teamStore.teams" 
        :loading="teamStore.isLoading"
        class="elevation-1" 
        item-value="id" 
        :items-per-page="25" 
        :items-per-page-options="[25, 50, 100]"
      >
        <template v-slot:top>
          <v-toolbar flat>
            <v-toolbar-title>
              <v-icon icon="mdi-account-group" size="small" start></v-icon>
            </v-toolbar-title>

            <v-spacer></v-spacer>

            <v-btn class="me-2" prepend-icon="mdi-plus" rounded="lg" text="Add" @click="add"></v-btn>
          </v-toolbar>
        </template>

        <!-- チーム名の表示 -->
        <template v-slot:item.name="{ item }">
          <div class="d-flex align-center py-2">
            <v-avatar color="primary" size="40" class="me-3">
              <v-icon icon="mdi-account-group" color="white"></v-icon>
            </v-avatar>
            <div>
              <div class="text-subtitle-1 font-weight-bold">{{ item.name }}</div>
              <div class="text-caption text-medium-emphasis">ID: {{ item.id }}</div>
            </div>
          </div>
        </template>

        <!-- マネージャーの表示 -->
        <template v-slot:item.managers="{ item }">
            <v-chip
              v-for="manager in item.managers"
              :key="manager.id"
              variant="outlined"
            >
              <v-icon icon="mdi-account-star" size="x-small" start></v-icon>
              {{ manager.name }}
            </v-chip>
        </template>

        <!-- 質問内容の表示 -->
        <template v-slot:item.questions="{ item }">
          <v-expansion-panels v-if="getQuestionCount(item.questions) > 0" variant="accordion" class="my-1">
            <v-expansion-panel>
              <v-expansion-panel-title class="text-body-2">
                <v-icon icon="mdi-comment-question-outline" size="small" class="me-2"></v-icon>
                質問を表示 ({{ getQuestionCount(item.questions) }}件)
              </v-expansion-panel-title>
              <v-expansion-panel-text>
                <v-list density="compact">
                  <v-list-item v-for="(question, key) in item.questions" :key="key" class="px-0">
                    <v-list-item-title class="text-body-2">
                      <v-chip size="x-small" color="primary" class="me-2">Q{{ key }}</v-chip>
                      {{ question }}
                    </v-list-item-title>
                  </v-list-item>
                </v-list>
              </v-expansion-panel-text>
            </v-expansion-panel>
          </v-expansion-panels>
          <v-chip v-else color="grey" variant="outlined" size="small">
            質問未設定
          </v-chip>
        </template>

        <!-- アクションの表示 -->
        <template v-slot:item.actions="{ item }">
          <v-btn icon="mdi-pencil" variant="text" size="small" color="primary" @click="editTeam(item)"></v-btn>
          <v-btn icon="mdi-delete" variant="text" size="small" color="error" @click="deleteTeam(item)"></v-btn>
        </template>
      </v-data-table>

    </v-card>
  </v-container>

  <v-dialog v-model="dialog" max-width="500">
    <v-card :title="`${isEditing ? 'Edit' : 'Add'} Team`">
      <v-card-text>
        <v-form ref="teamFormRef">
          <v-row>
            <v-col cols="12">
              <v-text-field 
                v-model="record.name" 
                label="チーム名" 
                :rules="validationRules.teamName" 
                required
                ></v-text-field>
            </v-col>

            <v-col cols="12">
              <v-select
                v-model="record.managers"
                :items="managerCandidates"
                item-title="name"
                item-value="id"
                label="マネージャー"
                multiple
                chips
                clearable
                :loading="userStore.isLoading"
              >
                <template v-slot:chip="{ props, item }">
                  <v-chip v-bind="props" variant="outlined">
                    {{ item.raw.name }}
                  </v-chip>
                </template>
              </v-select>
            </v-col>

            <v-col cols="12">
              <v-card variant="outlined" class="pa-4">
                <v-card-title class="text-h6 pa-0 mb-3">
                  質問設定
                </v-card-title>
                <v-card-text class="text-caption text-medium-emphasis pa-0 pt-2">
                  モチベーション調査で使用する3つの質問を設定してください。
                </v-card-text>

                <div v-for="(question, index) in questionsList" :key="question.id" class="mb-3">
                  <v-text-field v-model="question.text" :label="`質問 ${index + 1}`" variant="outlined" density="compact"
                    :placeholder="`例: ${index === 0 ? '今日の調子はどうですか？' : index === 1 ? '何かお困りのことはありますか？' : 'チームで共有したいことはありますか？'}`"></v-text-field>
                </div>
              </v-card>
            </v-col>
          </v-row>
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


  <!-- 削除確認ダイアログ -->
  <v-dialog v-model="deleteDialog" max-width="400">
    <v-card>
      <v-card-title class="text-h6">
        Delete Team
      </v-card-title>

      <v-card-text>
        <p class="mb-2">以下のチームを削除しますか？</p>
        {{ deletingTeam?.name }}
      </v-card-text>

      <v-divider></v-divider>

      <v-card-actions class="bg-surface-light">
        <v-btn text="CANCEL" variant="plain" @click="cancelDelete"></v-btn>

        <v-spacer></v-spacer>

        <v-btn text="DELETE" color="error" variant="flat" :loading="teamStore.isLoading" @click="confirmDelete"></v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<style scoped>
.v-data-table {
  border-radius: 8px;
}
</style>