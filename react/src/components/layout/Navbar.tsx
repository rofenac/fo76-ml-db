import { useRef } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { gsap } from 'gsap';
import { useGSAP } from '@gsap/react';

export function Navbar() {
  const location = useLocation();
  const navRef = useRef<HTMLDivElement>(null);

  useGSAP(() => {
    if (!navRef.current) return;

    gsap.from(navRef.current, {
      y: -100,
      opacity: 0,
      duration: 0.8,
      ease: 'power3.out',
    });
  }, []);

  const isActive = (path: string) => location.pathname === path;

  const navLinks = [
    { path: '/', label: 'Home' },
    { path: '/weapons', label: 'Weapons' },
    { path: '/armor', label: 'Armor' },
    { path: '/perks', label: 'Perks' },
    { path: '/mutations', label: 'Mutations' },
    { path: '/consumables', label: 'Consumables' },
    { path: '/chat', label: 'AI Chat' },
    { path: '/builder', label: 'Build Planner' },
  ];

  return (
    <div ref={navRef} className="navbar bg-base-300 shadow-lg sticky top-0 z-50">
      <div className="navbar-start">
        <div className="dropdown">
          <div tabIndex={0} role="button" className="btn btn-ghost lg:hidden">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-5 w-5"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M4 6h16M4 12h8m-8 6h16"
              />
            </svg>
          </div>
          <ul
            tabIndex={0}
            className="menu menu-sm dropdown-content mt-3 z-1 p-2 shadow bg-base-100 rounded-box w-52"
          >
            {navLinks.map((link) => (
              <li key={link.path}>
                <Link to={link.path} className={isActive(link.path) ? 'active' : ''}>
                  {link.label}
                </Link>
              </li>
            ))}
          </ul>
        </div>
        <Link to="/" className="btn btn-ghost text-xl">
          <span className="text-transparent bg-clip-text bg-linear-to-r from-blue-400 to-cyan-300">
            FO76 Builder
          </span>
        </Link>
      </div>

      <div className="navbar-center hidden lg:flex">
        <ul className="menu menu-horizontal px-1">
          {navLinks.slice(1).map((link) => (
            <li key={link.path}>
              <Link
                to={link.path}
                className={isActive(link.path) ? 'active' : ''}
              >
                {link.label}
              </Link>
            </li>
          ))}
        </ul>
      </div>

      <div className="navbar-end">
        <div className="badge badge-primary badge-sm">v1.0.0</div>
      </div>
    </div>
  );
}
