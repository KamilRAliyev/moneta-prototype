// Simple toast composable that uses window.showToast
// This matches the pattern from the zip file
export function useToast() {
  const showToast = (type: string, title: string, message?: string) => {
    if (typeof window !== "undefined" && (window as any).showToast) {
      (window as any).showToast({ type, title, message });
    } else {
      console.warn("ToastContainer not mounted yet");
    }
  };

  return {
    toast: showToast,
    success: (title: string, message?: string) =>
      showToast("success", title, message),
    error: (title: string, message?: string) =>
      showToast("error", title, message),
    warning: (title: string, message?: string) =>
      showToast("warning", title, message),
    info: (title: string, message?: string) =>
      showToast("info", title, message),
  };
}
