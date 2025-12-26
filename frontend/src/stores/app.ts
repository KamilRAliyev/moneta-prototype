import { defineStore } from "pinia";
import { ref, computed } from "vue";

export const useAppStore = defineStore("app", () => {
  // State
  const count = ref(0);
  const name = ref("Moneta");

  // Getters
  const doubleCount = computed(() => count.value * 2);

  // Actions
  function increment() {
    count.value++;
  }

  function decrement() {
    count.value--;
  }

  function reset() {
    count.value = 0;
  }

  function setName(newName: string) {
    name.value = newName;
  }

  return {
    // State
    count,
    name,
    // Getters
    doubleCount,
    // Actions
    increment,
    decrement,
    reset,
    setName,
  };
});
