# pyOnvista v2.0

> **Acknowledgment**: This project builds upon the excellent foundation of the original [pyOnvista](https://github.com/cloasdata/pyOnvista) by [cloasdata](https://github.com/cloasdata). The v2.0 enhancements add comprehensive fundamental data extraction capabilities while maintaining full backward compatibility with the original API.

A Python library for accessing financial data from onvista.de

**NEW in v2.0: Comprehensive fundamental data extraction**

## Features

- Real-time stock quotes and historical data
- Enhanced search with international stock support 
- Direct ISIN lookup
- **NEW**: Financial ratios (P/E, P/B, EPS, dividend yield, market cap)
- **NEW**: Performance metrics (returns, volatility, technical indicators)
- **NEW**: Company information (sector, industry, employees)
- **NEW**: ESG/sustainability data

## Installation

```bash
pip install pyonvista-v2
```

> **Package Name**: This enhanced v2.0 fork is published as `pyonvista-v2` on PyPI to avoid conflicts with the original package. The import statements remain the same (`from pyonvista.api import PyOnVista`).

## Quick Start

### Basic Usage

```python
import asyncio
import aiohttp
from pyonvista.api import PyOnVista

async def example():
    async with aiohttp.ClientSession() as session:
        api = PyOnVista()
        await api.install_client(session)
        
        # Search for instruments
        results = await api.search_instrument("Apple")
        
        # Get detailed data
        instrument = await api.request_instrument(isin="US0378331005")
        print(f"{instrument.name}: €{instrument.quote.close:.2f}")

asyncio.run(example())
```

### v2.0 Fundamental Data

```python
async def fundamental_data():
    async with aiohttp.ClientSession() as session:
        api = PyOnVista()
        await api.install_client(session)
        
        instrument = await api.request_instrument(isin="DE0007164600")  # SAP
        
        # Financial ratios
        ratios = instrument.get_financial_ratios()
        print(f"P/E Ratio: {ratios.pe_ratio:.2f}")
        print(f"Market Cap: €{ratios.market_cap:,.0f}")
        
        # Performance metrics
        performance = instrument.get_performance_metrics()
        print(f"1-Year Return: {performance.performance_1y:+.2f}%")
        
        # Company info
        company = instrument.get_company_info()
        print(f"Sector: {company.sector}")
        print(f"Employees: {company.employees:,}")

asyncio.run(fundamental_data())
```

### Enhanced Search

```python
async def enhanced_search():
    async with aiohttp.ClientSession() as session:
        api = PyOnVista()
        await api.install_client(session)
        
        # International symbol search
        apple_stocks = await api.search_international_stocks("AAPL")
        
        # Search with filters
        us_stocks = await api.search_instrument("Microsoft", 
                                              country="US", 
                                              instrument_type="STOCK")
        
        # Direct ISIN lookup
        apple = await api.search_by_isin("US0378331005")

asyncio.run(enhanced_search())
```

## v2.0 Data Classes

### FinancialRatios
Financial metrics: `pe_ratio`, `pb_ratio`, `eps`, `dividend_yield`, `market_cap`, `return_on_equity`, `debt_to_equity`

### PerformanceMetrics  
Performance data: `performance_1d`, `performance_1w`, `performance_1y`, `volatility_30d`, `beta`

### TechnicalIndicators
Technical analysis: `moving_avg_20d`, `moving_avg_200d`, `rsi_14d`, `bollinger_upper`, `bollinger_lower`

### CompanyInfo
Company data: `sector`, `industry`, `country`, `employees`, `headquarters`

### SustainabilityData
ESG metrics: `esg_score`, `environmental_score`, `social_score`, `governance_score`

## Migration from v1.0

v2.0 is fully backward compatible. All existing v1.0 code continues to work unchanged.

New capabilities are accessed through additional methods on `Instrument` objects:
- `instrument.get_financial_ratios()`
- `instrument.get_performance_metrics()`
- `instrument.get_technical_indicators()`
- `instrument.get_company_info()`
- `instrument.get_sustainability_data()`

## Rate Limiting

Built-in rate limiting with configurable delays:

```python
api = PyOnVista(request_delay=0.2, timeout=60)
```

## PyPI Package

This enhanced v2.0 fork is available on PyPI as **[pyonvista-v2](https://pypi.org/project/pyonvista-v2/)**:

- **Package Name**: `pyonvista-v2`
- **Current Version**: 2.0.0
- **Installation**: `pip install pyonvista-v2`
- **Import**: `from pyonvista.api import PyOnVista` (unchanged from v1.0)

The package includes both source distribution and universal wheel for easy installation across Python 3.8+ environments.

## License

MIT License - see [LICENSE.md](LICENSE.md) for details.

## Acknowledgments

- Original pyOnvista by [cloasdata](https://github.com/cloasdata)
