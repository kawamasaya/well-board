<script setup lang="ts">
import { roleOptions } from '@/constants/common'
import { useInfoStore } from '@/stores/info'
import { useTeamStore } from '@/stores/team'
import { useUserStore } from '@/stores/user'
import type { UserDetail, UserFormData } from '@/types'
import { validationRules } from '@/utils/validation'
import { onMounted, ref, shallowRef } from 'vue'

const userStore = useUserStore()
const teamStore = useTeamStore()
const infoStore = useInfoStore()

const dataTable = {
  headers: [
    { title: 'ユーザー', align: 'start' as const, key: 'name' },
    { title: 'メール', align: 'start' as const, key: 'email' },
    { title: '役割', align: 'start' as const, key: 'role' },
    { title: 'チーム', align: 'start' as const, key: 'teams' },
    { title: 'アクション', key: 'actions', sortable: false, align: 'center' as const }
  ],
}

const DEFAULT_RECORD: UserFormData = {
  name: '',
  email: '',
  role: 4, // USER
  teams: []
}

// roleOptionsは共通設定からインポート

const record = ref<UserFormData>({ ...DEFAULT_RECORD })
const dialog = shallowRef(false)
const isEditing = shallowRef(false)
const editingUserId = ref<number | null>(null)
const deleteDialog = shallowRef(false)
const deletingUser = ref<UserDetail | null>(null)
const userFormRef = ref<any>(null)

// 役割名を取得
function getRoleName(roleValue: number) {
  const role = roleOptions.find(r => r.value === roleValue)
  return role ? role.title : 'Unknown'
}

// 初期化メソッド
async function init() {
  try {
    await userStore.fetchUsers()
  } catch (error) {
    infoStore.add("ユーザーデータの取得に失敗しました", "error")
  }
}

onMounted(async () => {
  await init()
})

async function add() {
  try {
    await teamStore.fetchTeams()
    isEditing.value = false
    record.value = { ...DEFAULT_RECORD }
    dialog.value = true
  } catch (error) {
    // エラーハンドリングは必要に応じて追加
  }
}

async function save() {

  const { valid } = await userFormRef.value.validate()
  if (!valid) {
    infoStore.add("入力内容を確認してください", "error")
    return
  }

  try {
    if (isEditing.value && editingUserId.value) {
      // 編集の場合
      await userStore.updateUser(editingUserId.value, record.value)
    } else {
      // 新規作成の場合
      await userStore.addUser(record.value)
    }

    dialog.value = false
    // 初期化メソッドを呼び出し
    await init()
  } catch (error) {
    infoStore.add("ユーザーの保存に失敗しました", "error")
  }
}

// ユーザー編集
function editUser(user: UserDetail) {
  isEditing.value = true
  editingUserId.value = user.id
  record.value = {
    name: user.name,
    email: user.email,
    role: user.role || 4,
    teams: user.teams ? user.teams.map(team => team.id) : []
  }

  dialog.value = true
}

// ユーザー削除確認ダイアログを表示
function deleteUser(user: UserDetail) {
  deletingUser.value = user
  deleteDialog.value = true
}

// ユーザー削除を実行
async function confirmDelete() {
  if (!deletingUser.value) return

  try {
    await userStore.deleteUser(deletingUser.value.id)
    deleteDialog.value = false
    deletingUser.value = null
  
    // 初期化メソッドを呼び出し
    await init()
  } catch (error) {
    infoStore.add("ユーザーの削除に失敗しました", "error")
  }
}

// ユーザー削除をキャンセル
function cancelDelete() {
  deleteDialog.value = false
  deletingUser.value = null
}
</script>

