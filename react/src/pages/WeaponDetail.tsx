import { useParams, useNavigate } from 'react-router-dom';
import { useRef } from 'react';
import { gsap } from 'gsap';
import { useGSAP } from '@gsap/react';
import { useAPI } from '../hooks/useAPI';
import { getWeaponById } from '../utils/api';
import { Loading, ErrorMessage, Card, Button } from '../components/ui';
import { formatDamage, formatNumber, formatWeight, formatValue, formatPercent } from '../utils/format';

export function WeaponDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const contentRef = useRef<HTMLDivElement>(null);

  const { data: weapon, loading, error } = useAPI(
    () => getWeaponById(Number(id)),
    [id]
  );

  useGSAP(() => {
    if (!contentRef.current || !weapon) return;

    gsap.from(contentRef.current.children, {
      opacity: 0,
      y: 30,
      stagger: 0.1,
      duration: 0.6,
      ease: 'power3.out',
    });
  }, [weapon]);

  if (loading) return <Loading text="Loading weapon details..." fullScreen />;
  if (error) return <ErrorMessage message={error} fullScreen />;
  if (!weapon) return <ErrorMessage message="Weapon not found" fullScreen />;

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <Button variant="ghost" onClick={() => navigate('/weapons')}>
        ← Back to Weapons
      </Button>

      <div ref={contentRef} className="space-y-6">
        {/* Header */}
        <Card className="bg-base-200">
          <h1 className="text-4xl font-bold text-blue-400 mb-4">{weapon.name}</h1>
          <div className="flex gap-3 flex-wrap">
            <div className="badge badge-lg badge-primary">{weapon.type}</div>
            <div className="badge badge-lg badge-secondary">{weapon.weapon_class}</div>
            <div className="badge badge-lg">Level {weapon.level_requirement}</div>
            {weapon.ammo_type && (
              <div className="badge badge-lg badge-accent">{weapon.ammo_type}</div>
            )}
          </div>
        </Card>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <Card className="bg-base-200">
            <h3 className="text-sm font-semibold text-gray-400 uppercase">Damage</h3>
            <p className="text-3xl font-bold text-green-400">{formatDamage(weapon.damage)}</p>
          </Card>

          <Card className="bg-base-200">
            <h3 className="text-sm font-semibold text-gray-400 uppercase">DPS</h3>
            <p className="text-3xl font-bold text-yellow-400">{formatNumber(weapon.dps, 1)}</p>
          </Card>

          <Card className="bg-base-200">
            <h3 className="text-sm font-semibold text-gray-400 uppercase">Fire Rate</h3>
            <p className="text-3xl font-bold text-blue-400">{formatNumber(weapon.fire_rate, 0)}</p>
          </Card>

          <Card className="bg-base-200">
            <h3 className="text-sm font-semibold text-gray-400 uppercase">Range</h3>
            <p className="text-3xl font-bold text-purple-400">{formatNumber(weapon.range, 0)}</p>
          </Card>

          <Card className="bg-base-200">
            <h3 className="text-sm font-semibold text-gray-400 uppercase">Accuracy</h3>
            <p className="text-3xl font-bold text-cyan-400">{formatNumber(weapon.accuracy, 0)}</p>
          </Card>

          <Card className="bg-base-200">
            <h3 className="text-sm font-semibold text-gray-400 uppercase">AP Cost</h3>
            <p className="text-3xl font-bold text-orange-400">{formatNumber(weapon.ap_cost, 0)}</p>
          </Card>
        </div>

        {/* Details */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card className="bg-base-200">
            <h3 className="text-xl font-bold text-gray-200 mb-4">Weapon Properties</h3>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-gray-400">Weight:</span>
                <span className="text-gray-200">{formatWeight(weapon.weight)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Value:</span>
                <span className="text-gray-200">{formatValue(weapon.value)}</span>
              </div>
              {weapon.ammo_capacity && (
                <div className="flex justify-between">
                  <span className="text-gray-400">Ammo Capacity:</span>
                  <span className="text-gray-200">{weapon.ammo_capacity}</span>
                </div>
              )}
              {weapon.damage_per_action_point && (
                <div className="flex justify-between">
                  <span className="text-gray-400">Damage per AP:</span>
                  <span className="text-gray-200">
                    {formatNumber(weapon.damage_per_action_point, 2)}
                  </span>
                </div>
              )}
            </div>
          </Card>

          {/* Legendary Modifiers */}
          <Card className="bg-base-200">
            <h3 className="text-xl font-bold text-gray-200 mb-4">Legendary Modifiers</h3>
            <div className="space-y-2">
              {weapon.two_shot_modifier && (
                <div className="flex justify-between">
                  <span className="text-gray-400">Two Shot:</span>
                  <span className="text-green-400">{formatPercent(weapon.two_shot_modifier)}</span>
                </div>
              )}
              {weapon.aae_modifier && (
                <div className="flex justify-between">
                  <span className="text-gray-400">Anti-Armor Explosive:</span>
                  <span className="text-green-400">{formatPercent(weapon.aae_modifier)}</span>
                </div>
              )}
              {weapon.bloodied_modifier && (
                <div className="flex justify-between">
                  <span className="text-gray-400">Bloodied:</span>
                  <span className="text-red-400">{formatPercent(weapon.bloodied_modifier)}</span>
                </div>
              )}
              {weapon.furious_modifier && (
                <div className="flex justify-between">
                  <span className="text-gray-400">Furious:</span>
                  <span className="text-orange-400">{formatPercent(weapon.furious_modifier)}</span>
                </div>
              )}
              {weapon.vampire_modifier && (
                <div className="flex justify-between">
                  <span className="text-gray-400">Vampire:</span>
                  <span className="text-purple-400">{formatPercent(weapon.vampire_modifier)}</span>
                </div>
              )}
            </div>
          </Card>
        </div>

        {/* Related Perks */}
        {weapon.affected_perks && weapon.affected_perks.length > 0 && (
          <Card className="bg-base-200">
            <h3 className="text-xl font-bold text-gray-200 mb-4">Related Perks</h3>
            <div className="flex gap-2 flex-wrap">
              {weapon.affected_perks.map((perk) => (
                <div key={perk.perk_id} className="badge badge-lg badge-outline">
                  {perk.name}
                </div>
              ))}
            </div>
          </Card>
        )}
      </div>
    </div>
  );
}
