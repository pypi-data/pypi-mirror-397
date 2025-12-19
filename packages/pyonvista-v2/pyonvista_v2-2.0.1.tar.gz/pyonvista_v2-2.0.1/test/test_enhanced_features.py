"""
Tests for pyOnvista v2.0 enhanced features.
Tests fundamental data extraction capabilities.
"""

import pytest
import asyncio
import aiohttp
from unittest.mock import Mock, patch, AsyncMock
import sys
import os

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from pyonvista.api import PyOnVista
from pyonvista.util import Instrument, Quote


class TestEnhancedSearch:
    """Test enhanced search capabilities."""
    
    @pytest.mark.asyncio
    async def test_search_with_filters(self):
        """Test search with instrument type and country filters."""
        with patch('aiohttp.ClientSession.get') as mock_get:
            # Mock successful search response
            mock_response = Mock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={
                'list': [
                    {
                        'name': 'Apple Inc.',
                        'isin': 'US0378331005',
                        'symbol': 'APC',
                        'instrumentType': 'STOCK'
                    }
                ]
            })
            mock_get.return_value.__aenter__.return_value = mock_response
            
            async with aiohttp.ClientSession() as session:
                api = PyOnVista()
                await api.install_client(session)
                
                results = await api.search_instrument(
                    "Apple", 
                    instrument_type="STOCK", 
                    country="US",
                    limit=5
                )
                
                assert len(results) >= 1
                assert results[0].name == 'Apple Inc.'
                assert results[0].isin == 'US0378331005'
    
    @pytest.mark.asyncio
    async def test_search_by_isin(self):
        """Test direct ISIN lookup."""
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = Mock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={
                'list': [
                    {
                        'name': 'Apple Inc.',
                        'isin': 'US0378331005',
                        'symbol': 'APC',
                        'instrumentType': 'STOCK'
                    }
                ]
            })
            mock_get.return_value.__aenter__.return_value = mock_response
            
            async with aiohttp.ClientSession() as session:
                api = PyOnVista()
                await api.install_client(session)
                
                result = await api.search_by_isin("US0378331005")
                
                assert result is not None
                assert result.name == 'Apple Inc.'
                assert result.isin == 'US0378331005'
    
    @pytest.mark.asyncio
    async def test_search_international_stocks(self):
        """Test international stock symbol search."""
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = Mock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={
                'list': [
                    {
                        'name': 'Apple Inc.',
                        'isin': 'US0378331005',
                        'symbol': 'APC',
                        'instrumentType': 'STOCK'
                    }
                ]
            })
            mock_get.return_value.__aenter__.return_value = mock_response
            
            async with aiohttp.ClientSession() as session:
                api = PyOnVista()
                await api.install_client(session)
                
                results = await api.search_international_stocks("AAPL")
                
                assert len(results) >= 1
                assert results[0].name == 'Apple Inc.'


