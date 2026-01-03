import { describe, it, expect } from "vitest";
import { mount } from "@vue/test-utils";
import Badge from "../Badge.vue";

describe("Badge", () => {
  it("renders with default variant", () => {
    const wrapper = mount(Badge, {
      slots: {
        default: "Badge text",
      },
    });

    expect(wrapper.text()).toContain("Badge text");
    const element = wrapper.element as HTMLElement;
    expect(element).toBeDefined();
    expect(element.tagName).toBe("DIV");
    expect(element.className).toContain("inline-flex");
  });

  it("applies variant classes", () => {
    const wrapper = mount(Badge, {
      props: {
        variant: "destructive",
      },
      slots: {
        default: "Badge",
      },
    });

    const element = wrapper.element as HTMLElement;
    expect(element.className).toContain("bg-destructive");
  });

  it("applies custom class", () => {
    const wrapper = mount(Badge, {
      props: {
        class: "custom-class",
      },
      slots: {
        default: "Badge",
      },
    });

    const element = wrapper.element as HTMLElement;
    expect(element.className).toContain("custom-class");
  });
});
