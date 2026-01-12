import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { format } from 'date-fns';
import { type Market, type MarketListItem } from './types';
import { Loader2, RefreshCw } from 'lucide-react';

export default function Dashboard() {
  const [selectedMarket, setSelectedMarket] = useState<string>('');

  // Fetch Markets List
  const { data: markets, isLoading: isLoadingMarkets } = useQuery<MarketListItem[]>({
    queryKey: ['markets'],
    queryFn: async () => {
      const res = await fetch('/api/markets');
      if (!res.ok) throw new Error('Failed to fetch markets');
      return res.json();
    },
  });

  // Fetch Latest Data (Overview)
  const { data: latestData, isLoading: isLoadingLatest, refetch: refetchLatest } = useQuery<Market[]>({
    queryKey: ['latest'],
    queryFn: async () => {
      const res = await fetch('/api/latest');
      if (!res.ok) throw new Error('Failed to fetch latest data');
      return res.json();
    },
  });

  // Fetch History for Selected Market
  const { data: historyData, isLoading: isLoadingHistory } = useQuery<Market[]>({
    queryKey: ['history', selectedMarket],
    queryFn: async () => {
      if (!selectedMarket) return [];
      const res = await fetch(`/api/history?marketId=${selectedMarket}`);
      if (!res.ok) throw new Error('Failed to fetch history');
      const data = await res.json();
      return data.map((item: any) => ({
        ...item,
        timestamp: new Date(item.timestamp).getTime(), // Convert for Recharts
      }));
    },
    enabled: !!selectedMarket,
  });

  // Set default market
  if (!selectedMarket && markets && markets.length > 0) {
    setSelectedMarket(markets[0].market_id);
  }

  const handleRefresh = () => {
    refetchLatest();
  };

  if (isLoadingMarkets || isLoadingLatest) {
    return (
      <div className="flex justify-center items-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
      </div>
    );
  }

  const totalVolume = latestData?.reduce((sum, m) => sum + (m.volume || 0), 0) || 0;
  const avgWhaleConc = latestData 
    ? latestData.reduce((sum, m) => sum + (m.whale_concentration || 0), 0) / latestData.length 
    : 0;

  return (
    <div className="space-y-6">
      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-6 rounded-lg shadow border border-gray-100">
          <h3 className="text-sm font-medium text-gray-500">Total Markets</h3>
          <p className="text-2xl font-bold text-gray-900">{latestData?.length || 0}</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow border border-gray-100">
          <h3 className="text-sm font-medium text-gray-500">Total Volume</h3>
          <p className="text-2xl font-bold text-blue-600">
            ${totalVolume.toLocaleString(undefined, { maximumFractionDigits: 0 })}
          </p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow border border-gray-100">
          <h3 className="text-sm font-medium text-gray-500">Avg Whale Conc.</h3>
          <p className="text-2xl font-bold text-purple-600">
            {avgWhaleConc.toFixed(2)}%
          </p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow border border-gray-100 flex items-center justify-between">
          <div>
            <h3 className="text-sm font-medium text-gray-500">Last Update</h3>
            <p className="text-sm font-medium text-gray-900">
              {latestData && latestData.length > 0 
                ? format(new Date(latestData[0].timestamp), 'MM-dd HH:mm') 
                : 'N/A'}
            </p>
          </div>
          <button 
            onClick={handleRefresh}
            className="p-2 rounded-full hover:bg-gray-100 text-gray-500"
          >
            <RefreshCw className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Sidebar / Market List */}
        <div className="lg:col-span-1 bg-white rounded-lg shadow border border-gray-100 p-4">
          <h2 className="text-lg font-bold mb-4">Markets</h2>
          <div className="space-y-2 max-h-[600px] overflow-y-auto">
            {markets?.map((market) => (
              <button
                key={market.market_id}
                onClick={() => setSelectedMarket(market.market_id)}
                className={`w-full text-left px-4 py-3 rounded-md transition-colors ${
                  selectedMarket === market.market_id
                    ? 'bg-blue-50 text-blue-700 border-blue-200 border'
                    : 'hover:bg-gray-50 text-gray-700 border border-transparent'
                }`}
              >
                <div className="font-medium truncate">{market.market_title}</div>
              </button>
            ))}
          </div>
        </div>

        {/* Charts Area */}
        <div className="lg:col-span-2 space-y-6">
          {isLoadingHistory ? (
            <div className="flex justify-center items-center h-64 bg-white rounded-lg shadow">
              <Loader2 className="w-8 h-8 animate-spin text-gray-400" />
            </div>
          ) : (
            <>
              {/* Volume & Liquidity Chart */}
              <div className="bg-white p-6 rounded-lg shadow border border-gray-100">
                <h3 className="text-lg font-bold mb-4">Volume & Liquidity Trend</h3>
                <div className="h-[300px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={historyData}>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} />
                      <XAxis 
                        dataKey="timestamp" 
                        tickFormatter={(ts) => format(ts, 'HH:mm')}
                        type="number"
                        domain={['auto', 'auto']}
                        scale="time"
                      />
                      <YAxis yAxisId="left" />
                      <YAxis yAxisId="right" orientation="right" />
                      <Tooltip 
                        labelFormatter={(ts) => format(ts, 'MM-dd HH:mm')}
                        formatter={(val: number | undefined) => val?.toLocaleString() ?? ''}
                      />
                      <Legend />
                      <Line 
                        yAxisId="left"
                        type="monotone" 
                        dataKey="volume" 
                        stroke="#2563eb" 
                        name="Volume ($)"
                        dot={false}
                      />
                      <Line 
                        yAxisId="right"
                        type="monotone" 
                        dataKey="liquidity" 
                        stroke="#16a34a" 
                        name="Liquidity ($)"
                        dot={false}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Whale Concentration Chart */}
              <div className="bg-white p-6 rounded-lg shadow border border-gray-100">
                <h3 className="text-lg font-bold mb-4">Whale Concentration (%)</h3>
                <div className="h-[300px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={historyData}>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} />
                      <XAxis 
                        dataKey="timestamp" 
                        tickFormatter={(ts) => format(ts, 'HH:mm')}
                        type="number"
                        domain={['auto', 'auto']}
                        scale="time"
                      />
                      <YAxis domain={[0, 100]} />
                      <Tooltip labelFormatter={(ts) => format(ts, 'MM-dd HH:mm')} />
                      <Legend />
                      <Line 
                        type="monotone" 
                        dataKey="whale_concentration" 
                        stroke="#9333ea" 
                        name="Whale Conc."
                        strokeWidth={2}
                        dot={false}
                      />
                      <Line 
                        type="monotone" 
                        dataKey="top10_concentration" 
                        stroke="#ea580c" 
                        name="Top 10 Conc."
                        strokeDasharray="5 5"
                        dot={false}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
