import { useRef } from 'react';
import { gsap } from 'gsap';
import { useGSAP } from '@gsap/react';

interface ButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  variant?: 'primary' | 'secondary' | 'accent' | 'ghost' | 'outline';
  size?: 'xs' | 'sm' | 'md' | 'lg';
  disabled?: boolean;
  loading?: boolean;
  className?: string;
  type?: 'button' | 'submit' | 'reset';
}

export function Button({
  children,
  onClick,
  variant = 'primary',
  size = 'md',
  disabled = false,
  loading = false,
  className = '',
  type = 'button',
}: ButtonProps) {
  const buttonRef = useRef<HTMLButtonElement>(null);

  useGSAP(() => {
    if (!buttonRef.current || disabled || loading) return;

    const handleHover = () => {
      gsap.to(buttonRef.current, {
        scale: 1.05,
        duration: 0.2,
        ease: 'power2.out',
      });
    };

    const handleHoverOut = () => {
      gsap.to(buttonRef.current, {
        scale: 1,
        duration: 0.2,
        ease: 'power2.out',
      });
    };

    const button = buttonRef.current;
    button.addEventListener('mouseenter', handleHover);
    button.addEventListener('mouseleave', handleHoverOut);

    return () => {
      button.removeEventListener('mouseenter', handleHover);
      button.removeEventListener('mouseleave', handleHoverOut);
    };
  }, [disabled, loading]);

  const variantClass = {
    primary: 'btn-primary',
    secondary: 'btn-secondary',
    accent: 'btn-accent',
    ghost: 'btn-ghost',
    outline: 'btn-outline',
  }[variant];

  const sizeClass = {
    xs: 'btn-xs',
    sm: 'btn-sm',
    md: 'btn-md',
    lg: 'btn-lg',
  }[size];

  return (
    <button
      ref={buttonRef}
      type={type}
      className={`btn ${variantClass} ${sizeClass} ${className}`}
      onClick={onClick}
      disabled={disabled || loading}
    >
      {loading && <span className="loading loading-spinner"></span>}
      {children}
    </button>
  );
}
