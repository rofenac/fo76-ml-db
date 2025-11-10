import { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { usePaginatedAPI, useDebounce } from '../hooks/useAPI';
import { getArmor, getArmorTypes, getArmorClasses, getArmorSlots } from '../utils/api';
import { useAPI } from '../hooks/useAPI';
import { SearchBar, Select, Pagination, Loading, ErrorMessage, Card } from '../components/ui';
import { formatNumber, formatWeight } from '../utils/format';
import type { ArmorFilters } from '../types/api';

export function Armor() {
  const navigate = useNavigate();
  const [filters, setFilters] = useState<ArmorFilters>({});
  const [searchTerm, setSearchTerm] = useState('');
  const debouncedSearch = useDebounce(searchTerm, 500);

  const { data: armorTypes } = useAPI(() => getArmorTypes(), []);
  const { data: armorClasses } = useAPI(() => getArmorClasses(), []);
  const { data: armorSlots } = useAPI(() => getArmorSlots(), []);

  const fetcher = useCallback(
    (page: number, pageSize: number) =>
      getArmor({ ...filters, search: debouncedSearch }, page, pageSize),
    [filters, debouncedSearch]
  );

  const {
    data: armor,
    total,
    page,
    pageSize,
    totalPages,
    loading,
    error,
    goToPage,
    changePageSize,
  } = usePaginatedAPI(fetcher, 20);

  const handleFilterChange = (key: keyof ArmorFilters, value: string) => {
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
        <h1 className="text-4xl font-bold text-cyan-400">Armor Database</h1>
        <p className="text-gray-400">Browse all {total} armor pieces in Fallout 76</p>
      </div>

      {/* Filters */}
      <Card className="bg-base-200">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          <SearchBar
            value={searchTerm}
            onChange={setSearchTerm}
            placeholder="Search armor..."
          />

          <Select
            value={filters.type || ''}
            onChange={(value) => handleFilterChange('type', value)}
            options={(armorTypes || []).map((type) => ({ value: type, label: type }))}
            placeholder="All Types"
            label="Type"
          />

          <Select
            value={filters.armor_class || ''}
            onChange={(value) => handleFilterChange('armor_class', value)}
            options={(armorClasses || []).map((cls) => ({ value: cls, label: cls }))}
            placeholder="All Classes"
            label="Class"
          />

          <Select
            value={filters.slot || ''}
            onChange={(value) => handleFilterChange('slot', value)}
            options={(armorSlots || []).map((slot) => ({ value: slot, label: slot }))}
            placeholder="All Slots"
            label="Slot"
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
        <Loading text="Loading armor..." />
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {armor.map((piece) => (
              <Card
                key={piece.armor_id}
                hoverable
                onClick={() => navigate(`/armor/${piece.armor_id}`)}
              >
                <h3 className="text-xl font-bold text-cyan-300">{piece.name}</h3>
                <div className="grid grid-cols-2 gap-2 mt-4 text-sm">
                  <div>
                    <span className="text-gray-400">Type:</span>
                    <span className="ml-2 text-gray-200">{piece.type}</span>
                  </div>
                  <div>
                    <span className="text-gray-400">Slot:</span>
                    <span className="ml-2 text-gray-200">{piece.slot}</span>
                  </div>
                  <div>
                    <span className="text-gray-400">DR:</span>
                    <span className="ml-2 text-green-400 font-bold">
                      {formatNumber(piece.damage_resistance, 0)}
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-400">ER:</span>
                    <span className="ml-2 text-blue-400 font-bold">
                      {formatNumber(piece.energy_resistance, 0)}
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-400">RR:</span>
                    <span className="ml-2 text-yellow-400 font-bold">
                      {formatNumber(piece.radiation_resistance, 0)}
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-400">Weight:</span>
                    <span className="ml-2 text-gray-200">{formatWeight(piece.weight)}</span>
                  </div>
                </div>
                <div className="mt-3">
                  <div className="badge badge-sm badge-outline">{piece.armor_class}</div>
                  {piece.set_name && (
                    <div className="badge badge-sm badge-outline ml-2">{piece.set_name}</div>
                  )}
                  <div className="badge badge-sm badge-outline ml-2">
                    Lvl {piece.level_requirement}
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
