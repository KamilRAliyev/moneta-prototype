import { describe, it, expect, beforeEach } from "vitest";
import { setActivePinia, createPinia } from "pinia";
import { useAppStore } from "../app";

describe("App Store", () => {
  beforeEach(() => {
    // Create a fresh Pinia instance for each test
    setActivePinia(createPinia());
  });

  it("initializes with default state", () => {
    const store = useAppStore();

    expect(store.count).toBe(0);
    expect(store.name).toBe("Moneta");
  });

  it("increments count", () => {
    const store = useAppStore();

    expect(store.count).toBe(0);
    store.increment();
    expect(store.count).toBe(1);
    store.increment();
    expect(store.count).toBe(2);
  });

  it("decrements count", () => {
    const store = useAppStore();

    store.increment();
    store.increment();
    expect(store.count).toBe(2);

    store.decrement();
    expect(store.count).toBe(1);
    store.decrement();
    expect(store.count).toBe(0);
  });

  it("resets count to zero", () => {
    const store = useAppStore();

    store.increment();
    store.increment();
    store.increment();
    expect(store.count).toBe(3);

    store.reset();
    expect(store.count).toBe(0);
  });

  it("computes doubleCount correctly", () => {
    const store = useAppStore();

    expect(store.doubleCount).toBe(0);

    store.increment();
    expect(store.doubleCount).toBe(2);

    store.increment();
    expect(store.doubleCount).toBe(4);

    store.increment();
    expect(store.doubleCount).toBe(6);
  });

  it("sets name correctly", () => {
    const store = useAppStore();

    expect(store.name).toBe("Moneta");

    store.setName("New Name");
    expect(store.name).toBe("New Name");

    store.setName("Another Name");
    expect(store.name).toBe("Another Name");
  });
});
