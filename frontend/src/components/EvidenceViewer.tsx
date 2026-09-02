type BBox = { x: number; y: number; w: number; h: number };

export default function EvidenceViewer({ imageUrl, bboxes }: { imageUrl: string; bboxes: BBox[] }) {
  return (
    <div style={{ position: "relative" }}>
      <img src={imageUrl} alt="Scan evidence" style={{ maxWidth: "100%" }} />
      {bboxes.map((b, i) => (
        <div
          key={i}
          style={{
            position: "absolute",
            left: b.x,
            top: b.y,
            width: b.w,
            height: b.h,
            border: "2px solid red",
          }}
        />
      ))}
    </div>
  );
}
