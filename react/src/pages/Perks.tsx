import { useState, useCallback } from 'react';
import { usePaginatedAPI, useDebounce } from '../hooks/useAPI';
import { getPerks, getLegendaryPerks, getSpecialList } from '../utils/api';
import { useAPI } from '../hooks/useAPI';
import { SearchBar, Select, Pagination, Loading, ErrorMessage, Card, Button } from '../components/ui';
import { getStatColor } from '../utils/format';
import type { PerkFilters } from '../types/api';

export function Perks() {
  const [viewMode, setViewMode] = useState<'regular' | 'legendary'>('regular');
  const [filters, setFilters] = useState<PerkFilters>({});
  const [searchTerm, setSearchTerm] = useState('');
  const debouncedSearch = useDebounce(searchTerm, 500);

  const { data: specialStats } = useAPI(() => getSpecialList(), []);

  const regularFetcher = useCallback(
    (page: number, pageSize: number) =>
      getPerks({ ...filters, search: debouncedSearch }, page, pageSize),
    [filters, debouncedSearch]
  );

  const legendaryFetcher = useCallback(
    (page: number, pageSize: number) => getLegendaryPerks(page, pageSize),
    []
  );

  const regularPerks = usePaginatedAPI(regularFetcher, 20);
  const legendaryPerks = usePaginatedAPI(legendaryFetcher, 20);

  const currentView = viewMode === 'regular' ? regularPerks : legendaryPerks;

  const handleFilterChange = (key: keyof PerkFilters, value: string) => {
    setFilters((prev) => ({
      ...prev,
      [key]: value || undefined,
    }));
  };

  if (currentView.error) {
    return <ErrorMessage message={currentView.error} fullScreen />;
  }

  return (
    <div className="space-y-6">
      <div className="text-center space-y-2">
        <h1 className="text-4xl font-bold text-purple-400">Perks Database</h1>
        <p className="text-gray-400">Browse all {currentView.total} {viewMode} perks</p>
      </div>

      {/* View Toggle */}
      <div className="flex justify-center">
        <div className="btn-group">
          <Button
            variant={viewMode === 'regular' ? 'primary' : 'outline'}
            onClick={() => setViewMode('regular')}
          >
            Regular Perks
          </Button>
          <Button
            variant={viewMode === 'legendary' ? 'primary' : 'outline'}
            onClick={() => setViewMode('legendary')}
          >
            Legendary Perks
          </Button>
        </div>
      </div>

      {/* Filters (only for regular perks) */}
      {viewMode === 'regular' && (
        <Card className="bg-base-200">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <SearchBar
              value={searchTerm}
              onChange={setSearchTerm}
              placeholder="Search perks..."
            />

            <Select
              value={filters.special_stat || ''}
              onChange={(value) => handleFilterChange('special_stat', value)}
              options={(specialStats || []).map((stat) => ({ value: stat, label: stat }))}
              placeholder="All SPECIAL Stats"
              label="SPECIAL"
            />

            <Select
              value={currentView.pageSize.toString()}
              onChange={(value) => currentView.changePageSize(Number(value))}
              options={[
                { value: '10', label: '10 per page' },
                { value: '20', label: '20 per page' },
                { value: '50', label: '50 per page' },
              ]}
              label="Per Page"
            />
          </div>
        </Card>
      )}

      {/* Results */}
      {currentView.loading ? (
        <Loading text={`Loading ${viewMode} perks...`} />
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {currentView.data.map((perk: any) => (
              <Card key={perk.perk_id || perk.legendary_perk_id} hoverable>
                <h3 className="text-xl font-bold text-purple-300">{perk.name}</h3>
                {perk.special_stat && (
                  <div className={`badge badge-lg mt-2 ${getStatColor(perk.special_stat)}`}>
                    {perk.special_stat}
                  </div>
                )}
                <p className="text-sm text-gray-300 mt-4">{perk.description}</p>
                <div className="mt-4 flex justify-between items-center">
                  <div>
                    <span className="text-gray-400 text-sm">Max Rank:</span>
                    <span className="ml-2 text-yellow-400 font-bold">{perk.max_rank}</span>
                  </div>
                  {perk.level_requirement && (
                    <div className="badge badge-sm badge-outline">
                      Lvl {perk.level_requirement}
                    </div>
                  )}
                </div>
              </Card>
            ))}
          </div>

          {/* Pagination */}
          {currentView.totalPages > 1 && (
            <div className="flex justify-center">
              <Pagination
                currentPage={currentView.page}
                totalPages={currentView.totalPages}
                onPageChange={currentView.goToPage}
              />
            </div>
          )}
        </>
      )}
    </div>
  );
}
