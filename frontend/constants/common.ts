// 役割Enum
export enum UserRole {
  SUPERUSER = 1,
  ADMIN = 2,
  MANAGER = 3,
  USER = 4
}

// 役割設定
export const roleOptions = [
  { value: UserRole.SUPERUSER, title: 'スーパーユーザー' },
  { value: UserRole.ADMIN, title: '管理者' },
  { value: UserRole.MANAGER, title: 'マネージャー' },
  { value: UserRole.USER, title: 'ユーザー' }
]
