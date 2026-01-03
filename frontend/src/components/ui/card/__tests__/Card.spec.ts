import { describe, it, expect } from "vitest";
import { mount } from "@vue/test-utils";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "../index";

describe("Card Components", () => {
  it("renders Card with content", () => {
    const wrapper = mount(Card, {
      slots: {
        default: "Card content",
      },
    });

    expect(wrapper.text()).toContain("Card content");
    const element = wrapper.element as HTMLElement;
    expect(element).toBeDefined();
    expect(element.tagName).toBe("DIV");
    expect(element.className).toContain("rounded-lg");
  });

  it("renders CardHeader", () => {
    const wrapper = mount(CardHeader, {
      slots: {
        default: "Header content",
      },
    });

    expect(wrapper.text()).toContain("Header content");
    const element = wrapper.element as HTMLElement;
    expect(element).toBeDefined();
    expect(element.tagName).toBe("DIV");
  });

  it("renders CardTitle", () => {
    const wrapper = mount(CardTitle, {
      slots: {
        default: "Test Title",
      },
    });

    expect(wrapper.text()).toContain("Test Title");
  });

  it("renders CardDescription", () => {
    const wrapper = mount(CardDescription, {
      slots: {
        default: "Test Description",
      },
    });

    expect(wrapper.text()).toContain("Test Description");
  });

  it("renders CardContent", () => {
    const wrapper = mount(CardContent, {
      slots: {
        default: "Content here",
      },
    });

    expect(wrapper.text()).toContain("Content here");
  });
});
