import { useRef, useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { gsap } from 'gsap';
import { useGSAP } from '@gsap/react';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { getStats } from '../utils/api';

export function Home() {
  const titleRef = useRef<HTMLHeadingElement>(null);
  const subtitleRef = useRef<HTMLParagraphElement>(null);
  const cardsRef = useRef<HTMLDivElement>(null);
  const ctaRef = useRef<HTMLDivElement>(null);

  const [stats, setStats] = useState({
    total_weapons: 262,
    total_armor: 477,
    total_perks: 268,
    total_mutations: 19,
    total_consumables: 11,
  });

  useEffect(() => {
    getStats()
      .then(setStats)
      .catch(console.error);
  }, []);

  useGSAP(() => {
    const tl = gsap.timeline();

    tl.from(titleRef.current, {
      opacity: 0,
      y: -50,
      duration: 1,
      ease: 'power3.out',
    })
      .from(
        subtitleRef.current,
        {
          opacity: 0,
          y: -30,
          duration: 0.8,
          ease: 'power3.out',
        },
        '-=0.5'
      )
      .from(
        cardsRef.current?.children || [],
        {
          opacity: 0,
          y: 50,
          stagger: 0.15,
          duration: 0.8,
          ease: 'power3.out',
        },
        '-=0.4'
      )
      .from(
        ctaRef.current,
        {
          opacity: 0,
          scale: 0.8,
          duration: 0.6,
          ease: 'back.out(1.7)',
        },
        '-=0.3'
      );
  }, []);

  return (
    <div className="space-y-16">
      {/* Hero Section */}
      <div className="text-center space-y-6">
        <h1
          ref={titleRef}
          className="text-6xl font-bold text-transparent bg-clip-text bg-linear-to-r from-blue-400 to-cyan-300"
        >
          Fallout 76 Character Builder
        </h1>
        <p ref={subtitleRef} className="text-xl text-gray-300 max-w-2xl mx-auto">
          Build, optimize, and explore character builds powered by AI and comprehensive game data
        </p>
      </div>

      {/* Stats Cards */}
      <div ref={cardsRef} className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Link to="/weapons">
          <Card hoverable>
            <h2 className="card-title text-2xl text-blue-400">
              {stats.total_weapons} Weapons
            </h2>
            <p className="text-gray-300">
              Complete database of ranged, melee, grenades, mines, and specialty weapons with full
              damage stats and perk relationships.
            </p>
          </Card>
        </Link>

        <Link to="/armor">
          <Card hoverable>
            <h2 className="card-title text-2xl text-cyan-400">{stats.total_armor} Armor Pieces</h2>
            <p className="text-gray-300">
              Unified armor database covering 18 regular armor sets and 12 power armor sets with
              complete resistance data.
            </p>
          </Card>
        </Link>

        <Link to="/perks">
          <Card hoverable>
            <h2 className="card-title text-2xl text-purple-400">{stats.total_perks} Perks</h2>
            <p className="text-gray-300">
              240 regular SPECIAL perks with 449 ranks and 28 legendary perks with all progression
              tiers.
            </p>
          </Card>
        </Link>

        <Link to="/mutations">
          <Card hoverable>
            <h2 className="card-title text-2xl text-green-400">
              {stats.total_mutations} Mutations
            </h2>
            <p className="text-gray-300">
              All character mutations with positive and negative effects, plus perk interactions
              and suppression info.
            </p>
          </Card>
        </Link>

        <Link to="/consumables">
          <Card hoverable>
            <h2 className="card-title text-2xl text-yellow-400">
              {stats.total_consumables} Consumables
            </h2>
            <p className="text-gray-300">
              Build-relevant consumables including food, drinks, and chems with duration and effect
              data.
            </p>
          </Card>
        </Link>

        <Link to="/chat">
          <Card hoverable>
            <h2 className="card-title text-2xl text-pink-400">AI Chat Assistant</h2>
            <p className="text-gray-300">
              Ask questions about builds, compare items, and get AI-powered recommendations using
              RAG technology.
            </p>
          </Card>
        </Link>
      </div>

      {/* CTA Section */}
      <div ref={ctaRef} className="text-center space-y-6">
        <Card className="max-w-3xl mx-auto bg-base-200">
          <div className="flex items-center gap-4">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              className="stroke-info shrink-0 w-10 h-10"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <div className="text-left">
              <h3 className="font-bold text-lg">Powered by RAG & Claude AI</h3>
              <p className="text-sm text-gray-400">
                Hybrid search combining MySQL database queries with AI-powered semantic search for
                intelligent build recommendations
              </p>
            </div>
          </div>
        </Card>

        <div className="flex gap-4 justify-center">
          <Link to="/builder">
            <Button variant="primary" size="lg">
              Start Building
            </Button>
          </Link>
          <Link to="/chat">
            <Button variant="accent" size="lg">
              Ask AI
            </Button>
          </Link>
        </div>

        <div className="flex gap-3 justify-center flex-wrap">
          <div className="badge badge-outline badge-lg">MySQL 3NF Database</div>
          <div className="badge badge-outline badge-lg">ChromaDB Vector Search</div>
          <div className="badge badge-outline badge-lg">Claude AI</div>
          <div className="badge badge-outline badge-lg">OpenAI Embeddings</div>
        </div>
      </div>
    </div>
  );
}
