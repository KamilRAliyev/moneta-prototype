import { describe, it, expect } from "vitest";
import { mount } from "@vue/test-utils";
import DateLockField from "../DateLockField.vue";

describe("DateLockField", () => {
  it("renders date input field", () => {
    const wrapper = mount(DateLockField, {
      props: {
        modelValue: null,
      },
    });

    expect(wrapper.find('input[type="date"]').exists()).toBe(true);
    expect(wrapper.find('label[for="datelock_from"]').exists()).toBe(true);
  });

  it("displays help text", () => {
    const wrapper = mount(DateLockField, {
      props: {
        modelValue: null,
      },
    });

    expect(wrapper.text()).toContain("Date Lock");
    expect(wrapper.text()).toContain(
      "Transactions before this date will not be ingested",
    );
  });

  it("shows clear button when date is set", () => {
    const wrapper = mount(DateLockField, {
      props: {
        modelValue: "2023-01-01",
      },
    });

    const clearButton = wrapper.find('button[type="button"]');
    expect(clearButton.exists()).toBe(true);
    expect(clearButton.text()).toBe("Clear");
  });

  it("hides clear button when date is not set", () => {
    const wrapper = mount(DateLockField, {
      props: {
        modelValue: null,
      },
    });

    const clearButton = wrapper.find('button[type="button"]');
    expect(clearButton.exists()).toBe(false);
  });

  it("emits update event when date changes", async () => {
    const wrapper = mount(DateLockField, {
      props: {
        modelValue: null,
      },
    });

    const input = wrapper.find('input[type="date"]');
    await input.setValue("2023-01-01");

    expect(wrapper.emitted("update:modelValue")).toBeTruthy();
    expect(wrapper.emitted("update:modelValue")?.[0]).toEqual(["2023-01-01"]);
  });

  it("emits null when clear button is clicked", async () => {
    const wrapper = mount(DateLockField, {
      props: {
        modelValue: "2023-01-01",
      },
    });

    const clearButton = wrapper.find('button[type="button"]');
    await clearButton.trigger("click");

    expect(wrapper.emitted("update:modelValue")).toBeTruthy();
    expect(wrapper.emitted("update:modelValue")?.[0]).toEqual([null]);
  });

  it("displays error message when error prop is provided", () => {
    const wrapper = mount(DateLockField, {
      props: {
        modelValue: null,
        error: "Invalid date",
      },
    });

    expect(wrapper.text()).toContain("Invalid date");
    expect(wrapper.find('input[type="date"]').classes()).toContain(
      "border-red-500",
    );
  });
});
