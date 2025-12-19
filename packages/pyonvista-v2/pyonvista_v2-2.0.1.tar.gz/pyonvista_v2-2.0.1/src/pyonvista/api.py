"""
A comprehensive API for onvista.de financial website.

The API provides extensive financial data including:
- Quote and chart data
- Enhanced search capabilities with international stock support
- Advanced filtering and error handling
"""
import asyncio
import inspect
import weakref
import dataclasses
import datetime
import json as jsonlib
import logging
from typing import (
    Literal,
    Any,
    Optional,
    Union,
    Dict,
    List
)
from types import SimpleNamespace

import aiohttp
from .util import make_url

# Configure logging
logger = logging.getLogger(__name__)

ONVISTA_BASE = "https://www.onvista.de"
ONVISTA_API_BASE = "https://api.onvista.de/api/v1"

snapshot_map = {
    "FUND": "funds",
    "STOCK": "stocks",
}


# Financial Data Classes for pyOnvista v2.0
@dataclasses.dataclass
class FinancialRatios:
    """Financial ratios and key metrics extracted from OnVista snapshot data."""
    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    eps: Optional[float] = None
    dividend_yield: Optional[float] = None
    market_cap: Optional[float] = None
    book_value_per_share: Optional[float] = None
    price_to_sales: Optional[float] = None
    debt_to_equity: Optional[float] = None
    return_on_equity: Optional[float] = None
    return_on_assets: Optional[float] = None


@dataclasses.dataclass
class PerformanceMetrics:
    """Performance and volatility metrics from OnVista snapshot data."""
    performance_1d: Optional[float] = None
    performance_1w: Optional[float] = None
    performance_1m: Optional[float] = None
    performance_3m: Optional[float] = None
    performance_1y: Optional[float] = None
    performance_3y: Optional[float] = None
    volatility_30d: Optional[float] = None
    volatility_250d: Optional[float] = None
    beta: Optional[float] = None
    sharpe_ratio: Optional[float] = None


@dataclasses.dataclass
class TechnicalIndicators:
    """Technical indicators from OnVista snapshot data."""
    moving_avg_5d: Optional[float] = None
    moving_avg_20d: Optional[float] = None
    moving_avg_30d: Optional[float] = None
    moving_avg_100d: Optional[float] = None
    moving_avg_200d: Optional[float] = None
    rsi_14d: Optional[float] = None
    bollinger_upper: Optional[float] = None
    bollinger_lower: Optional[float] = None
    support_level: Optional[float] = None
    resistance_level: Optional[float] = None


@dataclasses.dataclass
class CompanyInfo:
    """Company and sector information from OnVista snapshot data."""
    sector: Optional[str] = None
    industry: Optional[str] = None
    country: Optional[str] = None
    employees: Optional[int] = None
    founded: Optional[str] = None
    headquarters: Optional[str] = None
    website: Optional[str] = None
    business_description: Optional[str] = None
    ceo: Optional[str] = None
    market_segment: Optional[str] = None


@dataclasses.dataclass
class SustainabilityData:
    """ESG and sustainability metrics from OnVista snapshot data."""
    esg_score: Optional[float] = None
    environmental_score: Optional[float] = None
    social_score: Optional[float] = None
    governance_score: Optional[float] = None
    sustainability_rating: Optional[str] = None
    carbon_footprint: Optional[float] = None
    water_usage: Optional[float] = None
    waste_production: Optional[float] = None
    renewable_energy_usage: Optional[float] = None
    sustainability_rank: Optional[int] = None


@dataclasses.dataclass
class Quote:
    resolution: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    pieces: int
    instrument: "Instrument"

    @classmethod
    def from_dict(cls, instrument: "Instrument", quote:dict) -> "Quote":
        try:
            volume = int(quote["money"])
        except KeyError:
            # not stonks
            volume = int(quote["totalMoney"])
        try:
            pieces = int(quote["volume"])
        except KeyError:
            # not stonks
            pieces = int(quote['volumeBid'])

        quote= cls(
            resolution="1m",
            timestamp=datetime.datetime.strptime(quote["datetimeLast"].split(".")[0], "%Y-%m-%dT%H:%M:%S"),
            open=float(quote["open"]),
            high=float(quote["high"]),
            low=float(quote["low"]),
            close=float(quote["last"]),  # not sure if this true
            volume=volume,
            pieces=pieces,
            instrument=instrument
        )
        return quote


