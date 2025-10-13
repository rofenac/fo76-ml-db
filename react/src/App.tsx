import { gsap } from "gsap";
import { useGSAP } from "@gsap/react";
import { useRef } from 'react';
import './index.css'

function App() {
  const titleRef = useRef<HTMLHeadingElement>(null);
  const subtitleRef = useRef<HTMLParagraphElement>(null);
  const cardsRef = useRef<HTMLDivElement>(null);

  useGSAP(() => {
    const tl = gsap.timeline();

    tl.from(titleRef.current, {
      opacity: 0,
      y: -50,
      duration: 1,
      ease: "power3.out"
    })
    .from(subtitleRef.current, {
      opacity: 0,
      y: -30,
      duration: 0.8,
      ease: "power3.out"
    }, "-=0.5")
    .from(cardsRef.current?.children || [], {
      opacity: 0,
      y: 50,
      stagger: 0.2,
      duration: 0.8,
      ease: "power3.out"
    }, "-=0.4");
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-800">
      <div className="container mx-auto px-4 py-16">
        <div className="text-center mb-16">
          <h1
            ref={titleRef}
            className="text-6xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-cyan-300 mb-4"
          >
            Fallout 76 Character Builder
          </h1>
          <p
            ref={subtitleRef}
            className="text-xl text-gray-300 max-w-2xl mx-auto"
          >
            Build, optimize, and explore character builds powered by AI and comprehensive game data
          </p>
        </div>

        <div ref={cardsRef} className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl mx-auto">
          <div className="card bg-base-100 shadow-xl hover:shadow-2xl transition-shadow">
            <div className="card-body">
              <h2 className="card-title text-2xl text-blue-400">
                262 Weapons
              </h2>
              <p className="text-gray-300">
                Complete database of ranged, melee, grenades, mines, and specialty weapons with full damage stats and perk relationships.
              </p>
            </div>
          </div>

          <div className="card bg-base-100 shadow-xl hover:shadow-2xl transition-shadow">
            <div className="card-body">
              <h2 className="card-title text-2xl text-cyan-400">
                477 Armor Pieces
              </h2>
              <p className="text-gray-300">
                Unified armor database covering 18 regular armor sets and 12 power armor sets with complete resistance data.
              </p>
            </div>
          </div>

          <div className="card bg-base-100 shadow-xl hover:shadow-2xl transition-shadow">
            <div className="card-body">
              <h2 className="card-title text-2xl text-purple-400">
                268 Perks
              </h2>
              <p className="text-gray-300">
                240 regular SPECIAL perks with 449 ranks and 28 legendary perks with all progression tiers.
              </p>
            </div>
          </div>
        </div>

        <div className="mt-16 text-center">
          <div className="alert alert-info max-w-2xl mx-auto shadow-lg">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" className="stroke-current shrink-0 w-6 h-6">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
            <div>
              <h3 className="font-bold">Powered by RAG & Claude AI</h3>
              <div className="text-sm">Ask questions about builds, compare weapons, and optimize your character with AI assistance</div>
            </div>
          </div>
        </div>

        <div className="mt-12 text-center">
          <div className="badge badge-outline badge-lg">MySQL Database</div>
          <div className="badge badge-outline badge-lg mx-2">RAG Interface</div>
          <div className="badge badge-outline badge-lg">Real-time Queries</div>
        </div>
      </div>
    </div>
  )
}

export default App
