import { useRef } from 'react';
import type { ReactNode } from 'react';
import { gsap } from 'gsap';
import { useGSAP } from '@gsap/react';

interface CardProps {
  children: ReactNode;
  title?: string;
  className?: string;
  onClick?: () => void;
  hoverable?: boolean;
  animateOnMount?: boolean;
}

export function Card({
  children,
  title,
  className = '',
  onClick,
  hoverable = true,
  animateOnMount = false,
}: CardProps) {
  const cardRef = useRef<HTMLDivElement>(null);

  useGSAP(() => {
    if (!cardRef.current) return;

    // Animate on mount
    if (animateOnMount) {
      gsap.from(cardRef.current, {
        opacity: 0,
        y: 30,
        duration: 0.6,
        ease: 'power3.out',
      });
    }

    // Hover animation
    if (hoverable) {
      const handleHover = () => {
        gsap.to(cardRef.current, {
          y: -5,
          scale: 1.02,
          duration: 0.3,
          ease: 'power2.out',
        });
      };

      const handleHoverOut = () => {
        gsap.to(cardRef.current, {
          y: 0,
          scale: 1,
          duration: 0.3,
          ease: 'power2.out',
        });
      };

      const card = cardRef.current;
      card.addEventListener('mouseenter', handleHover);
      card.addEventListener('mouseleave', handleHoverOut);

      return () => {
        card.removeEventListener('mouseenter', handleHover);
        card.removeEventListener('mouseleave', handleHoverOut);
      };
    }
  }, [hoverable, animateOnMount]);

  return (
    <div
      ref={cardRef}
      className={`card bg-base-100 shadow-xl ${hoverable ? 'hover:shadow-2xl transition-shadow cursor-pointer' : ''} ${className}`}
      onClick={onClick}
    >
      <div className="card-body">
        {title && <h2 className="card-title">{title}</h2>}
        {children}
      </div>
    </div>
  );
}
