const C = {
  maroon: "#7a2e3a", pista: "#cfe3b0", olive: "#7d8344", oliveSoft: "#c9cf8f",
  beige: "#f3e9d8", blush: "#f0c9c4", rose: "#e3a5a9", sand: "#e8d3a8", cream: "#fbf5ea",
};
const S = { stroke: C.maroon, strokeWidth: 3, strokeLinejoin: "round", strokeLinecap: "round" };

const shapes = {
  sparkle: () => <path d="M50 6 L61 38 L94 50 L61 62 L50 94 L39 62 L6 50 L39 38 Z" fill={C.pista} {...S} />,
  flower: () => (
    <g {...S}>
      {[[50, 22], [74, 36], [74, 64], [50, 78], [26, 64], [26, 36]].map(([x, y], i) => (
        <circle key={i} cx={x} cy={y} r="15" fill={C.blush} />
      ))}
      <circle cx="50" cy="50" r="12" fill={C.sand} />
    </g>
  ),
  sun: () => (
    <g {...S}>
      {[0, 45, 90, 135, 180, 225, 270, 315].map((a) => {
        const r = (a * Math.PI) / 180;
        return <line key={a} x1={50 + 30 * Math.cos(r)} y1={50 + 30 * Math.sin(r)} x2={50 + 42 * Math.cos(r)} y2={50 + 42 * Math.sin(r)} />;
      })}
      <circle cx="50" cy="50" r="22" fill={C.sand} />
    </g>
  ),
  heart: () => <path d="M50 84 C10 56 14 22 36 22 C44 22 50 28 50 34 C50 28 56 22 64 22 C86 22 90 56 50 84 Z" fill={C.rose} {...S} />,
  chai: () => (
    <g {...S}>
      <ellipse cx="47" cy="86" rx="32" ry="6" fill={C.pista} />
      <path d="M70 48 H78 Q90 48 90 58 Q90 70 76 70 H68" fill="none" />
      <path d="M22 42 H71 V62 Q71 82 46 82 Q22 82 22 62 Z" fill={C.cream} />
      <path d="M36 32 Q30 24 36 16 M52 32 Q46 24 52 16" fill="none" />
    </g>
  ),
  bag: () => (
    <g {...S}>
      <path d="M38 36 V28 Q38 22 44 22 H56 Q62 22 62 28 V36" fill="none" />
      <rect x="16" y="36" width="68" height="48" rx="9" fill={C.oliveSoft} />
      <path d="M16 56 H84" fill="none" />
      <rect x="44" y="52" width="12" height="10" rx="2" fill={C.cream} />
    </g>
  ),
  compass: () => (
    <g {...S}>
      <circle cx="50" cy="50" r="38" fill={C.cream} />
      <polygon points="50,18 60,50 40,50" fill={C.maroon} />
      <polygon points="50,82 60,50 40,50" fill={C.pista} />
      <circle cx="50" cy="50" r="4" fill={C.cream} />
    </g>
  ),
  speech: () => (
    <g {...S}>
      <path d="M16 22 H84 Q92 22 92 30 V58 Q92 66 84 66 H48 L28 84 V66 H16 Q8 66 8 58 V30 Q8 22 16 22 Z" fill={C.pista} />
      <circle cx="32" cy="44" r="3.5" fill={C.maroon} />
      <circle cx="50" cy="44" r="3.5" fill={C.maroon} />
      <circle cx="68" cy="44" r="3.5" fill={C.maroon} />
    </g>
  ),
  house: () => (
    <g {...S}>
      <path d="M14 50 H86 V86 H14 Z" fill={C.sand} />
      <path d="M6 52 L50 14 L94 52 Z" fill={C.maroon} />
      <rect x="42" y="58" width="16" height="28" fill={C.pista} />
    </g>
  ),
  leaf: () => (
    <g {...S}>
      <path d="M18 82 Q14 30 72 16 Q86 58 40 82 Z" fill={C.olive} />
      <path d="M18 82 L62 36" fill="none" stroke={C.cream} />
    </g>
  ),
  pin: () => (
    <g {...S}>
      <path d="M50 92 C28 64 24 52 24 40 A26 26 0 0 1 76 40 C76 52 72 64 50 92 Z" fill={C.maroon} />
      <circle cx="50" cy="40" r="10" fill={C.cream} />
    </g>
  ),
  shield: () => (
    <g {...S}>
      <path d="M50 8 L84 21 V50 Q84 76 50 92 Q16 76 16 50 V21 Z" fill={C.pista} />
      <path d="M35 50 L46 61 L66 38" fill="none" />
    </g>
  ),
};

export default function Sticker({ name, size = 64, rotate = 0, className = "", style }) {
  const draw = shapes[name] || shapes.sparkle;
  return (
    <svg
      className={`sticker ${className}`}
      viewBox="0 0 100 100"
      width={size}
      height={size}
      style={{ transform: `rotate(${rotate}deg)`, ...style }}
      aria-hidden="true"
      focusable="false"
    >
      {draw()}
    </svg>
  );
}
