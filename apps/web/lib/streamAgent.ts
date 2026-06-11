import type { StreamEvent } from "./types";

export type ParsedSseBuffer = {
  events: StreamEvent[];
  remaining: string;
};

export type StreamAgentOptions = {
  message: string;
  sessionId: string;
  onEvent: (event: StreamEvent) => void;
};

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export function parseSseBuffer(buffer: string): ParsedSseBuffer {
  const normalized = buffer.replace(/\r\n/g, "\n");
  const chunks = normalized.split("\n\n");
  const completeChunks = normalized.endsWith("\n\n") ? chunks.slice(0, -1) : chunks.slice(0, -1);
  const remaining = normalized.endsWith("\n\n") ? "" : chunks.at(-1) ?? "";

  const events = completeChunks
    .map(parseSseEvent)
    .filter((event): event is StreamEvent => event !== null);

  return { events, remaining };
}

export async function streamAgent(options: StreamAgentOptions): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/agent/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      message: options.message,
      sessionId: options.sessionId,
    }),
  });

  if (!response.ok || !response.body) {
    options.onEvent({
      event: "error",
      data: { message: `Agent request failed with status ${response.status}` },
    });
    return;
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) {
      break;
    }

    buffer += decoder.decode(value, { stream: true });
    const parsed = parseSseBuffer(buffer);
    parsed.events.forEach(options.onEvent);
    buffer = parsed.remaining;
  }

  buffer += decoder.decode();
  const parsed = parseSseBuffer(buffer);
  parsed.events.forEach(options.onEvent);
}

function parseSseEvent(chunk: string): StreamEvent | null {
  const lines = chunk.split("\n");
  const eventLine = lines.find((line) => line.startsWith("event: "));
  const dataLines = lines.filter((line) => line.startsWith("data: "));

  if (!eventLine || dataLines.length === 0) {
    return null;
  }

  const event = eventLine.replace("event: ", "").trim() as StreamEvent["event"];
  const dataText = dataLines.map((line) => line.replace("data: ", "")).join("\n");

  return {
    event,
    data: JSON.parse(dataText) as Record<string, unknown>,
  };
}
