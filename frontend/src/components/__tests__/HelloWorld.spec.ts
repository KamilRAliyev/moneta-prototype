import { describe, it, expect } from "vitest";
import { mount } from "@vue/test-utils";
import HelloWorld from "../HelloWorld.vue";

describe("HelloWorld", () => {
  it("renders the message prop", () => {
    const msg = "Hello Vitest";
    const wrapper = mount(HelloWorld, {
      props: { msg },
    });

    expect(wrapper.text()).toContain(msg);
  });

  it("increments count when button is clicked", async () => {
    const wrapper = mount(HelloWorld, {
      props: { msg: "Test" },
    });

    const button = wrapper.find("button");
    expect(button.text()).toContain("count is 0");

    await button.trigger("click");
    expect(button.text()).toContain("count is 1");

    await button.trigger("click");
    expect(button.text()).toContain("count is 2");
  });

  it("has correct structure", () => {
    const wrapper = mount(HelloWorld, {
      props: { msg: "Test" },
    });

    expect(wrapper.find("h1").exists()).toBe(true);
    expect(wrapper.find(".card").exists()).toBe(true);
    expect(wrapper.find("button").exists()).toBe(true);
  });
});
