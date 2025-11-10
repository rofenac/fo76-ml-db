import { useState, useRef } from 'react';
import { gsap } from 'gsap';
import { useGSAP } from '@gsap/react';

interface SearchBarProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  className?: string;
}

export function SearchBar({
  value,
  onChange,
  placeholder = 'Search...',
  className = '',
}: SearchBarProps) {
  const [isFocused, setIsFocused] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const iconRef = useRef<SVGSVGElement>(null);

  useGSAP(() => {
    if (!iconRef.current) return;

    if (isFocused) {
      gsap.to(iconRef.current, {
        rotation: 90,
        scale: 1.2,
        duration: 0.3,
        ease: 'back.out(1.7)',
      });
    } else {
      gsap.to(iconRef.current, {
        rotation: 0,
        scale: 1,
        duration: 0.3,
        ease: 'power2.out',
      });
    }
  }, [isFocused]);

  return (
    <div className={`form-control ${className}`}>
      <div className="input-group">
        <input
          ref={inputRef}
          type="text"
          placeholder={placeholder}
          className="input input-bordered w-full"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
        />
        <button className="btn btn-square">
          <svg
            ref={iconRef}
            xmlns="http://www.w3.org/2000/svg"
            className="h-6 w-6"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            />
          </svg>
        </button>
      </div>
    </div>
  );
}