@dataclasses.dataclass
class Market:
    """Maps ID,market,exchange whereas exchange is acronym/key for market"""
    name: str
    code: str


@dataclasses.dataclass
class Notation:
    market: Market
    id: str
    currency: str = None


@dataclasses.dataclass
class Instrument:
    """
    A minimal dataclass representing data from the onvista api to later request quotes
    Enhanced in v2.0 with fundamental data extraction capabilities.
    """
    uid: str = ""
    name: str = ""
    symbol: str = ""
    isin: str = ""
    url: str = ""
    type: str = ""
    quote: Optional[Quote] = dataclasses.field(repr=False, default=None)
    _snapshot_json: dict = dataclasses.field(repr=False, default_factory=dict)
    snapshot_valid_until: datetime.datetime = dataclasses.field(default_factory=datetime.datetime.now, repr=False)
    notations: List[Notation] = dataclasses.field(default_factory=list)
    last_change: datetime.datetime = dataclasses.field(default_factory=datetime.datetime.now, repr=False)

    @property
    def dict(self) -> dict:
        return self._snapshot_json

    @property
    def as_tree(self) -> SimpleNamespace:
        """
        Provides a simple object tree of json for easy browsing
        """
        return jsonlib.loads(jsonlib.dumps(self._snapshot_json), object_hook=lambda d: SimpleNamespace(**d))

    @classmethod
    def from_json(cls, data: dict) -> "Instrument":
        """
        Alternate constructor to parse data to a fresh instrument instance.
        :param data: a json dict from a web response
        :return: Instrument
        """
        instrument = cls()
        instrument.notations = []
        _update_instrument(instrument, data)
        return instrument

    @classmethod
    def from_isin(cls, isin:str) -> "Instrument":
        # todo: implement
        raise NotImplementedError("Constructor not implemented yet")

    # PyOnvista v2.0 - Financial Data Extraction Methods
    def get_financial_ratios(self) -> FinancialRatios:
        """
        Extract financial ratios from snapshot data.
        
        Returns:
            FinancialRatios object with available financial metrics
        """
        if not self._snapshot_json:
            return FinancialRatios()
        
        data = self._snapshot_json
        ratios = FinancialRatios()
        
        try:
            # Extract market cap from stocksFigure section
            if 'stocksFigure' in data:
                figure_data = data['stocksFigure']
                ratios.market_cap = self._safe_float(figure_data.get('marketCapInstrument'))
            
            # Extract financial ratios from stocksCnFundamentalList
            if 'stocksCnFundamentalList' in data and 'list' in data['stocksCnFundamentalList']:
                fund_list = data['stocksCnFundamentalList']['list']
                # Use most recent year data (first item is usually most recent)
                if fund_list:
                    recent_data = fund_list[0]  # Most recent year
                    ratios.pe_ratio = self._safe_float(recent_data.get('cnPer'))
                    ratios.pb_ratio = self._safe_float(recent_data.get('cnPriceBookvalue'))
                    ratios.eps = self._safe_float(recent_data.get('cnEpsAdj'))
                    ratios.dividend_yield = self._safe_float(recent_data.get('cnDivYield'))
            
            # Extract from stocksCnFinancialList
            if 'stocksCnFinancialList' in data and 'list' in data['stocksCnFinancialList']:
                fin_list = data['stocksCnFinancialList']['list']
                if fin_list:
                    recent_data = fin_list[0]  # Most recent year
                    if not ratios.return_on_equity:
                        ratios.return_on_equity = self._safe_float(recent_data.get('cnReturnEquity'))
                    if not ratios.debt_to_equity:
                        ratios.debt_to_equity = self._safe_float(recent_data.get('cnDebtEquity'))
            
            # Extract from stocksBalanceSheetList for additional metrics
            if 'stocksBalanceSheetList' in data and 'list' in data['stocksBalanceSheetList']:
                balance_list = data['stocksBalanceSheetList']['list']
                if balance_list:
                    recent_data = balance_list[0]  # Most recent year
                    if not ratios.eps:
                        ratios.eps = self._safe_float(recent_data.get('eps'))
                        
        except Exception as e:
            logger.debug(f"Error extracting financial ratios: {str(e)}")
            
        return ratios

    def get_performance_metrics(self) -> PerformanceMetrics:
        """
        Extract performance metrics from snapshot data.
        
        Returns:
            PerformanceMetrics object with available performance data
        """
        if not self._snapshot_json:
            return PerformanceMetrics()
            
        data = self._snapshot_json
        metrics = PerformanceMetrics()
        
        try:
            # Extract from cnPerformance section
            if 'cnPerformance' in data:
                perf_data = data['cnPerformance']
                metrics.performance_1d = self._safe_float(perf_data.get('performanceRelD1'))
                metrics.performance_1w = self._safe_float(perf_data.get('performanceRelW1'))
                metrics.performance_1m = self._safe_float(perf_data.get('performanceRelM1'))
                metrics.performance_3m = self._safe_float(perf_data.get('performanceRelM3'))
                metrics.performance_1y = self._safe_float(perf_data.get('performanceRelW52'))
                metrics.performance_3y = self._safe_float(perf_data.get('performanceRelY3'))
                
                # Volatility data
                metrics.volatility_30d = self._safe_float(perf_data.get('vola30'))
                metrics.volatility_250d = self._safe_float(perf_data.get('vola250'))
            
            # Extract basic performance from quote section
            if 'quote' in data:
                quote_data = data['quote']
                if not metrics.performance_1d:
                    metrics.performance_1d = self._safe_float(quote_data.get('performancePct'))
                if not metrics.performance_1y:
                    metrics.performance_1y = self._safe_float(quote_data.get('performance1YearPct'))
                    
        except Exception as e:
            logger.debug(f"Error extracting performance metrics: {str(e)}")
            
        return metrics

    def get_technical_indicators(self) -> TechnicalIndicators:
        """
        Extract technical indicators from snapshot data.
        
        Returns:
            TechnicalIndicators object with available technical data
        """
        if not self._snapshot_json:
            return TechnicalIndicators()
            
        data = self._snapshot_json
        indicators = TechnicalIndicators()
        
        try:
            # Extract from stocksCnTechnical section
            if 'stocksCnTechnical' in data:
                tech_data = data['stocksCnTechnical']
                indicators.moving_avg_5d = self._safe_float(tech_data.get('movingAverage5'))
                indicators.moving_avg_20d = self._safe_float(tech_data.get('movingAverage20'))
                indicators.moving_avg_30d = self._safe_float(tech_data.get('movingAverage30'))
                indicators.moving_avg_100d = self._safe_float(tech_data.get('movingAverage100'))
                indicators.moving_avg_200d = self._safe_float(tech_data.get('movingAverage200'))
                
                # RSI (Relative Strength Index)
                indicators.rsi_14d = self._safe_float(tech_data.get('relativeStrengthIndexWilder20'))
                
                # Other technical indicators from the API
                # Note: API uses different field names than traditional technical analysis
                # momentum and relative strength can be used as approximations
                        
        except Exception as e:
            logger.debug(f"Error extracting technical indicators: {str(e)}")
            
        return indicators

    def get_company_info(self) -> CompanyInfo:
        """
        Extract company information from snapshot data.
        
        Returns:
            CompanyInfo object with available company data
        """
        if not self._snapshot_json:
            return CompanyInfo()
            
        data = self._snapshot_json
        info = CompanyInfo()
        
        try:
            # Extract from company section
            if 'company' in data:
                comp_data = data['company']
                info.country = comp_data.get('isoCountry')
                info.headquarters = comp_data.get('nameCountry')
                
                # Extract sector/industry from branch
                if 'branch' in comp_data:
                    branch_data = comp_data['branch']
                    info.industry = branch_data.get('name')
                    if 'sector' in branch_data:
                        info.sector = branch_data['sector'].get('name')
            
            # Extract employee count from balance sheet
            if 'stocksBalanceSheetList' in data and 'list' in data['stocksBalanceSheetList']:
                balance_list = data['stocksBalanceSheetList']['list']
                if balance_list:
                    recent_data = balance_list[0]  # Most recent year
                    info.employees = self._safe_int(recent_data.get('employees'))
                    
        except Exception as e:
            logger.debug(f"Error extracting company info: {str(e)}")
            
        return info

    def get_sustainability_data(self) -> SustainabilityData:
        """
        Extract sustainability/ESG data from snapshot data.
        
        Returns:
            SustainabilityData object with available ESG metrics
        """
        if not self._snapshot_json:
            return SustainabilityData()
            
        data = self._snapshot_json
        sustainability = SustainabilityData()
        
        try:
            # Extract from sustainabilityData section
            if 'sustainabilityData' in data:
                sust_data = data['sustainabilityData']
                sustainability.esg_score = self._safe_float(sust_data.get('totalScore'))
                
                # Climate group data
                if 'climateGroup' in sust_data:
                    climate_data = sust_data['climateGroup']
                    sustainability.environmental_score = self._safe_float(climate_data.get('climateScore'))
                    sustainability.renewable_energy_usage = self._safe_float(climate_data.get('renewableEnergyValue'))
                
                # Society group data
                if 'societyGroup' in sust_data:
                    society_data = sust_data['societyGroup']
                    sustainability.social_score = self._safe_float(society_data.get('societyScore'))
                
                # Gender group data
                if 'genderGroup' in sust_data:
                    gender_data = sust_data['genderGroup']
                    sustainability.governance_score = self._safe_float(gender_data.get('genderScore'))
                    
        except Exception as e:
            logger.debug(f"Error extracting sustainability data: {str(e)}")
            
        return sustainability

    def _safe_float(self, value) -> Optional[float]:
        """Safely convert value to float, return None if not possible."""
        if value is None or value == '':
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
    
    def _safe_int(self, value) -> Optional[int]:
        """Safely convert value to int, return None if not possible."""
        if value is None or value == '':
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None


