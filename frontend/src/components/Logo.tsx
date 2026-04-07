export function AllTrailsToStravaLogo({ className = "", size = 120 }: { className?: string; size?: number }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 120 120"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
    >
      <title>AllTrails to Strava Logo</title>
      
      {/* Background Circle */}
      <circle cx="60" cy="60" r="58" fill="url(#gradient)" />
      
      {/* Mountain/Trail Path */}
      <path
        d="M30 70 L45 45 L60 55 L75 35 L90 50"
        stroke="white"
        strokeWidth="4"
        strokeLinecap="round"
        strokeLinejoin="round"
        fill="none"
        opacity="0.9"
      />
      
      {/* Activity Points */}
      <circle cx="30" cy="70" r="3" fill="white" />
      <circle cx="45" cy="45" r="3" fill="white" />
      <circle cx="60" cy="55" r="3" fill="white" />
      <circle cx="75" cy="35" r="3" fill="white" />
      <circle cx="90" cy="50" r="3" fill="white" />
      
      {/* Sync Arrow */}
      <g transform="translate(60, 75)">
        <path
          d="M-15 0 L0 -10 L0 -4 L15 -4 L15 4 L0 4 L0 10 Z"
          fill="white"
          opacity="0.95"
        />
      </g>
      
      {/* Inner Circle Accent */}
      <circle cx="60" cy="60" r="48" stroke="white" strokeWidth="1" opacity="0.2" fill="none" />
      
      {/* Gradient Definition */}
      <defs>
        <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#FC4C02" />
          <stop offset="50%" stopColor="#FF6B35" />
          <stop offset="100%" stopColor="#FC4C02" />
        </linearGradient>
      </defs>
    </svg>
  );
}
 
export default AllTrailsToStravaLogo;
 