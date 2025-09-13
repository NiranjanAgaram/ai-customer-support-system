#!/usr/bin/env python3
"""
AI Customer Support System - Test Script
Comprehensive testing of all system components
"""

import requests
import json
import time
from datetime import datetime

API_BASE = "http://localhost:8000"

def print_header(title):
    print(f"\n{'='*60}")
    print(f"🧪 {title}")
    print(f"{'='*60}")

def print_success(message):
    print(f"✅ {message}")

def print_error(message):
    print(f"❌ {message}")

def print_info(message):
    print(f"ℹ️  {message}")

def test_connection():
    """Test if the backend is running"""
    print_header("Testing Backend Connection")
    
    try:
        response = requests.get(f"{API_BASE}/")
        if response.status_code == 200:
            data = response.json()
            print_success(f"Backend is running: {data['service']} v{data['version']}")
            print_info(f"Timestamp: {data['timestamp']}")
            return True
        else:
            print_error(f"Backend returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to backend. Make sure it's running on port 8000")
        print_info("Start with: ./start_backend.sh")
        return False
    except Exception as e:
        print_error(f"Connection test failed: {e}")
        return False

def test_health_check():
    """Test health check endpoint"""
    print_header("Testing Health Check")
    
    try:
        response = requests.get(f"{API_BASE}/health")
        if response.status_code == 200:
            data = response.json()
            print_success("Health check passed")
            print_info(f"Status: {data['status']}")
            print_info(f"Components: {data['components']}")
            return True
        else:
            print_error(f"Health check failed with status: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Health check failed: {e}")
        return False

def test_ai_agents():
    """Test all AI agents with different query types"""
    print_header("Testing Multi-Agent AI System")
    
    test_queries = [
        {
            "query": "I cannot log into my account",
            "expected_agent": "technical",
            "description": "Login issue (Technical)"
        },
        {
            "query": "I was charged twice for my subscription this month",
            "expected_agent": "billing", 
            "description": "Billing issue (Billing)"
        },
        {
            "query": "The application is not working and showing errors",
            "expected_agent": "technical",
            "description": "Technical problem (Technical)"
        },
        {
            "query": "How do I cancel my subscription?",
            "expected_agent": "billing",
            "description": "Cancellation question (Billing)"
        },
        {
            "query": "Hello, I need some help",
            "expected_agent": "general",
            "description": "General inquiry (General)"
        }
    ]
    
    results = []
    
    for i, test in enumerate(test_queries, 1):
        print(f"\n🔍 Test {i}: {test['description']}")
        print(f"Query: \"{test['query']}\"")
        
        try:
            payload = {
                "query": test["query"],
                "customer_id": f"test_customer_{i}",
                "priority": "medium"
            }
            
            start_time = time.time()
            response = requests.post(f"{API_BASE}/api/v1/query", json=payload)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                # Check agent routing
                agent_correct = data["agent_type"] == test["expected_agent"]
                agent_status = "✅" if agent_correct else "⚠️"
                
                print(f"  {agent_status} Agent: {data['agent_type']} (expected: {test['expected_agent']})")
                print(f"  📊 Confidence: {data['confidence']:.1%}")
                print(f"  ⏱️  Response Time: {response_time:.2f}s")
                print(f"  🔄 Escalate: {'Yes' if data['escalate'] else 'No'}")
                print(f"  💬 Response: {data['response'][:100]}...")
                
                results.append({
                    "test": test["description"],
                    "agent_correct": agent_correct,
                    "confidence": data["confidence"],
                    "response_time": response_time,
                    "escalate": data["escalate"]
                })
                
                if agent_correct:
                    print_success("Agent routing correct")
                else:
                    print_error(f"Agent routing incorrect: got {data['agent_type']}, expected {test['expected_agent']}")
                    
            else:
                print_error(f"Query failed with status: {response.status_code}")
                results.append({"test": test["description"], "agent_correct": False})
                
        except Exception as e:
            print_error(f"Query test failed: {e}")
            results.append({"test": test["description"], "agent_correct": False})
    
    # Summary
    print(f"\n📋 Agent Test Summary:")
    correct_routing = sum(1 for r in results if r.get("agent_correct", False))
    total_tests = len(results)
    accuracy = (correct_routing / total_tests) * 100 if total_tests > 0 else 0
    
    print(f"  Routing Accuracy: {correct_routing}/{total_tests} ({accuracy:.1f}%)")
    
    if results:
        avg_confidence = sum(r.get("confidence", 0) for r in results) / len(results)
        avg_response_time = sum(r.get("response_time", 0) for r in results) / len(results)
        print(f"  Average Confidence: {avg_confidence:.1%}")
        print(f"  Average Response Time: {avg_response_time:.2f}s")
    
    return accuracy >= 80  # 80% accuracy threshold

def test_analytics():
    """Test analytics endpoint"""
    print_header("Testing Analytics System")
    
    try:
        response = requests.get(f"{API_BASE}/api/v1/analytics")
        if response.status_code == 200:
            data = response.json()
            print_success("Analytics endpoint working")
            print_info(f"Total Queries: {data.get('total_queries', 0)}")
            print_info(f"Average Response Time: {data.get('avg_response_time', 0)}s")
            print_info(f"Satisfaction Score: {data.get('satisfaction_score', 0)}/5")
            
            agent_dist = data.get('agent_distribution', {})
            if agent_dist:
                print_info("Agent Distribution:")
                for agent, count in agent_dist.items():
                    print(f"    {agent.title()}: {count} queries")
            
            return True
        else:
            print_error(f"Analytics failed with status: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Analytics test failed: {e}")
        return False

def test_api_documentation():
    """Test API documentation endpoint"""
    print_header("Testing API Documentation")
    
    try:
        response = requests.get(f"{API_BASE}/docs")
        if response.status_code == 200:
            print_success("API documentation is accessible")
            print_info(f"Visit: {API_BASE}/docs")
            return True
        else:
            print_error(f"API docs failed with status: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"API docs test failed: {e}")
        return False

def main():
    """Run all tests"""
    print_header("AI Customer Support System - Comprehensive Test")
    print_info(f"Testing system at: {API_BASE}")
    print_info(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("Backend Connection", test_connection),
        ("Health Check", test_health_check),
        ("AI Agents", test_ai_agents),
        ("Analytics", test_analytics),
        ("API Documentation", test_api_documentation)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print_error(f"{test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Final Summary
    print_header("Test Results Summary")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {test_name}")
    
    print(f"\n🎯 Overall Score: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    
    if passed == total:
        print_success("🎉 All tests passed! Your AI Customer Support System is working perfectly!")
        print_info("🌐 Open test_interface.html in your browser to try the visual interface")
        print_info(f"📚 API Documentation: {API_BASE}/docs")
    else:
        print_error("Some tests failed. Check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    main()