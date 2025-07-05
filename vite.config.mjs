import { fileURLToPath, URL } from 'node:url'
import Vue from '@vitejs/plugin-vue'
import Fonts from 'unplugin-fonts/vite'
// Plugins
import Components from 'unplugin-vue-components/vite'
import VueRouter from 'unplugin-vue-router/vite'
// Utilities
import { defineConfig } from 'vite'
import Vuetify, { transformAssetUrls } from 'vite-plugin-vuetify'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    VueRouter(),
    Vue({
      template: { transformAssetUrls },
    }),
    // https://github.com/vuetifyjs/vuetify-loader/tree/master/packages/vite-plugin#readme
    Vuetify({
      autoImport: true,
      styles: {
        configFile: 'frontend/styles/settings.scss',
      },
    }),
    // Components(),
    Fonts({
      google: {
        families: [{
          name: 'Roboto',
          styles: 'wght@100;300;400;500;700;900',
        }],
      },
    }),
  ],
  optimizeDeps: {
    include: [
      'vuetify/components/VCard',
      'vuetify/components/VForm',
      'vuetify/components/VGrid',
      'vuetify/components/VTabs',
      'vuetify/components/VTextField',
      'vuetify/components/VWindow',
      'vuetify/components/VAvatar',
      'vuetify/components/VChip',
      'vuetify/components/VDataTable',
      'vuetify/components/VDialog',
      'vuetify/components/VDivider',
      'vuetify/components/VExpansionPanel',
      'vuetify/components/VToolbar',
      'vuetify/components/VSelect',
      'vuetify/components/VSheet',
      'vuetify/components/VSparkline',
    ],
    // exclude: [
    //   'vuetify',
    //   'vue-router',
    //   'unplugin-vue-router/runtime',
    //   'unplugin-vue-router/data-loaders',
    //   'unplugin-vue-router/data-loaders/basic',
    // ],
  },
  define: { 'process.env': {} },
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('frontend', import.meta.url)),
    },
    extensions: [
      '.js',
      '.json',
      '.jsx',
      '.mjs',
      '.ts',
      '.tsx',
      '.vue',
    ],
  },
  build: {
    outDir: 'dist',
    assetsDir: 'static',
  },
  server: {
    watch: {
      usePolling: true,
      interval: 1000,
    },
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8081/",
      },
    },
  },
  css: {
    preprocessorOptions: {
      sass: {
        api: 'modern-compiler',
      },
      scss: {
        api: 'modern-compiler',
      },
    },
  },
})
