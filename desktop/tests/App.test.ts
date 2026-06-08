import { mount } from "@vue/test-utils";
import { describe, expect, it, vi } from "vitest";
import App from "../src/App.vue";

describe("Real-Time Translator UI", () => {
  it("renders grouped English and Spanish transcript pairs", () => {
    const wrapper = mount(App);

    expect(wrapper.text()).toContain("Real-Time Translator");
    expect(wrapper.text()).toContain("Good morning everyone");
    expect(wrapper.text()).toContain("Buenos dias a todos");
    expect(wrapper.findAll(".timeline-pair").length).toBeGreaterThanOrEqual(4);
  });

  it("sends pause commands through the desktop bridge", async () => {
    const sendCommand = vi.fn().mockResolvedValue({ accepted: true });
    window.translatorBridge = { sendCommand };
    const wrapper = mount(App);

    await wrapper.find(".control-button.primary").trigger("click");

    expect(sendCommand).toHaveBeenCalledWith({ type: "pause" });
  });
});
