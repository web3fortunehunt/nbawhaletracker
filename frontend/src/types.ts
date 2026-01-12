export interface Market {
  market_id: string;
  market_title: string;
  timestamp: string;
  volume: number;
  liquidity: number;
  price_yes: number;
  price_no: number;
  whale_concentration: number | null;
  smart_money_direction: string | null;
  top10_concentration: number | null;
}

export interface MarketListItem {
  market_id: string;
  market_title: string;
}
