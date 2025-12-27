import { describe, it, expect } from "vitest";
import { mount } from "@vue/test-utils";
import DateLockField from "../DateLockField.vue";

describe("DateLockField", () => {
  it("renders both date input fields", () => {
    const wrapper = mount(DateLockField, {
      props: {
        datelockFrom: null,
        datelockTo: null,
      },
    });

    expect(wrapper.find('input[id="datelock_from"]').exists()).toBe(true);
    expect(wrapper.find('input[id="datelock_to"]').exists()).toBe(true);
    expect(wrapper.find('label[for="datelock_from"]').exists()).toBe(true);
    expect(wrapper.find('label[for="datelock_to"]').exists()).toBe(true);
  });

  it("displays help text about date lock range", () => {
    const wrapper = mount(DateLockField, {
      props: {
        datelockFrom: null,
        datelockTo: null,
      },
    });

    expect(wrapper.text()).toContain("Date Lock Range");
    expect(wrapper.text()).toContain(
      "This range marks dates that have already been ingested",
    );
  });

  it("shows clear button for from date when set", () => {
    const wrapper = mount(DateLockField, {
      props: {
        datelockFrom: "2023-01-01",
        datelockTo: null,
      },
    });

    const clearButtons = wrapper.findAll('button[type="button"]');
    expect(clearButtons.length).toBe(1);
    expect(clearButtons[0].text()).toBe("Clear");
  });

  it("shows clear button for to date when set", () => {
    const wrapper = mount(DateLockField, {
      props: {
        datelockFrom: null,
        datelockTo: "2023-12-31",
      },
    });

    const clearButtons = wrapper.findAll('button[type="button"]');
    expect(clearButtons.length).toBe(1);
    expect(clearButtons[0].text()).toBe("Clear");
  });

  it("shows both clear buttons when both dates are set", () => {
    const wrapper = mount(DateLockField, {
      props: {
        datelockFrom: "2023-01-01",
        datelockTo: "2023-12-31",
      },
    });

    const clearButtons = wrapper.findAll('button[type="button"]');
    expect(clearButtons.length).toBe(2);
  });

  it("hides clear buttons when dates are not set", () => {
    const wrapper = mount(DateLockField, {
      props: {
        datelockFrom: null,
        datelockTo: null,
      },
    });

    const clearButtons = wrapper.findAll('button[type="button"]');
    expect(clearButtons.length).toBe(0);
  });

  it("emits update:datelockFrom event when from date changes", async () => {
    const wrapper = mount(DateLockField, {
      props: {
        datelockFrom: null,
        datelockTo: null,
      },
    });

    const fromInput = wrapper.find('input[id="datelock_from"]');
    await fromInput.setValue("2023-01-01");

    expect(wrapper.emitted("update:datelockFrom")).toBeTruthy();
    expect(wrapper.emitted("update:datelockFrom")?.[0]).toEqual(["2023-01-01"]);
  });

  it("emits update:datelockTo event when to date changes", async () => {
    const wrapper = mount(DateLockField, {
      props: {
        datelockFrom: null,
        datelockTo: null,
      },
    });

    const toInput = wrapper.find('input[id="datelock_to"]');
    await toInput.setValue("2023-12-31");

    expect(wrapper.emitted("update:datelockTo")).toBeTruthy();
    expect(wrapper.emitted("update:datelockTo")?.[0]).toEqual(["2023-12-31"]);
  });

  it("emits null when from clear button is clicked", async () => {
    const wrapper = mount(DateLockField, {
      props: {
        datelockFrom: "2023-01-01",
        datelockTo: null,
      },
    });

    const clearButtons = wrapper.findAll('button[type="button"]');
    await clearButtons[0].trigger("click");

    expect(wrapper.emitted("update:datelockFrom")).toBeTruthy();
    expect(wrapper.emitted("update:datelockFrom")?.[0]).toEqual([null]);
  });

  it("emits null when to clear button is clicked", async () => {
    const wrapper = mount(DateLockField, {
      props: {
        datelockFrom: null,
        datelockTo: "2023-12-31",
      },
    });

    const clearButtons = wrapper.findAll('button[type="button"]');
    await clearButtons[0].trigger("click");

    expect(wrapper.emitted("update:datelockTo")).toBeTruthy();
    expect(wrapper.emitted("update:datelockTo")?.[0]).toEqual([null]);
  });

  it("displays error message when error prop is provided", () => {
    const wrapper = mount(DateLockField, {
      props: {
        datelockFrom: null,
        datelockTo: null,
        error: "Invalid date range",
      },
    });

    expect(wrapper.text()).toContain("Invalid date range");
    const inputs = wrapper.findAll('input[type="date"]');
    inputs.forEach((input) => {
      expect(input.classes()).toContain("border-red-500");
    });
  });

  it("sets min attribute on to date input based on from date", () => {
    const wrapper = mount(DateLockField, {
      props: {
        datelockFrom: "2023-01-01",
        datelockTo: null,
      },
    });

    const toInput = wrapper.find('input[id="datelock_to"]');
    expect(toInput.attributes("min")).toBe("2023-01-01");
  });

  it("sets max attribute on from date input based on to date", () => {
    const wrapper = mount(DateLockField, {
      props: {
        datelockFrom: null,
        datelockTo: "2023-12-31",
      },
    });

    const fromInput = wrapper.find('input[id="datelock_from"]');
    expect(fromInput.attributes("max")).toBe("2023-12-31");
  });
});