def _update_instrument(instrument: Instrument, data: dict, quote: dict = None, full_snapshot: dict = None):
    """
    Updates instrument from a json data dict
    :param instrument: Instrument to update
    :param data: instrument data dict
    :param quote: quote data dict
    :param full_snapshot: complete snapshot response for v2.0 fundamental data extraction
    :return: updated instrument
    """
    if data.get("expires", None):
        instrument.snapshot_valid_until = datetime.datetime.fromtimestamp(
            float(data["expires"]))
    instrument.last_change = datetime.datetime.now()
    instrument.uid = data["entityValue"]
    instrument.name = data["name"]
    instrument.isin = data.get("isin", None)
    instrument.symbol = data.get("symbol", None)
    instrument.url = data["urls"]["WEBSITE"]
    instrument.type = data["entityType"]
    
    # Store full snapshot data for v2.0 fundamental data extraction
    if full_snapshot:
        instrument._snapshot_json = full_snapshot
    
    if quote:
        instrument.quote = Quote.from_dict(instrument, quote)
    return instrument


def _add_notation(instrument: Instrument, notations: dict):
    """
    Ads notation to provided instrument
    :param instrument:
    :param notations:
    :return:
    """
    for notation in notations:
        market = Market(name=notation["market"]["name"], code=notation["market"]["codeExchange"])
        currency = notation.get("isoCurrency")
        notation = Notation(market=market, id=notation["market"]["idNotation"], currency=currency)
        instrument.notations.append(notation)


