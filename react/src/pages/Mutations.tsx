import { usePaginatedAPI } from '../hooks/useAPI';
import { getMutations } from '../utils/api';
import { Pagination, Loading, ErrorMessage, Card } from '../components/ui';

export function Mutations() {
  const { data: mutations, total, page, totalPages, loading, error, goToPage } =
    usePaginatedAPI((page, pageSize) => getMutations(page, pageSize), 20);

  if (error) {
    return <ErrorMessage message={error} fullScreen />;
  }

  return (
    <div className="space-y-6">
      <div className="text-center space-y-2">
        <h1 className="text-4xl font-bold text-green-400">Mutations Database</h1>
        <p className="text-gray-400">All {total} mutations in Fallout 76</p>
      </div>

      {loading ? (
        <Loading text="Loading mutations..." />
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {mutations.map((mutation) => (
              <Card key={mutation.mutation_id} className="bg-base-200">
                <h3 className="text-2xl font-bold text-green-300 mb-4">{mutation.name}</h3>

                <div className="space-y-4">
                  <div>
                    <h4 className="text-sm font-semibold text-green-400 uppercase mb-2">
                      Positive Effects
                    </h4>
                    <p className="text-sm text-gray-300">{mutation.positive_effects}</p>
                  </div>

                  <div>
                    <h4 className="text-sm font-semibold text-red-400 uppercase mb-2">
                      Negative Effects
                    </h4>
                    <p className="text-sm text-gray-300">{mutation.negative_effects}</p>
                  </div>

                  {mutation.suppression_perk && (
                    <div>
                      <h4 className="text-sm font-semibold text-purple-400 uppercase mb-2">
                        Suppression Perk
                      </h4>
                      <div className="badge badge-outline">{mutation.suppression_perk}</div>
                    </div>
                  )}
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
