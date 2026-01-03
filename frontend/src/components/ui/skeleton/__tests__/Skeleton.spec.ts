import { describe, it, expect } from "vitest";
import { mount } from "@vue/test-utils";
import Skeleton from "../Skeleton.vue";

describe("Skeleton", () => {
  it("renders with default classes", () => {
    const wrapper = mount(Skeleton);

    const element = wrapper.element as HTMLElement;
    expect(element).toBeDefined();
    expect(element.tagName).toBe("DIV");
    expect(element.className).toContain("animate-pulse");
    expect(element.className).toContain("rounded-md");
  });

  it("applies custom class", () => {
    const wrapper = mount(Skeleton, {
      props: {
        class: "h-4 w-32",
      },
    });

    const element = wrapper.element as HTMLElement;
    expect(element.className).toContain("h-4");
    expect(element.className).toContain("w-32");
  });
});
