import { defineStore } from "pinia";
import { ref } from "vue";

export type ToastType = "success" | "error" | "warning" | "info";

export interface Toast {
  id: string;
  type: ToastType;
  title: string;
  description?: string;
  duration?: number;
}

export const useToastStore = defineStore("toast", () => {
  const toasts = ref<Toast[]>([]);

  function addToast(toast: Omit<Toast, "id">) {
    const id = `toast-${Date.now()}-${Math.random()}`;
    const newToast: Toast = {
      id,
      duration: 5000,
      ...toast,
    };

    toasts.value.push(newToast);

    // Auto-dismiss after duration
    if (newToast.duration && newToast.duration > 0) {
      setTimeout(() => {
        removeToast(id);
      }, newToast.duration);
    }

    return id;
  }

  function removeToast(id: string) {
    const index = toasts.value.findIndex((t) => t.id === id);
    if (index > -1) {
      toasts.value.splice(index, 1);
    }
  }

  function clearAll() {
    toasts.value = [];
  }

  // Convenience methods
  function success(title: string, description?: string) {
    return addToast({ type: "success", title, description });
  }

  function error(title: string, description?: string) {
    return addToast({ type: "error", title, description });
  }

  function warning(title: string, description?: string) {
    return addToast({ type: "warning", title, description });
  }

  function info(title: string, description?: string) {
    return addToast({ type: "info", title, description });
  }

  return {
    toasts,
    addToast,
    removeToast,
    clearAll,
    success,
    error,
    warning,
    info,
  };
});
