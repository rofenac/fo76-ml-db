import { useRef } from 'react';
import { gsap } from 'gsap';
import { useGSAP } from '@gsap/react';

interface StatBadgeProps {
  label: string;
  value: string | number;
  color?: string;
  icon?: React.ReactNode;
  className?: string;
  animateOnMount?: boolean;
}

export function StatBadge({
  label,
  value,
  color = 'badge-primary',
  icon,
  className = '',
  animateOnMount = false,
}: StatBadgeProps) {
  const badgeRef = useRef<HTMLDivElement>(null);

  useGSAP(() => {
    if (!badgeRef.current || !animateOnMount) return;

    gsap.from(badgeRef.current, {
      scale: 0,
      opacity: 0,
      duration: 0.5,
      ease: 'back.out(1.7)',
    });
  }, [animateOnMount]);

  return (
    <div
      ref={badgeRef}
      className={`stat bg-base-200 rounded-lg ${className}`}
    >
      <div className="stat-figure text-primary">
        {icon}
      </div>
      <div className="stat-title">{label}</div>
      <div className={`stat-value ${color}`}>{value}</div>
    </div>
  );
}
