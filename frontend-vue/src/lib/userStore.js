import { ref } from 'vue'

export const userRole = ref(null) // 'admin' o 'vendedor'

export function setUserRole(role) {
  userRole.value = role
}