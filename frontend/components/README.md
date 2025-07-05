# コンポーネント

このフォルダー内のVueテンプレートファイルは自動的にインポートされます。

## 🚀 使用方法

インポートは [unplugin-vue-components](https://github.com/unplugin/unplugin-vue-components) によって処理されます。このプラグインは `src/components` ディレクトリに作成された `.vue` ファイルを自動的にインポートし、グローバルコンポーネントとして登録します。これにより、手動でインポートすることなく、アプリケーション内の任意のコンポーネントを使用できます。

以下の例は `src/components/MyComponent.vue` に配置されたコンポーネントを想定しています：

```vue
<template>
  <div>
    <MyComponent />
  </div>
</template>

<script lang="ts" setup>
  //
</script>
```

テンプレートがレンダリングされる際、コンポーネントのインポートは自動的にインライン化され、次のようにレンダリングされます：

```vue
<template>
  <div>
    <MyComponent />
  </div>
</template>

<script lang="ts" setup>
  import MyComponent from '@/components/MyComponent.vue'
</script>
```
