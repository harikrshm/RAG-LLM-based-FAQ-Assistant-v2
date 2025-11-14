"""
Prompt Guardrails

Utilities to prevent investment advice generation and ensure compliance.
"""

import logging
import re
from typing import Dict, List, Optional, Tuple
from enum import Enum

logger = logging.getLogger(__name__)


class ViolationType(Enum):
    """Types of compliance violations."""
    INVESTMENT_ADVICE = "investment_advice"
    RECOMMENDATION = "recommendation"
    PREDICTION = "prediction"
    PERSONAL_OPINION = "personal_opinion"
    NONE = "none"


class GuardrailViolation:
    """Represents a guardrail violation."""
    
    def __init__(
        self,
        violation_type: ViolationType,
        matched_pattern: str,
        context: str,
        severity: str = "high",
    ):
        self.violation_type = violation_type
        self.matched_pattern = matched_pattern
        self.context = context
        self.severity = severity
    
    def to_dict(self) -> Dict:
        return {
            "type": self.violation_type.value,
            "pattern": self.matched_pattern,
            "context": self.context,
            "severity": self.severity,
        }


class PromptGuardrails:
    """
    Guardrails to prevent investment advice and ensure factual responses.
    
    Checks both user queries and LLM responses for compliance violations.
    """
    
    # Patterns that indicate investment advice
    ADVICE_PATTERNS = [
        # Direct recommendations
        r"\b(should|must|need to)\s+(buy|invest|purchase|sell|hold|exit)\b",
        r"\b(recommend|suggests?|advise)\s+.{0,20}\b(buy|invest|sell)\b",
        r"\b(better|best|good|great|excellent)\s+(investment|choice|option|fund)\b",
        r"\b(go for|opt for|choose)\s+.{0,20}\bfund\b",
        
        # Suggestions
        r"\bI (suggest|recommend|advise|think you should)\b",
        r"\byou (should|must|need to|ought to)\b",
        r"\bit('s| is) (advisable|recommended|suggested)\b",
        r"\b(consider|try) (buying|investing|purchasing)\b",
        
        # Predictions
        r"\b(will|going to|expected to)\s+(grow|increase|rise|perform|return)\b",
        r"\b(predict|forecast|expect).{0,30}(return|growth|performance)\b",
        r"\blikely to (outperform|beat|exceed)\b",
        
        # Performance opinions
        r"\b(good|bad|poor|excellent|superior|inferior)\s+(performance|returns?)\b",
        r"\b(overvalued|undervalued|overpriced|underpriced)\b",
        r"\b(strong|weak)\s+(buy|sell|hold)\b",
    ]
    
    # Keywords that strongly indicate advice
    ADVICE_KEYWORDS = [
        "should buy",
        "should invest",
        "should sell",
        "should hold",
        "i recommend",
        "i suggest",
        "i advise",
        "my recommendation",
        "my suggestion",
        "best choice",
        "good investment",
        "bad investment",
        "better option",
        "optimal choice",
        "ideal fund",
        "perfect for",
        "suitable for you",
        "right for you",
        "avoid this",
        "stay away",
        "go ahead",
        "definitely buy",
        "definitely invest",
    ]
    
    # Safe factual phrases (allow these)
    FACTUAL_PATTERNS = [
        r"\b(expense ratio|exit load|minimum sip|lock-in period|nav|aum)\b",
        r"\b(fund manager|benchmark|category|type|rating)\b",
        r"\b(historical|past|previous)\s+(return|performance)\b",
        r"\briskometer\s+(level|rating)\b",
        r"\b(available|offered|provided)\s+by\b",
    ]
    
    def __init__(self, strict_mode: bool = True):
        """
        Initialize guardrails.
        
        Args:
            strict_mode: If True, more aggressive filtering
        """
        self.strict_mode = strict_mode
        self.compiled_patterns = [
            re.compile(pattern, re.IGNORECASE)
            for pattern in self.ADVICE_PATTERNS
        ]
        self.compiled_factual = [
            re.compile(pattern, re.IGNORECASE)
            for pattern in self.FACTUAL_PATTERNS
        ]
    
    def check_query(self, query: str) -> Tuple[bool, Optional[GuardrailViolation]]:
        """
        Check if a user query is requesting investment advice.
        
        Args:
            query: User's question
            
        Returns:
            Tuple of (is_safe, violation_if_any)
        """
        query_lower = query.lower()
        
        # Check for advice-seeking patterns
        advice_seeking = [
            r"\bshould I (buy|invest|sell|hold)\b",
            r"\bwhat (should|must) I (do|buy|invest)\b",
            r"\b(which|what) (fund|scheme).{0,30}(best|better|recommend)\b",
            r"\b(help me|advise me|recommend|suggest).{0,30}(invest|fund)\b",
            r"\bis it (good|advisable|wise) to (buy|invest)\b",
        ]
        
        for pattern in advice_seeking:
            match = re.search(pattern, query_lower)
            if match:
                logger.warning(f"Query contains advice-seeking pattern: {match.group()}")
                return False, GuardrailViolation(
                    violation_type=ViolationType.INVESTMENT_ADVICE,
                    matched_pattern=match.group(),
                    context=query,
                    severity="high",
                )
        
        # Query is safe
        return True, None
    
    def check_response(self, response: str) -> Tuple[bool, List[GuardrailViolation]]:
        """
        Check if a response contains investment advice.
        
        Args:
            response: Generated response text
            
        Returns:
            Tuple of (is_safe, list_of_violations)
        """
        violations = []
        response_lower = response.lower()
        
        # Check keyword violations
        for keyword in self.ADVICE_KEYWORDS:
            if keyword in response_lower:
                logger.warning(f"Response contains advice keyword: {keyword}")
                violations.append(GuardrailViolation(
                    violation_type=ViolationType.INVESTMENT_ADVICE,
                    matched_pattern=keyword,
                    context=self._extract_context(response, keyword),
                    severity="high",
                ))
        
        # Check pattern violations
        for pattern in self.compiled_patterns:
            matches = pattern.finditer(response)
            for match in matches:
                matched_text = match.group()
                
                # Skip if it's in a factual context
                if self._is_factual_context(response, match.start(), match.end()):
                    continue
                
                logger.warning(f"Response contains advice pattern: {matched_text}")
                violations.append(GuardrailViolation(
                    violation_type=ViolationType.RECOMMENDATION,
                    matched_pattern=matched_text,
                    context=self._extract_context(response, matched_text),
                    severity="high",
                ))
        
        is_safe = len(violations) == 0
        return is_safe, violations
    
    def _is_factual_context(self, text: str, start: int, end: int) -> bool:
        """
        Check if a match is in a factual context (e.g., describing features).
        
        Args:
            text: Full text
            start: Start position of match
            end: End position of match
            
        Returns:
            True if factual context
        """
        # Get surrounding context (50 chars before and after)
        context_start = max(0, start - 50)
        context_end = min(len(text), end + 50)
        context = text[context_start:context_end].lower()
        
        # Check for factual indicators
        for pattern in self.compiled_factual:
            if pattern.search(context):
                return True
        
        return False
    
    def _extract_context(self, text: str, keyword: str, window: int = 50) -> str:
        """
        Extract context around a keyword match.
        
        Args:
            text: Full text
            keyword: Matched keyword
            window: Characters to include on each side
            
        Returns:
            Context string
        """
        text_lower = text.lower()
        keyword_lower = keyword.lower()
        
        pos = text_lower.find(keyword_lower)
        if pos == -1:
            return text[:100]  # Return beginning if not found
        
        start = max(0, pos - window)
        end = min(len(text), pos + len(keyword) + window)
        
        context = text[start:end]
        if start > 0:
            context = "..." + context
        if end < len(text):
            context = context + "..."
        
        return context
    
    def sanitize_response(
        self,
        response: str,
        violations: List[GuardrailViolation],
    ) -> str:
        """
        Attempt to sanitize a response by removing violating sections.
        
        Args:
            response: Original response
            violations: List of violations found
            
        Returns:
            Sanitized response (or empty if too many violations)
        """
        if len(violations) >= 3:
            # Too many violations - return safe fallback
            return (
                "I can only provide factual information about mutual funds. "
                "I cannot offer investment advice or recommendations."
            )
        
        # Remove sentences containing violations
        sentences = re.split(r'[.!?]+', response)
        safe_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # Check if sentence contains any violation
            has_violation = False
            for violation in violations:
                if violation.matched_pattern.lower() in sentence.lower():
                    has_violation = True
                    break
            
            if not has_violation:
                safe_sentences.append(sentence)
        
        if not safe_sentences:
            return (
                "I can only provide factual information about mutual funds. "
                "I cannot offer investment advice or recommendations."
            )
        
        return ". ".join(safe_sentences) + "."
    
    def get_safe_response_template(self) -> str:
        """
        Get a safe template response for advice-seeking queries.
        
        Returns:
            Safe response template
        """
        return (
            "I cannot provide investment advice or recommendations. "
            "I can only share factual information about mutual fund schemes, "
            "such as expense ratios, exit loads, minimum SIP amounts, "
            "lock-in periods, and other objective details. "
            "Please rephrase your question to ask about specific factual information."
        )


# Singleton instance
_guardrails_instance: Optional[PromptGuardrails] = None


def get_guardrails(strict_mode: bool = True) -> PromptGuardrails:
    """
    Get or create the singleton PromptGuardrails instance.
    
    Args:
        strict_mode: Enable strict checking
        
    Returns:
        PromptGuardrails instance
    """
    global _guardrails_instance
    
    if _guardrails_instance is None:
        _guardrails_instance = PromptGuardrails(strict_mode=strict_mode)
    
    return _guardrails_instance