<template>
  <v-container>
    <v-card>
      <v-card-title>
        Users
      </v-card-title>
      <v-data-table 
        :headers="dataTable.headers" 
        :items="userStore.users" 
        :loading="userStore.isLoading"
        class="elevation-1" 
        item-value="id" 
        :items-per-page="25" 
        :items-per-page-options="[25, 50, 100]"
      >
        <template v-slot:top>
          <v-toolbar flat>
            <v-toolbar-title>
              <v-icon icon="mdi-account-multiple" size="small" start></v-icon>
            </v-toolbar-title>

            <v-spacer></v-spacer>

            <v-btn class="me-2" prepend-icon="mdi-plus" rounded="lg" text="Add" @click="add"></v-btn>
          </v-toolbar>
        </template>

        <!-- ユーザー名の表示 -->
        <template v-slot:item.name="{ item }">
          <div class="d-flex align-center py-2">
            <v-avatar color="primary" size="40" class="me-3">
              <v-icon icon="mdi-account" color="white"></v-icon>
            </v-avatar>
            <div>
              <div class="text-subtitle-1 font-weight-bold">{{ item.name }}</div>
              <div class="text-caption text-medium-emphasis">ID: {{ item.id }}</div>
            </div>
          </div>
        </template>

        <!-- メールの表示 -->
        <template v-slot:item.email="{ item }">
          <div class="text-body-2">{{ item.email }}</div>
        </template>

        <!-- 役割の表示 -->
        <template v-slot:item.role="{ item }">
            {{ getRoleName(item.role || 4) }}
        </template>

        <!-- チームの表示 -->
        <template v-slot:item.teams="{ item }">
            <v-chip
              v-for="team in item.teams"
              :key="team.id"
              variant="outlined"
            >
              {{ team.name }}
            </v-chip>
        </template>

        <!-- アクションの表示 -->
        <template v-slot:item.actions="{ item }">
          <v-btn icon="mdi-pencil" variant="text" size="small" color="primary" @click="editUser(item)"></v-btn>
          <v-btn icon="mdi-delete" variant="text" size="small" color="error" @click="deleteUser(item)"></v-btn>
        </template>
      </v-data-table>
    </v-card>
  </v-container>


  <!-- ユーザー作成ダイアログ -->
  <v-dialog v-model="dialog" max-width="600">
    <v-card :title="`${isEditing ? 'Edit' : 'Add'} User`">
      <v-card-text>
        <v-form ref="userFormRef">
          <v-row>
            <v-col cols="12" md="6">
              <v-text-field 
                v-model="record.name" 
                label="ユーザー名" 
                :rules="validationRules.userName"
              >
              </v-text-field>
            </v-col>
            <v-col cols="12" md="6">
              <v-text-field 
                v-model="record.email" 
                label="メールアドレス" 
                type="email"
                :rules="validationRules.userEmail" 
              ></v-text-field>
            </v-col>
            <v-col cols="12" md="6">
              <v-select v-model="record.role" :items="roleOptions" item-title="title" item-value="value"
                label="役割" required></v-select>
            </v-col>
            <v-col cols="12" md="6">
              <v-select 
                v-model="record.teams" 
                :items="teamStore.teams" 
                item-title="name" 
                item-value="id"
                label="所属チーム" 
                :rules="validationRules.userTeam" 
                multiple 
                chips 
                closable-chips
              ></v-select>
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
        Delete User
      </v-card-title>

      <v-card-text>
        <p class="mb-2">以下のユーザーを削除しますか？</p>
        <div class="d-flex align-center">
          <div>
            <div class="font-weight-bold">{{ deletingUser?.name }}</div>
            <div class="text-caption text-medium-emphasis">{{ deletingUser?.email }}</div>
          </div>
        </div>
      </v-card-text>

      <v-divider></v-divider>

      <v-card-actions class="bg-surface-light">
        <v-btn text="CANCEL" variant="plain" @click="cancelDelete"></v-btn>

        <v-spacer></v-spacer>

        <v-btn text="DELETE" color="error" variant="text" :loading="userStore.isLoading" @click="confirmDelete"></v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<style scoped>
.v-data-table {
  border-radius: 8px;
}
</style>