"""
Multi-Agent Orchestrator for Customer Support System
Routes queries to specialized agents using free Hugging Face models
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch
from sentence_transformers import SentenceTransformer
import numpy as np

logger = logging.getLogger(__name__)

class CustomerServiceOrchestrator:
    """Main orchestrator that routes queries to specialized agents"""
    
    def __init__(self):
        self.classifier = None
        self.embedding_model = None
        self.agents = {}
        self.knowledge_base = []
        self.initialized = False
    
    async def initialize(self):
        """Initialize all AI models and agents"""
        try:
            logger.info("Initializing AI models...")
            
            # Use keyword-based classification (more efficient than AI models)
            self.classifier = None
            
            # Load embedding model for RAG (free)
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Initialize specialized agents
            self.agents = {
                'technical': TechnicalSupportAgent(),
                'billing': BillingAgent(),
                'general': GeneralSupportAgent()
            }
            
            # Initialize knowledge base
            await self._setup_knowledge_base()
            
            self.initialized = True
            logger.info("AI models initialized successfully")
            
        except Exception as e:
            logger.error(f"Model initialization failed: {e}")
            raise
    
    async def process_query(self, query: str, customer_id: str, session_id: str, 
                          priority: str = "medium", metadata: Dict = None) -> Dict[str, Any]:
        """Process customer query through multi-agent system"""
        
        if not self.initialized:
            await self.initialize()
        
        try:
            # Step 1: Classify query intent
            intent = await self._classify_intent(query)
            
            # Step 2: Retrieve relevant knowledge
            context = await self._retrieve_context(query)
            
            # Step 3: Route to appropriate agent
            agent = self.agents.get(intent, self.agents['general'])
            
            # Step 4: Generate response
            response = await agent.handle_query(
                query=query,
                context=context,
                customer_id=customer_id,
                priority=priority
            )
            
            # Step 5: Add orchestrator metadata
            response.update({
                'intent': intent,
                'session_id': session_id,
                'knowledge_sources': len(context)
            })
            
            return response
            
        except Exception as e:
            logger.error(f"Query processing failed: {e}")
            return {
                'response': "I apologize, but I'm experiencing technical difficulties. Please try again or contact human support.",
                'agent_type': 'error',
                'confidence': 0.0,
                'escalate': True
            }
    
    async def _classify_intent(self, query: str) -> str:
        """Classify query intent using enhanced keyword matching"""
        try:
            query_lower = query.lower()
            
            # Enhanced technical keywords with more specific patterns
            technical_keywords = [
                'login', 'log in', 'sign in', 'access', 'password', 'account',
                'error', 'bug', 'not working', 'broken', 'crash', 'slow',
                'technical', 'application', 'app', 'reset', 'unlock', 
                'authenticate', 'verification'
            ]
            
            # Enhanced billing keywords
            billing_keywords = [
                'billing', 'payment', 'charge', 'charged', 'invoice', 'subscription',
                'refund', 'cancel', 'upgrade', 'downgrade', 'price', 'cost',
                'twice', 'double', 'money', 'credit card', 'bank', 'transaction'
            ]
            
            # Specific phrase matching for better accuracy
            technical_phrases = [
                'cannot log', 'can\'t log', 'unable to access', 'won\'t load',
                'not loading', 'application is', 'app is', 'showing error',
                'login issue', 'technical issue', 'technical problem'
            ]
            
            billing_phrases = [
                'charged twice', 'billed twice', 'double charge', 'cancel subscription',
                'how do i cancel', 'want to cancel', 'subscription cost',
                'billing problem', 'billing issue', 'payment problem'
            ]
            
            # Generic words that need context
            generic_words = ['issue', 'problem', 'question', 'help', 'support']
            
            # Check for specific phrases first (higher weight)
            technical_score = 0
            billing_score = 0
            
            # Phrase matching (weight: 5)
            for phrase in technical_phrases:
                if phrase in query_lower:
                    technical_score += 5
            
            for phrase in billing_phrases:
                if phrase in query_lower:
                    billing_score += 5
            
            # Check for domain-specific combinations (weight: 3)
            if any(tech_word in query_lower for tech_word in ['technical', 'login', 'password', 'access', 'app', 'application']) and any(generic in query_lower for generic in generic_words):
                technical_score += 3
            
            if any(bill_word in query_lower for bill_word in ['billing', 'payment', 'charge', 'subscription', 'money']) and any(generic in query_lower for generic in generic_words):
                billing_score += 3
            
            # Keyword matching (weight: 1)
            for keyword in technical_keywords:
                if keyword in query_lower:
                    technical_score += 1
            
            for keyword in billing_keywords:
                if keyword in query_lower:
                    billing_score += 1
            
            # Determine intent with improved logic
            if technical_score > billing_score and technical_score > 0:
                return 'technical'
            elif billing_score > technical_score and billing_score > 0:
                return 'billing'
            elif technical_score == billing_score and technical_score > 0:
                # Better tie-breaker: check for more specific domain indicators
                if any(word in query_lower for word in ['login', 'password', 'access', 'account', 'technical']):
                    return 'technical'
                elif any(word in query_lower for word in ['billing', 'charge', 'payment', 'subscription', 'money']):
                    return 'billing'
            
            return 'general'
                
        except Exception as e:
            logger.error(f"Intent classification failed: {e}")
            return 'general'
    
    async def _retrieve_context(self, query: str, top_k: int = 3) -> List[Dict[str, str]]:
        """Retrieve relevant context from knowledge base using embeddings"""
        try:
            if not self.knowledge_base:
                return []
            
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query])
            
            # Calculate similarities using pre-computed embeddings
            similarities = []
            for i, doc in enumerate(self.knowledge_base):
                similarity = np.dot(query_embedding[0], doc['embedding']) / (
                    np.linalg.norm(query_embedding[0]) * np.linalg.norm(doc['embedding'])
                )
                similarities.append((i, similarity))
            
            # Get top-k most similar documents
            similarities.sort(key=lambda x: x[1], reverse=True)
            top_docs = [self.knowledge_base[i] for i, _ in similarities[:top_k]]
            
            return top_docs
            
        except Exception as e:
            logger.error(f"Context retrieval failed: {e}")
            return []
    
    async def _setup_knowledge_base(self):
        """Setup knowledge base with pre-computed embeddings"""
        docs = [
            {
                'id': '1',
                'title': 'Login Issues',
                'content': 'If you cannot log in, try resetting your password. Click "Forgot Password" on the login page and follow the instructions.',
                'category': 'technical'
            },
            {
                'id': '2',
                'title': 'Billing Cycles',
                'content': 'Billing occurs monthly on the date you signed up. You can view your billing history in Account Settings > Billing.',
                'category': 'billing'
            },
            {
                'id': '3',
                'title': 'Account Cancellation',
                'content': 'To cancel your account, go to Settings > Account > Cancel Subscription. You will retain access until the end of your billing period.',
                'category': 'billing'
            },
            {
                'id': '4',
                'title': 'Performance Issues',
                'content': 'If the application is running slowly, try clearing your browser cache or using a different browser. Contact support if issues persist.',
                'category': 'technical'
            },
            {
                'id': '5',
                'title': 'Feature Requests',
                'content': 'We welcome feature requests! Please submit them through our feedback form or contact support with your suggestions.',
                'category': 'general'
            }
        ]
        
        # Pre-compute embeddings once
        for doc in docs:
            doc['embedding'] = self.embedding_model.encode([doc['content']])[0]
        
        self.knowledge_base = docs
    
    async def health_check(self) -> bool:
        """Check if all models are loaded and working"""
        try:
            if not self.initialized:
                return False
            
            # Test classification
            test_intent = await self._classify_intent("test query")
            
            # Test embedding
            if self.embedding_model:
                self.embedding_model.encode(["test"])
                
            return True
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    async def cleanup(self):
        """Cleanup resources"""
        self.classifier = None
        self.embedding_model = None
        self.agents = {}
        self.initialized = False


class TechnicalSupportAgent:
    """Specialized agent for technical support queries"""
    
    async def handle_query(self, query: str, context: List[Dict], 
                          customer_id: str, priority: str) -> Dict[str, Any]:
        """Handle technical support queries"""
        
        # Generate technical response based on context
        if context:
            relevant_info = "\n".join(doc['content'] for doc in context)
            response = f"Based on our documentation, here's how I can help with your technical issue:\n\n{relevant_info}\n\nIf this doesn't resolve your issue, I can escalate to our technical team."
        else:
            response = "I understand you're experiencing a technical issue. Let me help troubleshoot this. Can you provide more details about the specific problem you're encountering?"
        
        return {
            'response': response,
            'agent_type': 'technical',
            'confidence': 0.85,
            'escalate': priority == 'urgent',
            'suggested_actions': [
                'Try the suggested solution',
                'Clear browser cache',
                'Contact technical team if issue persists'
            ]
        }


class BillingAgent:
    """Specialized agent for billing and payment queries"""
    
    async def handle_query(self, query: str, context: List[Dict], 
                          customer_id: str, priority: str) -> Dict[str, Any]:
        """Handle billing and payment queries"""
        
        # Generate billing response based on context
        if context:
            relevant_info = "\n".join(doc['content'] for doc in context)
            response = f"I can help you with your billing question. Here's the relevant information:\n\n{relevant_info}\n\nFor account-specific billing details, I may need to connect you with our billing team."
        else:
            response = f"I'm here to help with your billing inquiry for customer {customer_id}. I can assist with payment issues, subscription changes, and billing questions."
        
        return {
            'response': response,
            'agent_type': 'billing',
            'confidence': 0.90,
            'escalate': 'refund' in query.lower() or 'cancel' in query.lower(),
            'suggested_actions': [
                'Check account settings',
                'Review billing history',
                'Contact billing team for account changes'
            ]
        }


class GeneralSupportAgent:
    """General support agent for non-specialized queries"""
    
    async def handle_query(self, query: str, context: List[Dict], 
                          customer_id: str, priority: str) -> Dict[str, Any]:
        """Handle general support queries"""
        
        # Generate general response
        if context:
            relevant_info = "\n".join(doc['content'] for doc in context)
            response = f"Thank you for contacting support. I found some relevant information that might help:\n\n{relevant_info}\n\nIs there anything specific I can help you with today?"
        else:
            response = "Thank you for contacting our support team. I'm here to help you with any questions or concerns you may have. How can I assist you today?"
        
        return {
            'response': response,
            'agent_type': 'general',
            'confidence': 0.75,
            'escalate': priority in ['high', 'urgent'],
            'suggested_actions': [
                'Provide more specific details',
                'Check our help documentation',
                'Contact specialized support if needed'
            ]
        }