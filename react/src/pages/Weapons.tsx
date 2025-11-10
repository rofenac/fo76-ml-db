import { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { usePaginatedAPI, useDebounce } from '../hooks/useAPI';
import { getWeapons, getWeaponTypes, getWeaponClasses } from '../utils/api';
import { useAPI } from '../hooks/useAPI';
import { SearchBar, Select, Pagination, Loading, ErrorMessage, Card } from '../components/ui';
import { formatDamage, formatNumber, formatWeight, formatValue } from '../utils/format';
import type { WeaponFilters } from '../types/api';

export function Weapons() {
  const navigate = useNavigate();
  const [filters, setFilters] = useState<WeaponFilters>({});
  const [searchTerm, setSearchTerm] = useState('');
  const debouncedSearch = useDebounce(searchTerm, 500);

  const { data: weaponTypes } = useAPI(() => getWeaponTypes(), []);
  const { data: weaponClasses } = useAPI(() => getWeaponClasses(), []);

  const fetcher = useCallback(
    (page: number, pageSize: number) =>
      getWeapons({ ...filters, search: debouncedSearch }, page, pageSize),
    [filters, debouncedSearch]
  );

  const {
    data: weapons,
    total,
    page,
    pageSize,
    totalPages,
    loading,
    error,
    goToPage,
    changePageSize,
  } = usePaginatedAPI(fetcher, 20);

  const handleFilterChange = (key: keyof WeaponFilters, value: string) => {
    setFilters((prev) => ({
      ...prev,
      [key]: value || undefined,
    }));
  };

  if (error) {
    return <ErrorMessage message={error} fullScreen />;
  }

  return (
    <div className="space-y-6">
      <div className="text-center space-y-2">
        <h1 className="text-4xl font-bold text-blue-400">Weapons Database</h1>
        <p className="text-gray-400">Browse all {total} weapons in Fallout 76</p>
      </div>

      {/* Filters */}
      <Card className="bg-base-200">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <SearchBar
            value={searchTerm}
            onChange={setSearchTerm}
            placeholder="Search weapons..."
          />

          <Select
            value={filters.type || ''}
            onChange={(value) => handleFilterChange('type', value)}
            options={(weaponTypes || []).map((type) => ({ value: type, label: type }))}
            placeholder="All Types"
            label="Type"
          />

          <Select
            value={filters.weapon_class || ''}
            onChange={(value) => handleFilterChange('weapon_class', value)}
            options={(weaponClasses || []).map((cls) => ({ value: cls, label: cls }))}
            placeholder="All Classes"
            label="Class"
          />

          <Select
            value={pageSize.toString()}
            onChange={(value) => changePageSize(Number(value))}
            options={[
              { value: '10', label: '10 per page' },
              { value: '20', label: '20 per page' },
              { value: '50', label: '50 per page' },
            ]}
            label="Per Page"
          />
        </div>
      </Card>

      {/* Results */}
      {loading ? (
        <Loading text="Loading weapons..." />
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {weapons.map((weapon) => (
              <Card
                key={weapon.weapon_id}
                hoverable
                onClick={() => navigate(`/weapons/${weapon.weapon_id}`)}
              >
                <h3 className="text-xl font-bold text-blue-300">{weapon.name}</h3>
                <div className="grid grid-cols-2 gap-2 mt-4 text-sm">
                  <div>
                    <span className="text-gray-400">Type:</span>
                    <span className="ml-2 text-gray-200">{weapon.type}</span>
                  </div>
                  <div>
                    <span className="text-gray-400">Class:</span>
                    <span className="ml-2 text-gray-200">{weapon.weapon_class}</span>
                  </div>
                  <div>
                    <span className="text-gray-400">Damage:</span>
                    <span className="ml-2 text-green-400 font-bold">
                      {formatDamage(weapon.damage)}
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-400">DPS:</span>
                    <span className="ml-2 text-yellow-400">
                      {formatNumber(weapon.dps, 1)}
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-400">Weight:</span>
                    <span className="ml-2 text-gray-200">{formatWeight(weapon.weight)}</span>
                  </div>
                  <div>
                    <span className="text-gray-400">Value:</span>
                    <span className="ml-2 text-gray-200">{formatValue(weapon.value)}</span>
                  </div>
                </div>
                <div className="mt-3">
                  <div className="badge badge-sm badge-outline">{weapon.ammo_type || 'N/A'}</div>
                  <div className="badge badge-sm badge-outline ml-2">
                    Lvl {weapon.level_requirement}
                  </div>
                </div>
              </Card>
            ))}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex justify-center">
              <Pagination currentPage={page} totalPages={totalPages} onPageChange={goToPage} />
            </div>
          )}
        </>
      )}
    </div>
  );
}