class TestFundamentalDataExtraction:
    """Test fundamental data extraction from snapshot responses."""
    
    def create_mock_snapshot(self):
        """Create a mock OnVista snapshot response with comprehensive data."""
        return {
            'type': 'INSTRUMENT_SNAPSHOT',
            'instrument': {
                'name': 'SAP SE',
                'isin': 'DE0007164600',
                'symbol': 'SAP',
                'instrumentType': 'STOCK'
            },
            'quote': {
                'close': 233.35,
                'volume': 1000000,
                'timestamp': '2024-01-01T10:00:00Z'
            },
            'stocksFigure': {
                'kgv': 26.52,  # P/E ratio
                'kbv': 3.77,   # P/B ratio
                'eps': 4.46,
                'dividendYield': 1.58
            },
            'cnPerformance': {
                'performance1D': -3.57,
                'performance1W': 1.04,
                'performance1Y': 6.53,
                'volatility30D': 29.46
            },
            'stocksCnTechnical': {
                'movingAverage20D': 233.47,
                'movingAverage200D': 249.66,
                'rsi14D': 57.1
            },
            'company': {
                'sector': 'Software',
                'industry': 'Standardsoftware',
                'country': 'DE',
                'employees': 107415,
                'headquarters': 'Deutschland'
            },
            'sustainabilityData': {
                'esgScore': 0.6,
                'environmentalScore': 0.6,
                'socialScore': 0.7,
                'governanceScore': 0.5
            },
            'stocksDetails': {
                'marketCap': 270769500000,
                'bookValuePerShare': 61.94,
                'priceToSales': 4.2,
                'debtToEquity': 0.3,
                'returnOnEquity': 15.2,
                'returnOnAssets': 8.1,
                'beta': 1.1,
                'sharpeRatio': 0.8
            }
        }
    
    def test_financial_ratios_extraction(self):
        """Test extraction of financial ratios."""
        mock_snapshot = self.create_mock_snapshot()
        
        # Create instrument with mock data
        instrument = Instrument(
            name="SAP SE",
            isin="DE0007164600", 
            symbol="SAP",
            type="STOCK",
            quote=Quote(close=233.35, volume=1000000)
        )
        instrument._snapshot_json = mock_snapshot
        
        ratios = instrument.get_financial_ratios()
        
        assert ratios.pe_ratio == 26.52
        assert ratios.pb_ratio == 3.77
        assert ratios.eps == 4.46
        assert ratios.dividend_yield == 1.58
        assert ratios.market_cap == 270769500000
        assert ratios.book_value_per_share == 61.94
        assert ratios.price_to_sales == 4.2
        assert ratios.debt_to_equity == 0.3
        assert ratios.return_on_equity == 15.2
        assert ratios.return_on_assets == 8.1
    
    def test_performance_metrics_extraction(self):
        """Test extraction of performance metrics."""
        mock_snapshot = self.create_mock_snapshot()
        
        instrument = Instrument(
            name="SAP SE",
            isin="DE0007164600",
            symbol="SAP", 
            type="STOCK",
            quote=Quote(close=233.35, volume=1000000)
        )
        instrument._snapshot_json = mock_snapshot
        
        performance = instrument.get_performance_metrics()
        
        assert performance.performance_1d == -3.57
        assert performance.performance_1w == 1.04
        assert performance.performance_1y == 6.53
        assert performance.volatility_30d == 29.46
        assert performance.beta == 1.1
        assert performance.sharpe_ratio == 0.8
    
    def test_technical_indicators_extraction(self):
        """Test extraction of technical indicators."""
        mock_snapshot = self.create_mock_snapshot()
        
        instrument = Instrument(
            name="SAP SE",
            isin="DE0007164600",
            symbol="SAP",
            type="STOCK", 
            quote=Quote(close=233.35, volume=1000000)
        )
        instrument._snapshot_json = mock_snapshot
        
        technical = instrument.get_technical_indicators()
        
        assert technical.moving_avg_20d == 233.47
        assert technical.moving_avg_200d == 249.66
        assert technical.rsi_14d == 57.1
    
    def test_company_info_extraction(self):
        """Test extraction of company information."""
        mock_snapshot = self.create_mock_snapshot()
        
        instrument = Instrument(
            name="SAP SE",
            isin="DE0007164600",
            symbol="SAP",
            type="STOCK",
            quote=Quote(close=233.35, volume=1000000)
        )
        instrument._snapshot_json = mock_snapshot
        
        company = instrument.get_company_info()
        
        assert company.sector == 'Software'
        assert company.industry == 'Standardsoftware'
        assert company.country == 'DE'
        assert company.employees == 107415
        assert company.headquarters == 'Deutschland'
    
    def test_sustainability_data_extraction(self):
        """Test extraction of ESG/sustainability data."""
        mock_snapshot = self.create_mock_snapshot()
        
        instrument = Instrument(
            name="SAP SE",
            isin="DE0007164600",
            symbol="SAP",
            type="STOCK",
            quote=Quote(close=233.35, volume=1000000)
        )
        instrument._snapshot_json = mock_snapshot
        
        esg = instrument.get_sustainability_data()
        
        assert esg.esg_score == 0.6
        assert esg.environmental_score == 0.6
        assert esg.social_score == 0.7
        assert esg.governance_score == 0.5
    
    def test_missing_data_handling(self):
        """Test graceful handling of missing data."""
        # Create instrument with minimal snapshot data
        minimal_snapshot = {
            'instrument': {
                'name': 'Test Company',
                'isin': 'TEST123456789',
                'symbol': 'TEST'
            },
            'quote': {
                'close': 100.0,
                'volume': 1000
            }
        }
        
        instrument = Instrument(
            name="Test Company",
            isin="TEST123456789",
            symbol="TEST",
            type="STOCK",
            quote=Quote(close=100.0, volume=1000)
        )
        instrument._snapshot_json = minimal_snapshot
        
        # All extraction methods should return objects with None values
        ratios = instrument.get_financial_ratios()
        performance = instrument.get_performance_metrics()
        technical = instrument.get_technical_indicators()
        company = instrument.get_company_info()
        esg = instrument.get_sustainability_data()
        
        assert ratios.pe_ratio is None
        assert performance.performance_1y is None
        assert technical.moving_avg_20d is None
        assert company.sector is None
        assert esg.esg_score is None


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    @pytest.mark.asyncio
    async def test_invalid_search_parameters(self):
        """Test handling of invalid search parameters."""
        async with aiohttp.ClientSession() as session:
            api = PyOnVista()
            await api.install_client(session)
            
            # Empty search string should raise ValueError
            with pytest.raises(ValueError):
                await api.search_instrument("")
    
    @pytest.mark.asyncio
    async def test_invalid_isin_format(self):
        """Test handling of invalid ISIN format."""
        async with aiohttp.ClientSession() as session:
            api = PyOnVista()
            await api.install_client(session)
            
            # Invalid ISIN should raise ValueError
            with pytest.raises(ValueError):
                await api.search_by_isin("INVALID")
    
    @pytest.mark.asyncio
    async def test_network_error_handling(self):
        """Test handling of network errors."""
        with patch('aiohttp.ClientSession.get') as mock_get:
            # Mock network error
            mock_get.side_effect = aiohttp.ClientError("Network error")
            
            async with aiohttp.ClientSession() as session:
                api = PyOnVista()
                await api.install_client(session)
                
                with pytest.raises(aiohttp.ClientError):
                    await api.search_instrument("Apple")
    
    @pytest.mark.asyncio
    async def test_api_error_responses(self):
        """Test handling of API error responses."""
        with patch('aiohttp.ClientSession.get') as mock_get:
            # Mock API error response
            mock_response = Mock()
            mock_response.status = 404
            mock_response.raise_for_status.side_effect = aiohttp.ClientResponseError(
                request_info=Mock(), history=[]
            )
            mock_get.return_value.__aenter__.return_value = mock_response
            
            async with aiohttp.ClientSession() as session:
                api = PyOnVista()
                await api.install_client(session)
                
                with pytest.raises(aiohttp.ClientResponseError):
                    await api.search_instrument("NonExistent")


