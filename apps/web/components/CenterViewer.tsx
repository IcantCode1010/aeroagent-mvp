import type { ImageResult } from "../lib/types";

type CenterViewerProps = {
  image: ImageResult | null;
};

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export function CenterViewer({ image }: CenterViewerProps) {
  return (
    <section className="center-viewer" aria-label="Source viewer">
      {image ? (
        <>
          <div className="viewer-toolbar">
            <p className="eyebrow">Source image</p>
            <h2>{image.title}</h2>
          </div>
          <div className="image-stage">
            <img src={`${API_BASE_URL}${image.imageUrl}`} alt={image.title} />
          </div>
        </>
      ) : (
        <div className="empty-viewer">
          <p>No source selected</p>
        </div>
      )}
    </section>
  );
}
