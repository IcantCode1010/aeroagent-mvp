import { describe, expect, it } from "vitest";

import { parseSseBuffer } from "./streamAgent";

describe("parseSseBuffer", () => {
  it("returns complete typed events and preserves an incomplete trailing event", () => {
    const input = [
      "event: status",
      'data: {"message":"Planning request..."}',
      "",
      "event: image_result",
      'data: {"imageId":"apu_generator","title":"APU Generator Diagram"}',
      "",
      "event: agent_token",
      'data: {"text":"partial"}',
    ].join("\n");

    const result = parseSseBuffer(input);

    expect(result.events).toEqual([
      { event: "status", data: { message: "Planning request..." } },
      {
        event: "image_result",
        data: { imageId: "apu_generator", title: "APU Generator Diagram" },
      },
    ]);
    expect(result.remaining).toBe('event: agent_token\ndata: {"text":"partial"}');
  });

  it("parses a done event after a Windows newline delimiter", () => {
    const result = parseSseBuffer('event: done\r\ndata: {"messageId":"demo-msg-1"}\r\n\r\n');

    expect(result).toEqual({
      events: [{ event: "done", data: { messageId: "demo-msg-1" } }],
      remaining: "",
    });
  });
});
