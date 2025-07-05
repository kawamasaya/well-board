import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { NotificationColor } from '@/types'

export const useInfoStore = defineStore('info', () => {
  // State
  const message = ref<string | null>(null)
  const color = ref<NotificationColor | null>(null)
  const visible = ref<boolean>(false)
  
  // Actions
  function add(messageText: string, colorValue: NotificationColor = 'success'): void {
    message.value = messageText
    color.value = colorValue
    visible.value = true
  }
  
  function hide(): void {
    visible.value = false
  }
  
  function clear(): void {
    message.value = null
    color.value = null
    visible.value = false
  }
  
  return {
    // State
    message,
    color,
    visible,
    
    // Actions
    add,
    hide,
    clear
  }
})