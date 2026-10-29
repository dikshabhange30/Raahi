import { useState } from "react";

// Drawn fallbacks, shown until (or unless) a real photo exists in /public/photos
const scenes = {
  city: (
    <svg viewBox="0 0 200 150" preserveAspectRatio="xMidYMid slice" aria-hidden="true">
      <rect width="200" height="150" fill="#f5dfcb" />
      <circle cx="150" cy="40" r="20" fill="#f0c9c4" />
      <g fill="#7a2e3a"><rect x="18" y="70" width="34" height="80" /><rect x="60" y="48" width="30" height="102" /><rect x="98" y="82" width="38" height="68" /></g>
      <rect x="142" y="60" width="38" height="90" fill="#7d8344" />
      <g fill="#fbf5ea"><rect x="26" y="80" width="7" height="9" /><rect x="38" y="80" width="7" height="9" /><rect x="26" y="98" width="7" height="9" /><rect x="68" y="60" width="7" height="9" /><rect x="68" y="78" width="7" height="9" /><rect x="106" y="94" width="7" height="9" /><rect x="150" y="74" width="7" height="9" /><rect x="162" y="92" width="7" height="9" /></g>
      <rect y="132" width="200" height="18" fill="#cfe3b0" />
    </svg>
  ),
  hills: (
    <svg viewBox="0 0 200 150" preserveAspectRatio="xMidYMid slice" aria-hidden="true">
      <rect width="200" height="150" fill="#e4efd0" />
      <circle cx="46" cy="38" r="18" fill="#e8d3a8" />
      <ellipse cx="60" cy="150" rx="110" ry="62" fill="#c9cf8f" />
      <ellipse cx="160" cy="154" rx="100" ry="54" fill="#7d8344" />
      <rect x="112" y="86" width="26" height="20" fill="#fbf5ea" /><path d="M108 88 L125 74 L142 88 Z" fill="#7a2e3a" />
    </svg>
  ),
  market: (
    <svg viewBox="0 0 200 150" preserveAspectRatio="xMidYMid slice" aria-hidden="true">
      <rect width="200" height="150" fill="#f7ecd2" />
      {[0, 1, 2, 3, 4, 5, 6, 7].map((i) => <rect key={i} x={i * 25} y="0" width="25" height="44" fill={i % 2 ? "#fbf5ea" : "#7a2e3a"} />)}
      <rect y="100" width="200" height="50" fill="#e8d3a8" />
      {[[30, 94, "#f0c9c4"], [58, 94, "#cfe3b0"], [86, 94, "#c9cf8f"], [114, 94, "#f0c9c4"], [142, 94, "#cfe3b0"], [170, 94, "#c9cf8f"]].map(([x, y, f], i) => <circle key={i} cx={x} cy={y} r="13" fill={f} stroke="#7a2e3a" strokeWidth="2" />)}
    </svg>
  ),
  home: (
    <svg viewBox="0 0 200 150" preserveAspectRatio="xMidYMid slice" aria-hidden="true">
      <rect width="200" height="150" fill="#f0c9c4" />
      <rect y="118" width="200" height="32" fill="#cfe3b0" />
      <rect x="52" y="64" width="96" height="58" fill="#f3e9d8" stroke="#7a2e3a" strokeWidth="3" />
      <path d="M42 66 L100 22 L158 66 Z" fill="#7a2e3a" />
      <rect x="90" y="86" width="20" height="36" fill="#7d8344" />
      <rect x="62" y="80" width="18" height="18" fill="#fbf5ea" stroke="#7a2e3a" strokeWidth="2" />
      <rect x="120" y="80" width="18" height="18" fill="#fbf5ea" stroke="#7a2e3a" strokeWidth="2" />
      <circle cx="176" cy="96" r="16" fill="#7d8344" /><rect x="174" y="108" width="4" height="14" fill="#7a2e3a" />
    </svg>
  ),
};

export default function Photo({ src, alt = "", caption, scene = "city", rotate = 0, className = "" }) {
  const [loaded, setLoaded] = useState(false);
  return (
    <figure className={`polaroid ${className}`} style={{ transform: `rotate(${rotate}deg)` }}>
      <span className="tape" aria-hidden="true" />
      <div className="polaroid-img">
        {scenes[scene]}
        {src && (
          <img
            src={`/photos/${src}`}
            alt={alt}
            className={loaded ? "show" : ""}
            onLoad={() => setLoaded(true)}
            onError={() => setLoaded(false)}
          />
        )}
      </div>
      {caption && <figcaption>{caption}</figcaption>}
    </figure>
  );
}
