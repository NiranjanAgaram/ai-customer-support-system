"""
Unit tests for AI Customer Support System
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from main import app, SimpleOrchestrator

client = TestClient(app)

class TestAPI:
    """Test API endpoints"""
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "AI Customer Support System" in data["service"]
    
    def test_health_check_endpoint(self):
        """Test detailed health check"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "components" in data
    
    def test_query_endpoint(self):
        """Test query processing endpoint"""
        test_query = {
            "query": "I cannot login to my account",
            "customer_id": "test_customer",
            "priority": "medium"
        }
        response = client.post("/api/v1/query", json=test_query)
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "agent_type" in data
        assert "confidence" in data
        assert data["agent_type"] in ["technical", "billing", "general"]
    
    def test_analytics_endpoint(self):
        """Test analytics endpoint"""
        response = client.get("/api/v1/analytics")
        assert response.status_code == 200
        data = response.json()
        assert "total_queries" in data
        assert "agent_distribution" in data

class TestClassification:
    """Test agent classification logic"""
    
    def setup_method(self):
        """Setup test orchestrator"""
        self.orchestrator = SimpleOrchestrator()
    
    @pytest.mark.asyncio
    async def test_technical_classification(self):
        """Test technical queries classification"""
        technical_queries = [
            "I cannot login to my account",
            "The app is not working",
            "Password reset issue",
            "Technical problem with login"
        ]
        
        for query in technical_queries:
            result = await self.orchestrator._classify_intent(query)
            assert result == "technical", f"Query '{query}' should be technical, got {result}"
    
    @pytest.mark.asyncio
    async def test_billing_classification(self):
        """Test billing queries classification"""
        billing_queries = [
            "I was charged twice this month",
            "Billing problem with my account",
            "Cancel my subscription",
            "Payment issue"
        ]
        
        for query in billing_queries:
            result = await self.orchestrator._classify_intent(query)
            assert result == "billing", f"Query '{query}' should be billing, got {result}"
    
    @pytest.mark.asyncio
    async def test_general_classification(self):
        """Test general queries classification"""
        general_queries = [
            "What are your business hours?",
            "How can I contact support?",
            "General information needed",
            "Hello, I need help"
        ]
        
        for query in general_queries:
            result = await self.orchestrator._classify_intent(query)
            assert result == "general", f"Query '{query}' should be general, got {result}"
    
    @pytest.mark.asyncio
    async def test_empty_query(self):
        """Test empty query handling"""
        result = await self.orchestrator._classify_intent("")
        assert result == "general"
    
    @pytest.mark.asyncio
    async def test_mixed_keywords(self):
        """Test queries with mixed keywords"""
        # Should prioritize billing due to specific billing phrases
        result = await self.orchestrator._classify_intent("I have a billing problem with login")
        assert result == "billing"
        
        # Should prioritize technical due to specific technical phrases  
        result = await self.orchestrator._classify_intent("Login issue with payment")
        assert result == "technical"

class TestValidation:
    """Test input validation"""
    
    def test_invalid_query_data(self):
        """Test invalid query data"""
        # Missing required fields
        response = client.post("/api/v1/query", json={})
        assert response.status_code == 422
        
        # Invalid priority
        invalid_query = {
            "query": "test query",
            "customer_id": "test",
            "priority": "invalid_priority"
        }
        response = client.post("/api/v1/query", json=invalid_query)
        assert response.status_code == 422
    
    def test_query_length_limits(self):
        """Test query length validation"""
        # Too long query
        long_query = {
            "query": "x" * 1001,  # Exceeds 1000 char limit
            "customer_id": "test"
        }
        response = client.post("/api/v1/query", json=long_query)
        assert response.status_code == 422

if __name__ == "__main__":
    pytest.main([__file__, "-v"])