class PyOnVista:
    def __init__(self, request_delay: float = 0.1, timeout: int = 30):
        """
        Initialize PyOnvista API client.
        
        Args:
            request_delay: Delay between requests to avoid rate limiting (default: 0.1s)
            timeout: Request timeout in seconds (default: 30s)
        """
        self._client: Optional[aiohttp.ClientSession] = None
        self._loop: Optional[asyncio.BaseEventLoop] = None
        self._instruments = weakref.WeakSet()
        self._request_delay = request_delay
        self._timeout = timeout
        self._last_request_time = 0.0

    async def install_client(self, client: Any):
        """
        This function installs the client to the pyonvista api.
        It should be called in front of any other calls to this api.
        A client must implement at least a get method and should be configured
        to follow redirects. Otherwise, you'll be warned.

        If you run an async client this function will check for a running loop. An keeps a weakref to it.
        :param client:
        :return:
        """
        if not getattr(client, "get"):
            raise AttributeError(f"Provided client {client} does not implement a get method.")

        self._client = client

        if inspect.ismethod(getattr(client, "get")):
            self._loop = weakref.ref(asyncio.get_event_loop())
        else:
            raise AttributeError(f"The provided client {client} seems not have an async get method")

    async def _get_json(self, url: str, *args, **kwargs) -> Optional[Dict]:
        """
        Enhanced JSON fetcher with rate limiting and error handling.
        
        Args:
            url: URL to fetch
            *args: Additional arguments for aiohttp
            **kwargs: Additional keyword arguments for aiohttp
            
        Returns:
            Dict containing JSON response or None if failed
        """
        # Rate limiting
        current_time = datetime.datetime.now().timestamp()
        time_since_last = current_time - self._last_request_time
        if time_since_last < self._request_delay:
            await asyncio.sleep(self._request_delay - time_since_last)
        
        self._last_request_time = datetime.datetime.now().timestamp()
        
        try:
            timeout = aiohttp.ClientTimeout(total=self._timeout)
            async with self._client.get(url, timeout=timeout, *args, **kwargs) as response:
                if response.status == 200:
                    return dict(await response.json())
                elif response.status == 429:  # Rate limited
                    logger.warning(f"Rate limited, waiting longer for URL: {url}")
                    await asyncio.sleep(1.0)
                    return await self._get_json(url, *args, **kwargs)  # Retry once
                else:
                    logger.warning(f"HTTP {response.status} for URL: {url}")
                    return None
        except asyncio.TimeoutError:
            logger.error(f"Timeout for URL: {url}")
            return None
        except Exception as e:
            logger.error(f"Error fetching {url}: {str(e)}")
            return None

    async def search_instrument(self, key: str, instrument_type: Optional[str] = None, 
                              country: Optional[str] = None, limit: int = 50) -> List[Instrument]:
        """
        Enhanced search with support for international stocks.
        
        Args:
            key: Search term (company name, ISIN, WKN, symbol)
            instrument_type: Filter by type ('STOCK', 'FUND', 'BOND', 'INDEX', etc.)
            country: Filter by country code ('DE', 'US', 'GB', 'FR', etc.)
            limit: Maximum number of results (default 50, max 100)
            
        Returns:
            List of matching instruments
        """
        if not key or not key.strip():
            raise ValueError("Search key cannot be empty")
        
        limit = min(max(1, limit), 500)  # Get more results to filter from
        
        params = {
            "perType": 100,  # Get maximum from API
            "searchValue": key.strip()
        }
            
        url = make_url(ONVISTA_API_BASE, *["instruments", "search", "facet"], **params)
        json_data = await self._get_json(url)
        
        if not json_data or "facets" not in json_data:
            return []
            
        results = []
        for facet in json_data["facets"]:
            if facet_results := facet.get("results"):
                try:
                    results.extend([Instrument.from_json(data) for data in facet_results])
                except Exception as e:
                    logger.warning(f"Error parsing instrument data: {str(e)}")
                    continue
        
        # Apply client-side filters
        filtered_results = results
        
        if instrument_type:
            instrument_type = instrument_type.upper()
            filtered_results = [r for r in filtered_results if r.type == instrument_type]
        
        if country:
            country = country.upper()
            # Filter by ISIN country code (first 2 characters)
            filtered_results = [r for r in filtered_results 
                              if r.isin and r.isin[:2] == country]
        
        # Apply limit
        return filtered_results[:limit]

    async def search_by_isin(self, isin: str) -> Optional[Instrument]:
        """
        Direct search by ISIN for international stocks.
        
        Args:
            isin: International Securities Identification Number
            
        Returns:
            Instrument if found, None otherwise
        """
        if not isin or len(isin.strip()) != 12:
            raise ValueError("ISIN must be exactly 12 characters")
        
        try:
            return await self.request_instrument(isin=isin.strip().upper())
        except Exception as e:
            logger.debug(f"ISIN search failed for {isin}: {str(e)}")
            return None

    async def search_international_stocks(self, symbol: str, country: Optional[str] = None, limit: int = 50) -> List[Instrument]:
        """
        Search for international stocks by symbol.
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL', 'TSLA', 'SAP')
            country: Country code ('DE', 'US', 'GB', 'FR', etc.)
            limit: Maximum number of results (default 50)
            
        Returns:
            List of matching stock instruments
        """
        if not symbol or not symbol.strip():
            raise ValueError("Symbol cannot be empty")
        
        search_terms = [symbol.strip()]
        
        # Add country-specific searches if provided
        if country:
            search_terms.append(f"{symbol}.{country}")
            
        results = []
        for term in search_terms:
            try:
                instruments = await self.search_instrument(term, instrument_type="STOCK", country=country)
                results.extend(instruments)
            except Exception as e:
                logger.debug(f"Search failed for term {term}: {str(e)}")
                continue
                
        # Remove duplicates based on ISIN
        seen_isins = set()
        unique_results = []
        for instrument in results:
            if instrument.isin and instrument.isin not in seen_isins:
                seen_isins.add(instrument.isin)
                unique_results.append(instrument)
                
        return unique_results

    async def request_instrument(self, instrument: Instrument = None, isin: str = None) -> Instrument:
        """
        If instrument is provided, the instrument is updated.
        If a isin is provided a new instrument is provided.
        Enhanced in v2.0 to store full snapshot data for fundamental analysis.
        
        :param instrument: Existing instrument to update
        :param isin: ISIN to fetch instrument data for
        :return: Updated or new instrument with full snapshot data
        """
        isin = isin or (instrument.isin if instrument else None)
        if not isin:
            raise AttributeError("At least one argument must be provided")
        if not instrument:
            instrument = Instrument()
            instrument.isin = isin

        # Map instrument type for API endpoint
        type_ = snapshot_map.get(getattr(instrument, 'type', None), 'stocks')
        
        url = make_url(
            ONVISTA_API_BASE,
            type_,
            f"ISIN:{isin}",
            "snapshot"
        )
        
        data = await self._get_json(url)
        if not data:
            raise ValueError(f"No data found for ISIN: {isin}")
            
        # Update instrument with full snapshot data for v2.0 features
        _update_instrument(
            instrument, 
            data["instrument"], 
            data.get("quote"), 
            full_snapshot=data  # Store complete snapshot for fundamental data extraction
        )
        
        # Add market notations
        if "quoteList" in data and "list" in data["quoteList"]:
            _add_notation(instrument, notations=data["quoteList"]["list"])
            
        return instrument

    async def request_quotes(
            self,
            instrument: Instrument,
            start: datetime.datetime = None,
            end: datetime.datetime = None,
            resolution: Literal["1m", "15m", "1D"] = "15m",
            notation: Notation = None,

    ) -> list[Quote]:
        """
        Gets historic quotes form on vista api.
        """
        try:
            notation = notation or instrument.notations[0]
        except IndexError:
            instrument = await self.request_instrument(instrument)
            notation = instrument.notations[0]

        start = start or datetime.datetime.now() - datetime.timedelta(days=7)
        end = end or datetime.datetime.now()+datetime.timedelta(days=1)
        request_data = make_url(
            ONVISTA_API_BASE,
            "instruments",
            str(instrument.type),
            str(instrument.uid),
            "chart_history",
            endDate=end.strftime("%Y-%m-%d"),
            idNotation=notation.id,
            resolution=resolution,
            startDate=start.strftime("%Y-%m-%d"),
        )

        data = await self._get_json(request_data)

        result = []
        if data:
            quotes = zip(
                data["datetimeLast"],
                data["first"],
                data["last"],
                data["high"],
                data["low"],
                data["volume"],
                data["numberPrices"]
            )
            for date, first, last, high, low, volume, pieces in quotes:
                result.append(
                    Quote(resolution, datetime.datetime.fromtimestamp(date), first, high, low, last, volume,
                          pieces, instrument)
                )

        return result
