import httpx
import json
from difflib import SequenceMatcher

from app.config import settings


class EvaluatorService:
    """Service for evaluating shadowing practice using LLM."""

    EVALUATION_PROMPT = """You are an English pronunciation and shadowing practice evaluator.

Compare the original text with the user's transcribed speech and provide feedback.

Original text: {original_text}
User's transcription: {transcribed_text}

Analyze the following aspects:
1. Accuracy: How closely does the transcription match the original?
2. Missing words: Which words were missed or unclear?
3. Added words: Were there any extra words?
4. Pronunciation issues: Based on common transcription errors, what pronunciation areas need work?

Provide your evaluation in the following JSON format:
{{
    "accuracy_score": <0-100>,
    "missing_words": ["word1", "word2"],
    "added_words": ["word1", "word2"],
    "pronunciation_notes": "Brief notes on pronunciation areas to improve",
    "overall_feedback": "Encouraging overall feedback with specific suggestions",
    "strengths": ["strength1", "strength2"],
    "areas_to_improve": ["area1", "area2"]
}}

Respond ONLY with the JSON, no additional text."""

    async def evaluate(
        self, original_text: str, transcribed_text: str
    ) -> dict:
        """Evaluate transcription against original text."""
        # Calculate basic accuracy first
        basic_accuracy = self._calculate_accuracy(original_text, transcribed_text)

        if settings.llm_provider == "ollama":
            return await self._evaluate_with_ollama(
                original_text, transcribed_text, basic_accuracy
            )
        elif settings.llm_provider == "claude":
            return await self._evaluate_with_claude(
                original_text, transcribed_text, basic_accuracy
            )
        else:
            # Fallback to basic evaluation
            return self._basic_evaluation(
                original_text, transcribed_text, basic_accuracy
            )

    def _calculate_accuracy(self, original: str, transcribed: str) -> float:
        """Calculate basic text similarity."""
        original_lower = original.lower().strip()
        transcribed_lower = transcribed.lower().strip()
        ratio = SequenceMatcher(None, original_lower, transcribed_lower).ratio()
        return round(ratio * 100, 1)

    def _basic_evaluation(
        self, original: str, transcribed: str, accuracy: float
    ) -> dict:
        """Basic evaluation without LLM."""
        original_words = set(original.lower().split())
        transcribed_words = set(transcribed.lower().split())

        missing = list(original_words - transcribed_words)
        added = list(transcribed_words - original_words)

        return {
            "accuracy_score": accuracy,
            "missing_words": missing[:5],  # Limit to 5
            "added_words": added[:5],
            "pronunciation_notes": "LLM evaluation not available",
            "overall_feedback": f"Accuracy: {accuracy}%. Keep practicing!",
            "strengths": [],
            "areas_to_improve": missing[:3] if missing else [],
        }

    async def _evaluate_with_ollama(
        self, original: str, transcribed: str, basic_accuracy: float
    ) -> dict:
        """Evaluate using Ollama."""
        prompt = self.EVALUATION_PROMPT.format(
            original_text=original,
            transcribed_text=transcribed,
        )

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{settings.ollama_base_url}/api/generate",
                    json={
                        "model": settings.ollama_model,
                        "prompt": prompt,
                        "stream": False,
                        "format": "json",
                    },
                )
                response.raise_for_status()

                result = response.json()
                evaluation = json.loads(result["response"])
                return evaluation

        except Exception as e:
            # Fallback to basic evaluation
            return self._basic_evaluation(original, transcribed, basic_accuracy)

    async def _evaluate_with_claude(
        self, original: str, transcribed: str, basic_accuracy: float
    ) -> dict:
        """Evaluate using Claude API."""
        if not settings.claude_api_key:
            return self._basic_evaluation(original, transcribed, basic_accuracy)

        prompt = self.EVALUATION_PROMPT.format(
            original_text=original,
            transcribed_text=transcribed,
        )

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={
                        "x-api-key": settings.claude_api_key,
                        "anthropic-version": "2023-06-01",
                        "content-type": "application/json",
                    },
                    json={
                        "model": "claude-3-haiku-20240307",
                        "max_tokens": 1024,
                        "messages": [
                            {"role": "user", "content": prompt}
                        ],
                    },
                )
                response.raise_for_status()

                result = response.json()
                content = result["content"][0]["text"]
                evaluation = json.loads(content)
                return evaluation

        except Exception as e:
            return self._basic_evaluation(original, transcribed, basic_accuracy)
