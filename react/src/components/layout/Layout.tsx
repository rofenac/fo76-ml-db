import type { ReactNode } from 'react';
import { Navbar } from './Navbar';

interface LayoutProps {
  children: ReactNode;
}

export function Layout({ children }: LayoutProps) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-800">
      <Navbar />
      <main className="container mx-auto px-4 py-8">
        {children}
      </main>
      <footer className="footer footer-center p-10 bg-base-200 text-base-content rounded mt-16">
        <div className="grid grid-flow-col gap-4">
          <span className="text-sm text-gray-400">
            Fallout 76 Character Builder - Powered by RAG & Claude AI
          </span>
        </div>
        <div>
          <p className="text-xs text-gray-500">
            Data sourced from Fallout Wiki | Personal academic project
          </p>
        </div>
      </footer>
    </div>
  );
}
