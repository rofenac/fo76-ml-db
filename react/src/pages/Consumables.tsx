import { usePaginatedAPI } from '../hooks/useAPI';
import { getConsumables } from '../utils/api';
import { Pagination, Loading, ErrorMessage, Card } from '../components/ui';
import { formatDuration, formatWeight, formatValue } from '../utils/format';

export function Consumables() {
  const { data: consumables, total, page, totalPages, loading, error, goToPage } =
    usePaginatedAPI((page, pageSize) => getConsumables(page, pageSize), 20);

  if (error) {
    return <ErrorMessage message={error} fullScreen />;
  }

  return (
    <div className="space-y-6">
      <div className="text-center space-y-2">
        <h1 className="text-4xl font-bold text-yellow-400">Consumables Database</h1>
        <p className="text-gray-400">All {total} build-relevant consumables</p>
      </div>

      {loading ? (
        <Loading text="Loading consumables..." />
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {consumables.map((consumable) => (
              <Card key={consumable.consumable_id} hoverable className="bg-base-200">
                <h3 className="text-xl font-bold text-yellow-300">{consumable.name}</h3>

                <div className="mt-2">
                  <div className="badge badge-accent">{consumable.category}</div>
                </div>

                <div className="mt-4">
                  <h4 className="text-sm font-semibold text-gray-400 uppercase mb-2">Effects</h4>
                  <p className="text-sm text-gray-300">{consumable.effects}</p>
                </div>

                <div className="grid grid-cols-2 gap-2 mt-4 text-sm">
                  <div>
                    <span className="text-gray-400">Duration:</span>
                    <span className="ml-2 text-gray-200">
                      {formatDuration(consumable.duration_minutes)}
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-400">Weight:</span>
                    <span className="ml-2 text-gray-200">{formatWeight(consumable.weight)}</span>
                  </div>
                  <div>
                    <span className="text-gray-400">Value:</span>
                    <span className="ml-2 text-gray-200">{formatValue(consumable.value)}</span>
                  </div>
                </div>
              </Card>
            ))}
          </div>

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
