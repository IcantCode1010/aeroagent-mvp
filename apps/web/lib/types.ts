export type StreamEventName =
  | "status"
  | "tool_start"
  | "tool_done"
  | "agent_token"
  | "image_result"
  | "ui_action"
  | "warning"
  | "done"
  | "error";

export type StreamEvent = {
  event: StreamEventName;
  data: Record<string, unknown>;
};

export type ImageResult = {
  imageId: string;
  title: string;
  thumbnailUrl: string;
  imageUrl: string;
  caption: string;
};

export type UIAction = {
  type: "open_image";
  payload: {
    imageId: string;
  };
};

export type ChatBlock =
  | {
      id: string;
      type: "text";
      text: string;
    }
  | {
      id: string;
      type: "image";
      image: ImageResult;
    };
