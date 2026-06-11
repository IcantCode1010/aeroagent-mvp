"use client";

import { FormEvent, useRef, useState } from "react";

import { streamAgent } from "../lib/streamAgent";
import type { ChatBlock, ImageResult, StreamEvent, UIAction } from "../lib/types";
import { ImageCard } from "./ImageCard";

type ChatPanelProps = {
  onOpenImage: (image: ImageResult) => void;
};

export function ChatPanel({ onOpenImage }: ChatPanelProps) {
  const [input, setInput] = useState("show me apu images");
  const [blocks, setBlocks] = useState<ChatBlock[]>([]);
  const [status, setStatus] = useState("Ready");
  const [isStreaming, setIsStreaming] = useState(false);
  const imagesById = useRef(new Map<string, ImageResult>());

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const message = input.trim();
    if (!message || isStreaming) {
      return;
    }

    setBlocks([]);
    setStatus("Connecting...");
    setIsStreaming(true);

    await streamAgent({
      message,
      sessionId: "demo",
      onEvent: handleStreamEvent,
    });
  }

  function handleStreamEvent(event: StreamEvent) {
    if (event.event === "status") {
      setStatus(String(event.data.message ?? "Working..."));
      return;
    }

    if (event.event === "tool_start") {
      setStatus(`Running ${String(event.data.tool ?? "tool")}...`);
      return;
    }

    if (event.event === "tool_done") {
      setStatus("Tool finished");
      return;
    }

    if (event.event === "image_result") {
      const image = event.data as ImageResult;
      imagesById.current.set(image.imageId, image);
      setBlocks((current) => [...current, { id: `image-${image.imageId}`, type: "image", image }]);
      return;
    }

    if (event.event === "ui_action") {
      const action = event.data as UIAction;
      const image = imagesById.current.get(action.payload.imageId);
      if (action.type === "open_image" && image) {
        onOpenImage(image);
      }
      return;
    }

    if (event.event === "agent_token") {
      setBlocks((current) => [
        ...current,
        { id: `text-${current.length}-${Date.now()}`, type: "text", text: String(event.data.text ?? "") },
      ]);
      return;
    }

    if (event.event === "warning" || event.event === "error") {
      setStatus(String(event.data.message ?? "Agent warning"));
      setIsStreaming(false);
      return;
    }

    if (event.event === "done") {
      setStatus("Done");
      setIsStreaming(false);
    }
  }

  return (
    <aside className="chat-panel" aria-label="Streaming agent chat">
      <div className="chat-header">
        <div>
          <p className="eyebrow">Agent stream</p>
          <h2>Chat</h2>
        </div>
        <span className="status-pill">{status}</span>
      </div>

      <div className="chat-feed" aria-live="polite">
        {blocks.length === 0 ? (
          <p className="feed-placeholder">No messages yet</p>
        ) : (
          blocks.map((block) =>
            block.type === "image" ? (
              <ImageCard key={block.id} image={block.image} onOpen={onOpenImage} />
            ) : (
              <div key={block.id} className="assistant-message">
                {block.text}
              </div>
            ),
          )
        )}
      </div>

      <form className="chat-form" onSubmit={handleSubmit}>
        <textarea
          value={input}
          onChange={(event) => setInput(event.target.value)}
          rows={3}
          aria-label="Message"
        />
        <button type="submit" disabled={isStreaming}>
          {isStreaming ? "Streaming" : "Send"}
        </button>
      </form>
    </aside>
  );
}
