import pytest

class TestSample:
    """Sample test class to verify pytest setup"""
    
    def test_sample(self) -> None:
        """Sample synchronous test"""
        assert True

    @pytest.mark.asyncio
    async def test_async_sample(self) -> None:
        """Sample asynchronous test"""
        assert True
