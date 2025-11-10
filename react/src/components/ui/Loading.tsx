interface LoadingProps {
  size?: 'xs' | 'sm' | 'md' | 'lg';
  text?: string;
  fullScreen?: boolean;
}

export function Loading({ size = 'lg', text, fullScreen = false }: LoadingProps) {
  const sizeClass = {
    xs: 'loading-xs',
    sm: 'loading-sm',
    md: 'loading-md',
    lg: 'loading-lg',
  }[size];

  const content = (
    <div className="flex flex-col items-center justify-center gap-4">
      <span className={`loading loading-spinner ${sizeClass} text-primary`}></span>
      {text && <p className="text-lg text-gray-400">{text}</p>}
    </div>
  );

  if (fullScreen) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        {content}
      </div>
    );
  }

  return <div className="flex items-center justify-center p-8">{content}</div>;
}
