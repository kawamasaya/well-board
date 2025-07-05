export const validationRules = {

  tenantName: [
    (v: string) => !!v || '組織名は必須です',
    (v: string) => v.length <= 50 || '組織名は50文字以下で入力してください'
  ],

  tenantDomain: [
    (v: string) => !!v || 'ドメインは必須です',
    (v: string) => /^[a-zA-Z0-9-]+\.[a-zA-Z]{2,}$/.test(v) || 'ドメインの形式が正しくありません',
  ],

  userName: [
    (v: string) => !!v || 'ユーザー名は必須です',
    (v: string) => v.length <= 100 || '組織名は100文字以下で入力してください'
  ],

  userTeam: [
    (v: string) => v.length > 0 || 'チームは必須です'
  ],

  name: [
    (v: string) => !v || v.length <= 100 || '名前は100文字以下で入力してください'
  ],

  userEmail: [
    (v: string) => !!v || 'メールアドレスは必須です',
    (v: string) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v) || 'メールアドレスの形式が正しくありません'
  ],

  teamName: [
    (v: string) => !!v || 'チーム名は必須です'
  ],

  entryTeam: [
    (v: string) => !!v || 'チームは必須です'
  ],
}