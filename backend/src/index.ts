import { Hono } from 'hono';
import { cors } from 'hono/cors';

interface Env {
	DB: D1Database;
	AUTH_COOKIE: string;
}

interface Market {
	marketId: string;
	title: string;
	volume: number;
	liquidity: number;
	prices: { yes: number; no: number };
	conditionId: string;
}

interface WhaleAnalysis {
	success: boolean;
	data?: {
		whaleConcentration: number;
		smartMoneyDirection: string;
		top10Concentration: number;
	};
}

const app = new Hono<{ Bindings: Env }>();

app.use('/*', cors());

// --- Helper Functions ---

const BASE_URL = 'https://polysportslab.com';

async function fetchTopMarkets(authCookie: string, limit = 20): Promise<Market[]> {
	const url = `${BASE_URL}/api/polymarket?limit=${limit}`;
	const headers = {
		'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
		'Cookie': `auth_session_v2=${authCookie}`,
		'Accept-Encoding': 'gzip, deflate'
	};

	try {
		const response = await fetch(url, { headers });
		if (!response.ok) throw new Error(`API Error: ${response.status}`);
		return await response.json() as Market[];
	} catch (error) {
		console.error('Error fetching markets:', error);
		return [];
	}
}

async function fetchWhaleAnalysis(conditionId: string, authCookie: string): Promise<WhaleAnalysis | null> {
	const url = `${BASE_URL}/api/market-holders?conditionId=${conditionId}&limit=20`;
	const headers = {
		'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
		'Cookie': `auth_session_v2=${authCookie}`,
		'Accept-Encoding': 'gzip, deflate'
	};

	try {
		const response = await fetch(url, { headers });
		if (!response.ok) return null;
		return await response.json() as WhaleAnalysis;
	} catch (error) {
		console.error(`Error fetching whale analysis for ${conditionId}:`, error);
		return null;
	}
}

async function processAndStoreData(env: Env) {
	const authCookie = env.AUTH_COOKIE;
	if (!authCookie) {
		console.error('Missing AUTH_COOKIE secret');
		return;
	}

	const markets = await fetchTopMarkets(authCookie);
	console.log(`Fetched ${markets.length} markets`);

	const timestamp = new Date().toISOString();
	const stmt = env.DB.prepare(`
		INSERT INTO market_history (
			market_id, market_title, timestamp, volume, liquidity, 
			price_yes, price_no, whale_concentration, 
			smart_money_direction, top10_concentration
		) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
	`);

	const batch = [];

	for (const market of markets) {
		if (!market.conditionId) continue;
		
		// Add a small delay to be polite
		await new Promise(r => setTimeout(r, 100));
		
		const analysis = await fetchWhaleAnalysis(market.conditionId, authCookie);
		
		let whaleConc = null;
		let smartMoneyDir = null;
		let top10Conc = null;

		if (analysis && analysis.success && analysis.data) {
			whaleConc = analysis.data.whaleConcentration;
			smartMoneyDir = analysis.data.smartMoneyDirection;
			top10Conc = analysis.data.top10Concentration;
		}

		batch.push(stmt.bind(
			market.marketId,
			market.title,
			timestamp,
			market.volume,
			market.liquidity,
			market.prices.yes,
			market.prices.no,
			whaleConc,
			smartMoneyDir,
			top10Conc
		));
	}

	if (batch.length > 0) {
		await env.DB.batch(batch);
		console.log(`Saved ${batch.length} records to DB`);
	}
}

// --- API Endpoints ---

app.get('/', (c) => c.text('PolySportsLab Whale Tracker API'));

app.get('/api/markets', async (c) => {
	const limit = c.req.query('limit') || '20';
	const { results } = await c.env.DB.prepare(
		`SELECT DISTINCT market_id, market_title FROM market_history LIMIT ?`
	).bind(parseInt(limit)).all();
	return c.json(results);
});

app.get('/api/latest', async (c) => {
	// Get the latest timestamp first
	const latestTimeResult = await c.env.DB.prepare(
		`SELECT MAX(timestamp) as latest_ts FROM market_history`
	).first();
	
	const latestTs = latestTimeResult?.latest_ts;

	if (!latestTs) return c.json([]);

	const { results } = await c.env.DB.prepare(
		`SELECT * FROM market_history WHERE timestamp = ? ORDER BY volume DESC`
	).bind(latestTs).all();

	return c.json(results);
});

app.get('/api/history', async (c) => {
	const marketId = c.req.query('marketId');
	if (!marketId) return c.json({ error: 'Missing marketId' }, 400);

	const { results } = await c.env.DB.prepare(
		`SELECT * FROM market_history WHERE market_id = ? ORDER BY timestamp ASC`
	).bind(marketId).all();

	return c.json(results);
});

// Manual trigger for testing
app.post('/api/fetch', async (c) => {
	await processAndStoreData(c.env);
	return c.json({ status: 'Data fetch triggered' });
});

// --- Scheduled Task ---

export default {
	fetch: app.fetch,
	async scheduled(event: ScheduledEvent, env: Env, ctx: ExecutionContext) {
		ctx.waitUntil(processAndStoreData(env));
	},
};
