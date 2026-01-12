import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Dashboard from './Dashboard';

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <div className="min-h-screen bg-gray-50 text-gray-900">
        <header className="bg-white shadow-sm">
          <div className="max-w-7xl mx-auto py-4 px-4 sm:px-6 lg:px-8">
            <h1 className="text-2xl font-bold text-gray-900">
              🏀 PolySportsLab Whale Tracker
            </h1>
          </div>
        </header>
        <main>
          <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
            <Dashboard />
          </div>
        </main>
      </div>
    </QueryClientProvider>
  );
}

export default App;
