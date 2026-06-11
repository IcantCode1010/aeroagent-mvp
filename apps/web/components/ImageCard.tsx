import type { ImageResult } from "../lib/types";

type ImageCardProps = {
  image: ImageResult;
  onOpen: (image: ImageResult) => void;
};

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export function ImageCard({ image, onOpen }: ImageCardProps) {
  return (
    <article className="image-card">
      <img src={`${API_BASE_URL}${image.thumbnailUrl}`} alt="" />
      <div className="image-card-body">
        <h3>{image.title}</h3>
        <p>{image.caption}</p>
        <button type="button" onClick={() => onOpen(image)}>
          Open
        </button>
      </div>
    </article>
  );
}
