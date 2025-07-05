<script setup lang="ts">
import { useAuthStore } from '@/stores/auth'
import { useInfoStore } from '@/stores/info'
import type { LoginFormData, TenantRequestFormData } from '@/types'
import { validationRules } from '@/utils/validation'
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const authStore = useAuthStore()
const infoStore = useInfoStore()

const tab = ref<string>('login')
const error = ref<string | null>(null)
const isLoading = ref<boolean>(false)
const tenantRequestFormRef = ref<any>(null)

const loginForm = ref<LoginFormData>({
  email: '',
  password: ''
})

const tenantRequestForm = ref<TenantRequestFormData>({
  tenantName: '',
  email: '',
  name: '',
  domain: ''
})

async function login(): Promise<void> {
  try {
    isLoading.value = true
    error.value = null
    await authStore.login(loginForm.value)
    await router.push('/home')
  } catch (err: any) {
    if (err.response?.status === 401) {
      infoStore.add("メールアドレスまたはパスワードが間違っています。", "error")
    } else {
      infoStore.add("ログインに失敗しました。時間をおいて再試行してください。", "error")
    }
  } finally {
    isLoading.value = false
  }
}

async function tenantRequest(): Promise<void> {
  // フォームバリデーションチェック
  const { valid } = await tenantRequestFormRef.value.validate()
  if (!valid) {
    infoStore.add("入力内容を確認してください。", "error")
    return
  }

  try {
    isLoading.value = true
    error.value = null
    await authStore.tenantRequest(tenantRequestForm.value)
    infoStore.add("テナント申請が完了しました。承認をお待ちください。", "success")
    tab.value = 'login'
  } catch (err: any) {
    if (err.response?.status === 400) {
      const errors = err.response.data
      if (errors.email) {
        infoStore.add("メールアドレスが既に使用されています。", "error")
      } else {
        infoStore.add("入力内容に問題があります。", "error")
      }
    } else {
      infoStore.add("リクエストに失敗しました。時間をおいて再試行してください。", "error")
    }
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <v-container>
    <v-card 
      width="600"
      class="mx-auto pa-12 pb-8"
      elevation="8"
      max-width="448"
      rounded="lg"
    >
      <v-tabs v-model="tab" align-tabs="center">
        <v-tab value="login">ログイン</v-tab>
        <v-tab value="tenant-request">テナント申請</v-tab>
      </v-tabs>

      <v-window v-model="tab">
        <v-window-item value="login">
          <v-card-text>
            <v-form @submit.prevent="login">

              <v-text-field
                v-model = "loginForm.email"
                density="compact"
                placeholder="Email address"
                prepend-inner-icon="mdi-email-outline"
                variant="outlined"
              ></v-text-field>

              <v-text-field
                v-model = "loginForm.password"
                type="password"
                density="compact"
                placeholder="Enter your password"
                prepend-inner-icon="mdi-lock-outline"
                variant="outlined"
              ></v-text-field>

              <v-btn type="submit" class="mb-8" color="primary" size="large" variant="text" block>
                Log In
              </v-btn>
              <a
                class="text-caption text-decoration-none text-blue"
                href="#"
                rel="noopener noreferrer"
                target="_blank"
              >
                Forgot login password?
              </a>
            </v-form>

          </v-card-text>
        </v-window-item>

        <v-window-item value="tenant-request">
          <v-card-text>
            <v-form ref="tenantRequestFormRef" @submit.prevent="tenantRequest">

              <v-text-field
                v-model="tenantRequestForm.tenantName"
                density="compact"
                placeholder="組織名"
                prepend-inner-icon="mdi-home-account"
                variant="outlined"
                :rules="validationRules.tenantName"
              ></v-text-field>

              <v-text-field
                v-model="tenantRequestForm.email"
                density="compact"
                placeholder="メールアドレス"
                prepend-inner-icon="mdi-email-outline"
                variant="outlined"
                :rules="validationRules.userEmail"
              ></v-text-field>

              <v-text-field
                v-model="tenantRequestForm.name"
                density="compact"
                placeholder="ユーザー名"
                prepend-inner-icon="mdi-account"
                variant="outlined"
                :rules="validationRules.userName"
              ></v-text-field>

              <v-text-field
                v-model="tenantRequestForm.domain"
                density="compact"
                placeholder="ドメイン (例: example.com)"
                prepend-inner-icon="mdi-domain"
                variant="outlined"
                :rules="validationRules.tenantDomain"
              ></v-text-field>

              <v-btn type="submit" class="mb-8" color="primary" size="large" variant="text" block>
                申請
              </v-btn>
            </v-form>
          </v-card-text>
        </v-window-item>
      </v-window>
    </v-card>
  </v-container>
</template>

<style scoped>

</style>