class TestDataConversion:
    """Test helper methods for safe data conversion."""
    
    def test_safe_float_conversion(self):
        """Test safe conversion to float."""
        from src.pyonvista.util import safe_float
        
        assert safe_float("123.45") == 123.45
        assert safe_float(123.45) == 123.45
        assert safe_float("invalid") is None
        assert safe_float(None) is None
        assert safe_float("") is None
    
    def test_safe_int_conversion(self):
        """Test safe conversion to int."""
        from src.pyonvista.util import safe_int
        
        assert safe_int("123") == 123
        assert safe_int(123) == 123
        assert safe_int("123.45") == 123
        assert safe_int("invalid") is None
        assert safe_int(None) is None
        assert safe_int("") is None


class TestBackwardCompatibility:
    """Test that v2.0 maintains backward compatibility with v1.0."""
    
    @pytest.mark.asyncio
    async def test_v1_search_still_works(self):
        """Test that v1.0 style search still works."""
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = Mock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={
                'list': [
                    {
                        'name': 'Apple Inc.',
                        'isin': 'US0378331005',
                        'symbol': 'APC',
                        'instrumentType': 'STOCK'
                    }
                ]
            })
            mock_get.return_value.__aenter__.return_value = mock_response
            
            async with aiohttp.ClientSession() as session:
                api = PyOnVista()
                await api.install_client(session)
                
                # v1.0 style call - should still work
                results = await api.search_instrument("Apple")
                
                assert len(results) >= 1
                assert results[0].name == 'Apple Inc.'
    
    @pytest.mark.asyncio
    async def test_v1_instrument_request_still_works(self):
        """Test that v1.0 style instrument requests still work."""
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = Mock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={
                'instrument': {
                    'name': 'Apple Inc.',
                    'isin': 'US0378331005',
                    'symbol': 'APC',
                    'instrumentType': 'STOCK'
                },
                'quote': {
                    'close': 150.0,
                    'volume': 1000000,
                    'timestamp': '2024-01-01T10:00:00Z'
                }
            })
            mock_get.return_value.__aenter__.return_value = mock_response
            
            async with aiohttp.ClientSession() as session:
                api = PyOnVista()
                await api.install_client(session)
                
                # v1.0 style call - should still work
                instrument = await api.request_instrument(isin="US0378331005")
                
                assert instrument.name == 'Apple Inc.'
                assert instrument.quote.close == 150.0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
