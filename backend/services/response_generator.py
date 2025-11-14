"""
Response Generator Service

Generates factual, citation-backed responses using RAG pipeline and LLM.
"""

import logging
from typing import List, Dict, Optional, Any
import time

from backend.config.settings import settings
from backend.models.knowledge import KnowledgeChunk, RetrievalResult
from backend.services.groww_mapper import get_groww_mapper
from backend.services.llm_service import get_llm_service, LLMGenerationResult
from backend.services.rag_retrieval import get_rag_retrieval
from backend.utils.guardrails import get_guardrails, ViolationType

logger = logging.getLogger(__name__)


class ResponseGenerator:
    """
    Generates responses using RAG pipeline and LLM with prompt engineering.
    
    Ensures responses are factual, citation-backed, and compliant with guidelines.
    """

    def __init__(self):
        """Initialize the response generator."""
        self.llm_service = get_llm_service()
        self.rag_retrieval = get_rag_retrieval()
        self.guardrails = get_guardrails(strict_mode=True)
        self.groww_mapper = get_groww_mapper()
        
        logger.info("ResponseGenerator initialized with guardrails and Groww mapper enabled")

    def generate_response(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate a complete response for a user query.
        
        Args:
            query: User's question
            filters: Optional metadata filters for retrieval
            session_id: Optional session ID for tracking
            
        Returns:
            Dictionary with response, sources, and metadata
        """
        start_time = time.time()
        
        try:
            logger.info(f"Generating response for query: '{query}'")
            
            # Step 0: Check query for advice-seeking patterns (guardrail)
            query_safe, query_violation = self.guardrails.check_query(query)
            if not query_safe:
                logger.warning(
                    f"Query blocked by guardrails: {query_violation.violation_type.value}"
                )
                return {
                    "response": self.guardrails.get_safe_response_template(),
                    "sources": [],
                    "groww_page_url": None,
                    "chunks_retrieved": 0,
                    "generation_time_ms": 0.0,
                    "retrieval_time_ms": 0.0,
                    "llm_tokens_used": 0,
                    "guardrail_blocked": True,
                    "violation": query_violation.to_dict() if query_violation else None,
                }
            
            # Step 1: Retrieve relevant knowledge chunks
            retrieval_result = self.rag_retrieval.retrieve(
                query=query,
                filters=filters,
            )
            
            # Check if we have relevant context
            if not retrieval_result.chunks:
                logger.warning(f"No relevant chunks found for query: '{query}'")
                return self._generate_fallback_response(query)
            
            # Step 2: Build context from retrieved chunks
            context = self.rag_retrieval.get_context_window(
                chunks=retrieval_result.chunks,
                max_tokens=2000,
            )
            
            # Step 3: Check Groww page availability (FALLBACK LOGIC - Priority 1)
            groww_page_url = self.groww_mapper.find_groww_page(
                query=query,
                chunks=retrieval_result.chunks,
            )
            
            # Step 4: Extract and prioritize sources (FALLBACK LOGIC - Priority 2)
            sources = self.rag_retrieval.get_sources(
                chunks=retrieval_result.chunks,
            )
            
            # Prioritize Groww sources first, then external AMC/SEBI/AMFI
            sources = self.groww_mapper.prioritize_sources(sources)
            
            # If no Groww page found but we have external sources, that's acceptable
            if not groww_page_url and sources:
                logger.info(
                    f"No Groww page found, using {len(sources)} external sources as fallback"
                )
            
            # Step 5: Build prompt with context
            prompt = self._build_factual_prompt(
                query=query,
                context=context,
                sources=sources,
            )
            
            # Step 6: Generate response using LLM
            llm_result = self.llm_service.generate(
                prompt=prompt,
                temperature=settings.LLM_TEMPERATURE,
                max_tokens=settings.LLM_MAX_TOKENS,
            )
            
            # Step 7: Post-process and validate response
            response_text = self._post_process_response(llm_result.text)
            
            # Step 8: Check response for compliance violations (guardrail)
            response_safe, response_violations = self.guardrails.check_response(response_text)
            
            if not response_safe:
                logger.warning(
                    f"Response contains {len(response_violations)} guardrail violations"
                )
                # Attempt to sanitize the response
                response_text = self.guardrails.sanitize_response(
                    response_text,
                    response_violations,
                )
                logger.info("Response sanitized by guardrails")
            
            # Calculate total generation time
            generation_time_ms = (time.time() - start_time) * 1000
            
            # Get Groww mapping metadata
            groww_metadata = self.groww_mapper.create_response_metadata(
                query=query,
                chunks=retrieval_result.chunks,
            )
            
            logger.info(
                f"Generated response in {generation_time_ms:.2f}ms "
                f"(retrieved {len(retrieval_result.chunks)} chunks, "
                f"Groww available: {groww_metadata['groww_availability']['is_available_on_groww']})"
            )
            
            return {
                "response": response_text,
                "sources": sources,
                "groww_page_url": groww_page_url,
                "chunks_retrieved": len(retrieval_result.chunks),
                "generation_time_ms": generation_time_ms,
                "retrieval_time_ms": retrieval_result.retrieval_time_ms,
                "llm_tokens_used": llm_result.tokens_used,
                "session_id": session_id,
                "guardrail_violations": len(response_violations) if not response_safe else 0,
                "guardrail_blocked": False,
                "groww_metadata": groww_metadata,
                "fallback_level": self._determine_fallback_level(groww_page_url, sources),
            }
            
        except Exception as e:
            logger.error(f"Response generation failed: {e}", exc_info=True)
            raise

    def _build_factual_prompt(
        self,
        query: str,
        context: str,
        sources: List[Dict[str, Any]],
    ) -> str:
        """
        Build a prompt engineered for factual, citation-backed responses.
        
        Args:
            query: User's question
            context: Retrieved context from knowledge base
            sources: List of source documents
            
        Returns:
            Engineered prompt string
        """
        # Build source references for the prompt
        source_refs = "\n".join([
            f"[{i+1}] {src.get('title', 'Untitled')} - {src['url']}"
            for i, src in enumerate(sources)
        ])
        
        prompt = f"""You are a factual FAQ assistant for mutual fund information. Your role is to provide accurate, concise answers based ONLY on the provided context.

STRICT GUIDELINES:
1. Answer ONLY using information from the context provided below
2. Be factual and precise - no speculation or assumptions
3. Keep responses concise (2-4 sentences maximum)
4. Reference sources using [Source N] notation when stating facts
5. If the context doesn't contain enough information to answer, say "I don't have specific information about this in my knowledge base."
6. NEVER provide investment advice, recommendations, or predictions
7. NEVER suggest buying, selling, or holding any mutual fund
8. Focus on factual data only: expense ratios, exit loads, minimum SIP amounts, lock-in periods, fund managers, benchmarks, etc.

CONTEXT FROM KNOWLEDGE BASE:
{context}

AVAILABLE SOURCES:
{source_refs}

USER QUESTION:
{query}

FACTUAL ANSWER (remember: no advice, only facts with source references):"""

        return prompt

    def _post_process_response(self, response: str) -> str:
        """
        Post-process the LLM response for quality and compliance.
        
        Args:
            response: Raw LLM response
            
        Returns:
            Cleaned and validated response
        """
        # Remove leading/trailing whitespace
        response = response.strip()
        
        # Remove any common LLM artifacts
        response = response.replace("```", "")
        
        # Check for compliance violations (investment advice keywords)
        advice_keywords = [
            "should buy",
            "should invest",
            "recommend",
            "suggested",
            "advice",
            "better to",
            "best choice",
            "you should",
            "I suggest",
            "consider buying",
            "good investment",
        ]
        
        response_lower = response.lower()
        for keyword in advice_keywords:
            if keyword in response_lower:
                logger.warning(f"Potential advice detected in response: '{keyword}'")
                # Flag for review but don't automatically reject
                # In production, you might want stricter handling
        
        return response

    def _generate_fallback_response(self, query: str) -> Dict[str, Any]:
        """
        Generate a fallback response when no relevant context is found.
        
        This is the FINAL FALLBACK (Priority 3) when:
        - No Groww page found
        - No external sources found
        
        Args:
            query: User's query
            
        Returns:
            Fallback response dictionary
        """
        fallback_text = (
            "I don't have specific information about this in my knowledge base. "
            "I can only answer factual questions about mutual fund schemes using "
            "verified sources from official AMC, SEBI, and AMFI websites. "
            "Please try rephrasing your question or ask about specific fund details like "
            "expense ratio, exit load, minimum SIP, or lock-in period."
        )
        
        return {
            "response": fallback_text,
            "sources": [],
            "groww_page_url": None,
            "chunks_retrieved": 0,
            "generation_time_ms": 0.0,
            "retrieval_time_ms": 0.0,
            "llm_tokens_used": 0,
            "is_fallback": True,
            "fallback_level": "generic",
        }
    
    def _determine_fallback_level(
        self,
        groww_page_url: Optional[str],
        sources: List[Dict[str, Any]],
    ) -> str:
        """
        Determine which fallback level was used.
        
        Priority order:
        1. Groww page (best)
        2. External sources (AMC/SEBI/AMFI)
        3. Generic fallback (no sources)
        
        Args:
            groww_page_url: Groww page URL if found
            sources: List of sources
            
        Returns:
            Fallback level: "groww", "external", or "generic"
        """
        if groww_page_url:
            return "groww"
        elif sources:
            # Check if we have at least one external source
            has_external = any(
                "groww.in" not in src.get("url", "").lower()
                for src in sources
            )
            if has_external:
                return "external"
            return "groww_sources_only"
        else:
            return "generic"

    def _extract_groww_url(self, chunks: List[KnowledgeChunk]) -> Optional[str]:
        """
        Extract the most relevant Groww page URL from chunks.
        
        Args:
            chunks: Retrieved knowledge chunks
            
        Returns:
            Groww page URL if available, None otherwise
        """
        for chunk in chunks:
            if chunk.groww_page_url:
                return chunk.groww_page_url
        return None

    def generate_response_with_amc_filter(
        self,
        query: str,
        amc_name: str,
        session_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate response filtered by specific AMC.
        
        Args:
            query: User's question
            amc_name: AMC name to filter by
            session_id: Optional session ID
            
        Returns:
            Response dictionary
        """
        logger.info(f"Generating response for AMC: {amc_name}")
        return self.generate_response(
            query=query,
            filters={"amc_name": amc_name},
            session_id=session_id,
        )

    def health_check(self) -> Dict[str, Any]:
        """
        Check if the response generator is healthy.
        
        Returns:
            Health status dictionary
        """
        try:
            llm_health = self.llm_service.health_check()
            rag_health = self.rag_retrieval.health_check()
            
            all_healthy = (
                llm_health["status"] == "healthy" and
                rag_health["status"] == "healthy"
            )
            
            return {
                "status": "healthy" if all_healthy else "unhealthy",
                "llm_service": llm_health,
                "rag_retrieval": rag_health,
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
            }


# Singleton instance
_response_generator_instance: Optional[ResponseGenerator] = None


def get_response_generator() -> ResponseGenerator:
    """
    Get or create the singleton ResponseGenerator instance.
    
    Returns:
        ResponseGenerator instance
    """
    global _response_generator_instance
    
    if _response_generator_instance is None:
        _response_generator_instance = ResponseGenerator()
    
    return _response_generator_instance

