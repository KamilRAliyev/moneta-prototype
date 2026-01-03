import { useDark, useToggle } from "@vueuse/core";

export function useTheme() {
  const isDark = useDark({
    storageKey: "moneta-theme",
    selector: "html",
    attribute: "class",
    valueDark: "dark",
    valueLight: "",
  });

  const toggleTheme = useToggle(isDark);

  return {
    isDark,
    toggleTheme,
  };
}
