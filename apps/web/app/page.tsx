"use client";

import { useState } from "react";

import { CenterViewer } from "../components/CenterViewer";
import { ChatPanel } from "../components/ChatPanel";
import { LeftPanel } from "../components/LeftPanel";
import type { ImageResult } from "../lib/types";

export default function Home() {
  const [selectedImage, setSelectedImage] = useState<ImageResult | null>(null);

  return (
    <main className="workspace-shell">
      <LeftPanel />
      <CenterViewer image={selectedImage} />
      <ChatPanel onOpenImage={setSelectedImage} />
    </main>
  );
}
