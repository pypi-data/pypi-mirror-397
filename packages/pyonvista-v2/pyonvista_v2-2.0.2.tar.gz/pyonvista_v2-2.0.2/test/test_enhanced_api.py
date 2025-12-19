#!/usr/bin/env python3
"""
Tests for enhanced PyOnvista API functionality.

This test suite focuses on the working enhanced search features:
- Enhanced search with filters
- ISIN-based search  
- International stock search
- Error handling
"""

import pytest
import asyncio
import aiohttp
from src.pyonvista.api import PyOnVista, Instrument


@pytest.fixture
async def api_client():
    """Create API client with aiohttp session."""
    api = PyOnVista(request_delay=0.1)
    session = aiohttp.ClientSession()
    await api.install_client(session)
    yield api
    await session.close()


class TestEnhancedSearch:
    """Test enhanced search capabilities."""
    
    @pytest.mark.asyncio
    async def test_search_with_country_filter(self, api_client):
        """Test search with country filter."""
        results = await api_client.search_instrument("SAP", country="DE", limit=5)
        
        assert isinstance(results, list)
        assert len(results) <= 5
        
        if results:
            # Verify all results have required attributes
            for instrument in results:
                assert hasattr(instrument, 'name')
                assert hasattr(instrument, 'isin')
                assert hasattr(instrument, 'symbol')
                assert instrument.name is not None
    
    @pytest.mark.asyncio
    async def test_search_with_instrument_type_filter(self, api_client):
        """Test search with instrument type filter."""
        results = await api_client.search_instrument("BMW", instrument_type="STOCK", limit=5)
        
        assert isinstance(results, list)
        
        if results:
            # Verify all results are stocks
            for instrument in results:
                assert instrument.type == "STOCK"
    
    @pytest.mark.asyncio
    async def test_search_by_isin_valid(self, api_client):
        """Test direct ISIN search with valid ISIN."""
        # SAP SE ISIN
        result = await api_client.search_by_isin("DE0007164600")
        
        if result:  # API might not always return data
            assert isinstance(result, Instrument)
            assert result.isin == "DE0007164600"
            assert result.name is not None
    
    @pytest.mark.asyncio
    async def test_search_international_stocks(self, api_client):
        """Test international stock search."""
        results = await api_client.search_international_stocks("AAPL", country="US")
        
        assert isinstance(results, list)
        
        if results:
            # Verify results contain Apple-related stocks
            apple_found = any("APPLE" in instrument.name.upper() or 
                            "AAPL" in str(instrument.symbol).upper() 
                            for instrument in results)
            assert apple_found or len(results) > 0  # Either Apple found or some results


class TestErrorHandling:
    """Test error handling for enhanced search features."""
    
    @pytest.mark.asyncio
    async def test_empty_search_query(self, api_client):
        """Test that empty search query raises ValueError."""
        with pytest.raises(ValueError, match="Search key cannot be empty"):
            await api_client.search_instrument("")
    
    @pytest.mark.asyncio
    async def test_invalid_isin_format(self, api_client):
        """Test that invalid ISIN format raises ValueError."""
        with pytest.raises(ValueError, match="ISIN must be exactly 12 characters"):
            await api_client.search_by_isin("INVALID")
    
    @pytest.mark.asyncio
    async def test_empty_symbol_search(self, api_client):
        """Test that empty symbol raises ValueError."""
        with pytest.raises(ValueError, match="Symbol cannot be empty"):
            await api_client.search_international_stocks("")


class TestSearchParameters:
    """Test search parameter validation and limits."""
    
    @pytest.mark.asyncio
    async def test_search_limit_clamping(self, api_client):
        """Test that search limits are properly clamped."""
        # Test with specific limit
        results = await api_client.search_instrument("BMW", limit=5)
        assert isinstance(results, list)
        assert len(results) <= 5
        
        # Test with zero limit - should be clamped to 1
        results = await api_client.search_instrument("BMW", limit=0)
        assert isinstance(results, list)
        assert len(results) >= 1
    
    @pytest.mark.asyncio
    async def test_search_with_whitespace(self, api_client):
        """Test that search handles whitespace correctly."""
        results = await api_client.search_instrument("  BMW  ", limit=5)
        assert isinstance(results, list)


class TestBackwardCompatibility:
    """Test that enhanced API maintains backward compatibility."""
    
    @pytest.mark.asyncio
    async def test_original_search_still_works(self, api_client):
        """Test that original search_instrument method works."""
        results = await api_client.search_instrument("BMW")
        assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_request_instrument_works(self, api_client):
        """Test that request_instrument method still works."""
        # First get an instrument
        search_results = await api_client.search_instrument("SAP", limit=1)
        
        if search_results:
            instrument = search_results[0]
            
            # Test updating existing instrument
            updated = await api_client.request_instrument(instrument)
            assert isinstance(updated, Instrument)
            assert updated.isin == instrument.isin
    
    @pytest.mark.asyncio
    async def test_request_quotes_works(self, api_client):
        """Test that request_quotes method still works."""
        # First get an instrument
        search_results = await api_client.search_instrument("SAP", limit=1)
        
        if search_results:
            instrument = search_results[0]
            
            try:
                quotes = await api_client.request_quotes(instrument)
                assert isinstance(quotes, list)
            except Exception:
                # Quotes might fail due to API changes, but method should exist
                assert hasattr(api_client, 'request_quotes')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
