import { useState, useRef } from 'react';
import { gsap } from 'gsap';
import { useGSAP } from '@gsap/react';
import { useLocalStorage } from '../hooks/useLocalStorage';
import { Button, Card } from '../components/ui';
import { SPECIAL_STATS, MAX_SPECIAL, MIN_SPECIAL, STORAGE_KEYS } from '../config/constants';
import type { CharacterBuild, SpecialStats } from '../types/api';

export function BuildPlanner() {
  const [builds, setBuilds] = useLocalStorage<CharacterBuild[]>(STORAGE_KEYS.BUILDS, []);
  const [currentBuild, setCurrentBuild] = useState<CharacterBuild>({
    name: 'My Build',
    description: '',
    level: 50,
    special_stats: {
      strength: 1,
      perception: 1,
      endurance: 1,
      charisma: 1,
      intelligence: 1,
      agility: 1,
      luck: 1,
    },
    perks: [],
    legendary_perks: [],
    weapons: [],
    armor: [],
    mutations: [],
    consumables: [],
  });

  const [shareUrl, setShareUrl] = useState('');
  const specialRef = useRef<HTMLDivElement>(null);

  useGSAP(() => {
    if (!specialRef.current) return;

    gsap.from(specialRef.current.children, {
      opacity: 0,
      x: -30,
      stagger: 0.1,
      duration: 0.5,
      ease: 'power2.out',
    });
  }, []);

  const totalSpecialPoints = Object.values(currentBuild.special_stats).reduce(
    (sum, val) => sum + val,
    0
  );
  const availablePoints = currentBuild.level > 50 ? 56 : 21 + currentBuild.level;
  const remainingPoints = availablePoints - totalSpecialPoints;

  const handleSpecialChange = (stat: keyof SpecialStats, value: number) => {
    const newValue = Math.max(MIN_SPECIAL, Math.min(MAX_SPECIAL, value));
    setCurrentBuild((prev) => ({
      ...prev,
      special_stats: {
        ...prev.special_stats,
        [stat]: newValue,
      },
    }));
  };

  const handleSave = () => {
    const buildToSave = {
      ...currentBuild,
      id: currentBuild.id || Date.now().toString(),
      created_at: currentBuild.created_at || new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    const existingIndex = builds.findIndex((b) => b.id === buildToSave.id);
    if (existingIndex >= 0) {
      const updatedBuilds = [...builds];
      updatedBuilds[existingIndex] = buildToSave;
      setBuilds(updatedBuilds);
    } else {
      setBuilds([...builds, buildToSave]);
    }

    alert('Build saved successfully!');
  };

  const handleShare = () => {
    const encoded = btoa(JSON.stringify(currentBuild));
    const url = `${window.location.origin}${window.location.pathname}#/builder?build=${encoded}`;
    setShareUrl(url);
    navigator.clipboard.writeText(url);
    alert('Build URL copied to clipboard!');
  };

  const handleLoad = (build: CharacterBuild) => {
    setCurrentBuild(build);
  };

  const handleReset = () => {
    if (confirm('Reset build to default values?')) {
      setCurrentBuild({
        name: 'My Build',
        description: '',
        level: 50,
        special_stats: {
          strength: 1,
          perception: 1,
          endurance: 1,
          charisma: 1,
          intelligence: 1,
          agility: 1,
          luck: 1,
        },
        perks: [],
        legendary_perks: [],
        weapons: [],
        armor: [],
        mutations: [],
        consumables: [],
      });
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="text-center space-y-2">
        <h1 className="text-4xl font-bold text-blue-400">Build Planner</h1>
        <p className="text-gray-400">Create and optimize your character build</p>
      </div>

      {/* Build Info */}
      <Card className="bg-base-200">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="form-control">
            <label className="label">
              <span className="label-text">Build Name</span>
            </label>
            <input
              type="text"
              className="input input-bordered"
              value={currentBuild.name}
              onChange={(e) => setCurrentBuild({ ...currentBuild, name: e.target.value })}
            />
          </div>

          <div className="form-control">
            <label className="label">
              <span className="label-text">Character Level</span>
            </label>
            <input
              type="number"
              className="input input-bordered"
              min="1"
              max="1000"
              value={currentBuild.level}
              onChange={(e) =>
                setCurrentBuild({ ...currentBuild, level: Number(e.target.value) })
              }
            />
          </div>

          <div className="form-control">
            <label className="label">
              <span className="label-text">Points Available</span>
            </label>
            <div className="input input-bordered flex items-center">
              <span className={remainingPoints < 0 ? 'text-error' : 'text-success'}>
                {remainingPoints} / {availablePoints}
              </span>
            </div>
          </div>
        </div>

        <div className="form-control mt-4">
          <label className="label">
            <span className="label-text">Description</span>
          </label>
          <textarea
            className="textarea textarea-bordered h-24"
            placeholder="Describe your build strategy..."
            value={currentBuild.description}
            onChange={(e) => setCurrentBuild({ ...currentBuild, description: e.target.value })}
          />
        </div>
      </Card>

      {/* SPECIAL Stats */}
      <Card className="bg-base-200">
        <h2 className="text-2xl font-bold mb-6">SPECIAL Attributes</h2>
        <div ref={specialRef} className="space-y-4">
          {SPECIAL_STATS.map((stat) => {
            const value = currentBuild.special_stats[stat.key as keyof SpecialStats];
            return (
              <div key={stat.key} className="flex items-center gap-4">
                <div className="w-32">
                  <span className={`text-lg font-bold ${stat.color}`}>{stat.label}</span>
                </div>
                <input
                  type="range"
                  min={MIN_SPECIAL}
                  max={MAX_SPECIAL}
                  value={value}
                  className="range range-primary flex-1"
                  onChange={(e) =>
                    handleSpecialChange(stat.key as keyof SpecialStats, Number(e.target.value))
                  }
                />
                <div className="flex gap-2 items-center">
                  <button
                    className="btn btn-sm btn-circle"
                    onClick={() => handleSpecialChange(stat.key as keyof SpecialStats, value - 1)}
                  >
                    -
                  </button>
                  <span className="text-2xl font-bold w-12 text-center">{value}</span>
                  <button
                    className="btn btn-sm btn-circle"
                    onClick={() => handleSpecialChange(stat.key as keyof SpecialStats, value + 1)}
                  >
                    +
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      </Card>

      {/* Build Sections (Placeholders) */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card className="bg-base-200">
          <h3 className="text-xl font-bold mb-4">Perks</h3>
          <p className="text-gray-400 text-sm">
            Perk selection coming soon. Use the Perks page to browse available perks.
          </p>
        </Card>

        <Card className="bg-base-200">
          <h3 className="text-xl font-bold mb-4">Equipment</h3>
          <p className="text-gray-400 text-sm">
            Equipment selection coming soon. Browse weapons and armor in their respective pages.
          </p>
        </Card>

        <Card className="bg-base-200">
          <h3 className="text-xl font-bold mb-4">Mutations</h3>
          <p className="text-gray-400 text-sm">
            Mutation selection coming soon. View all mutations on the Mutations page.
          </p>
        </Card>

        <Card className="bg-base-200">
          <h3 className="text-xl font-bold mb-4">Consumables</h3>
          <p className="text-gray-400 text-sm">
            Consumable selection coming soon. Check the Consumables page for options.
          </p>
        </Card>
      </div>

      {/* Actions */}
      <Card className="bg-base-200">
        <div className="flex gap-3 flex-wrap justify-center">
          <Button variant="primary" size="lg" onClick={handleSave}>
            💾 Save Build
          </Button>
          <Button variant="accent" size="lg" onClick={handleShare}>
            🔗 Share Build
          </Button>
          <Button variant="outline" onClick={handleReset}>
            🔄 Reset
          </Button>
        </div>

        {shareUrl && (
          <div className="mt-4 p-4 bg-base-300 rounded-lg">
            <p className="text-sm text-gray-400 mb-2">Share URL (copied to clipboard):</p>
            <code className="text-xs break-all">{shareUrl}</code>
          </div>
        )}
      </Card>

      {/* Saved Builds */}
      {builds.length > 0 && (
        <Card className="bg-base-200">
          <h2 className="text-2xl font-bold mb-4">Saved Builds ({builds.length})</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {builds.map((build) => (
              <div key={build.id} className="p-4 bg-base-300 rounded-lg">
                <h3 className="font-bold text-lg">{build.name}</h3>
                <p className="text-sm text-gray-400">Level {build.level}</p>
                <p className="text-xs text-gray-500 mt-2">
                  {build.description || 'No description'}
                </p>
                <div className="mt-3 flex gap-2">
                  <Button size="sm" onClick={() => handleLoad(build)}>
                    Load
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => {
                      if (confirm('Delete this build?')) {
                        setBuilds(builds.filter((b) => b.id !== build.id));
                      }
                    }}
                  >
                    Delete
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  );
}
