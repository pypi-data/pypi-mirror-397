"""
LLM Client module for Gemini and Groq API integrations
"""

import json
import re
from typing import Optional, Dict, Any, List
from abc import ABC, abstractmethod

from pragyan.models import LLMProvider, LLMConfig, Question, Solution, ProgrammingLanguage


def _clean_and_parse_json(response: str) -> Dict[str, Any]:
    """
    Clean LLM response and parse as JSON with robust error handling.
    Handles control characters, markdown code blocks, and common issues.
    """
    # Strip whitespace
    response = response.strip()
    
    # Remove markdown code blocks
    if response.startswith("```json"):
        response = response[7:]
    if response.startswith("```"):
        response = response[3:]
    if response.endswith("```"):
        response = response[:-3]
    
    response = response.strip()
    
    # Try parsing as-is first
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        pass
    
    # Remove control characters except for those inside strings
    # First, find the first { and last }
    start_idx = response.find('{')
    end_idx = response.rfind('}')
    
    if start_idx == -1 or end_idx == -1:
        # Try to find array brackets
        start_idx = response.find('[')
        end_idx = response.rfind(']')
    
    if start_idx != -1 and end_idx != -1:
        response = response[start_idx:end_idx + 1]
    
    # Replace problematic control characters within string values
    # Handle unescaped newlines and tabs in strings
    def escape_string_content(match):
        content = match.group(1)
        # Escape control characters
        content = content.replace('\n', '\\n')
        content = content.replace('\r', '\\r')
        content = content.replace('\t', '\\t')
        content = content.replace('\b', '\\b')
        content = content.replace('\f', '\\f')
        return f'"{content}"'
    
    # This regex finds string values and escapes control chars inside them
    try:
        # First attempt: try to fix common issues
        cleaned = response
        
        # Replace literal newlines that might be in the middle of strings
        # by using a more aggressive approach
        cleaned = re.sub(r'(?<!\\)\n(?=.*?")', '\\n', cleaned)
        cleaned = re.sub(r'(?<!\\)\r(?=.*?")', '\\r', cleaned)
        cleaned = re.sub(r'(?<!\\)\t(?=.*?")', '\\t', cleaned)
        
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass
    
    # More aggressive cleaning: remove all control characters
    try:
        # Remove all control characters except spaces
        cleaned = ''.join(char if ord(char) >= 32 or char in '\n\r\t' else ' ' for char in response)
        # Then normalize whitespace within strings
        cleaned = re.sub(r'\s+', ' ', cleaned)
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass
    
    # Last resort: try to extract and rebuild JSON manually
    try:
        # Very aggressive: just keep valid JSON characters
        cleaned = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', response)
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse JSON response: {str(e)}\nResponse was: {response[:500]}...")


class BaseLLMClient(ABC):
    """Abstract base class for LLM clients"""
    
    def __init__(self, config: LLMConfig):
        self.config = config
    
    @abstractmethod
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate a response from the LLM"""
        pass
    
    @abstractmethod
    def generate_json(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """Generate a JSON response from the LLM"""
        pass


class GeminiClient(BaseLLMClient):
    """Client for Google Gemini API"""
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        try:
            import google.generativeai as genai
            genai.configure(api_key=config.api_key)
            
            generation_config = genai.GenerationConfig(
                temperature=config.temperature,
                max_output_tokens=config.max_tokens,
            )
            
            # Ensure model name is set
            model_name = config.model or "gemini-2.0-flash"
            
            self.model = genai.GenerativeModel(
                model_name=model_name,
                generation_config=generation_config,
            )
        except ImportError:
            raise ImportError("Please install google-generativeai: pip install google-generativeai")
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate a response using Gemini"""
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        
        response = self.model.generate_content(full_prompt)
        return response.text
    
    def generate_json(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """Generate a JSON response using Gemini"""
        json_prompt = f"{prompt}\n\nRespond ONLY with valid JSON, no markdown code blocks or extra text."
        response = self.generate(json_prompt, system_prompt)
        
        return _clean_and_parse_json(response)


class GroqClient(BaseLLMClient):
    """Client for Groq API"""
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        try:
            from groq import Groq
            self.client = Groq(api_key=config.api_key)
        except ImportError:
            raise ImportError("Please install groq: pip install groq")
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate a response using Groq"""
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        # Ensure model name is set
        model_name = self.config.model or "llama-3.3-70b-versatile"
        
        response = self.client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
        )
        
        content = response.choices[0].message.content
        return content if content else ""
    
    def generate_json(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """Generate a JSON response using Groq"""
        json_system = system_prompt or ""
        json_system += "\nYou must respond ONLY with valid JSON, no markdown code blocks or extra text."
        
        response = self.generate(prompt, json_system)
        
        return _clean_and_parse_json(response)


class LLMClient:
    """Factory class for creating LLM clients"""
    
    def __init__(self, provider: str, api_key: str, model: Optional[str] = None):
        """
        Initialize LLM client
        
        Args:
            provider: Either "gemini" or "groq"
            api_key: API key for the provider
            model: Optional model name override
        """
        llm_provider = LLMProvider(provider.lower())
        self.config = LLMConfig(provider=llm_provider, api_key=api_key, model=model)
        
        if llm_provider == LLMProvider.GEMINI:
            self.client = GeminiClient(self.config)
        elif llm_provider == LLMProvider.GROQ:
            self.client = GroqClient(self.config)
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate a response"""
        return self.client.generate(prompt, system_prompt)
    
    def generate_json(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """Generate a JSON response"""
        return self.client.generate_json(prompt, system_prompt)
    
    def analyze_question(self, question: Question) -> Dict[str, Any]:
        """Analyze a DSA question and extract key information"""
        system_prompt = """You are an expert DSA instructor and competitive programmer. 
Analyze the given problem and extract key information about the concepts, approach, and solution strategy."""
        
        prompt = f"""Analyze this DSA problem and provide detailed insights:

{question.to_prompt()}

Provide your analysis in the following JSON format:
{{
    "title": "Problem title",
    "difficulty": "Easy/Medium/Hard",
    "topics": ["array", "dynamic programming", etc.],
    "main_concept": "The primary concept/technique needed",
    "sub_concepts": ["related concepts"],
    "approach": "Brief description of the approach",
    "intuition": "Why this approach works",
    "edge_cases": ["edge cases to consider"],
    "similar_problems": ["names of similar problems"]
}}"""
        
        return self.generate_json(prompt, system_prompt)
    
    def generate_solution(
        self, 
        question: Question, 
        language: ProgrammingLanguage,
        analysis: Optional[Dict[str, Any]] = None
    ) -> Solution:
        """Generate a complete solution for the DSA question"""
        system_prompt = """You are an expert competitive programmer and coding instructor.
Generate clean, efficient, and well-documented code solutions.
Always include detailed comments explaining the logic."""
        
        lang_name = language.value
        
        prompt = f"""Generate a complete solution for this DSA problem in {lang_name}:

{question.to_prompt()}

{"Analysis context: " + json.dumps(analysis) if analysis else ""}

Provide your solution in the following JSON format:
{{
    "code": "The complete, working code solution with comments",
    "explanation": "Detailed explanation of the solution",
    "time_complexity": "O(?) with explanation",
    "space_complexity": "O(?) with explanation",
    "concept": "Main concept/technique used",
    "approach": "Step-by-step approach description",
    "step_by_step": ["Step 1: ...", "Step 2: ...", ...],
    "example_walkthrough": "Detailed walkthrough of Example 1 showing how the algorithm works"
}}

Make sure the code is complete, syntactically correct, and follows best practices for {lang_name}."""
        
        result = self.generate_json(prompt, system_prompt)
        
        return Solution(
            code=result.get("code", ""),
            language=language,
            explanation=result.get("explanation", ""),
            time_complexity=result.get("time_complexity", ""),
            space_complexity=result.get("space_complexity", ""),
            concept=result.get("concept", ""),
            approach=result.get("approach", ""),
            step_by_step=result.get("step_by_step", []),
            example_walkthrough=result.get("example_walkthrough", ""),
        )
    
    def generate_video_script(
        self, 
        question: Question, 
        solution: Solution,
        analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate a script for the explanation video"""
        system_prompt = """You are an expert at creating educational content for programming tutorials.
Create engaging, clear, and well-structured video scripts that explain DSA concepts effectively."""
        
        prompt = f"""Create a detailed video script for explaining this DSA problem and its solution:

PROBLEM:
{question.to_prompt()}

SOLUTION:
Language: {solution.language.value}
Code:
{solution.code}

Concept: {solution.concept}
Approach: {solution.approach}
Time Complexity: {solution.time_complexity}
Space Complexity: {solution.space_complexity}

ANALYSIS:
{json.dumps(analysis, indent=2)}

Create a video script with the following scenes in JSON format:
{{
    "scenes": [
        {{
            "scene_type": "intro",
            "title": "Scene title",
            "narration": "What to explain in this scene",
            "visual_elements": ["list of visual elements to show"],
            "duration": 5,
            "animations": ["fade_in", "highlight", etc.]
        }},
        ...
    ]
}}

Include these scenes:
1. intro - Problem introduction
2. concept - Explain the main concept/technique
3. approach - Explain the approach/intuition
4. code - Show and explain the code
5. example - Walkthrough with an example
6. complexity - Explain time and space complexity
7. outro - Summary and tips

Each scene should have clear narration and visual elements that support the explanation."""
        
        result = self.generate_json(prompt, system_prompt)
        return result.get("scenes", [])
    
    def generate_manim_code(self, scene: Dict[str, Any], question: Question, solution: Solution) -> str:
        """Generate Manim code for a specific scene"""
        system_prompt = """You are an expert at creating Manim animations for educational videos.
Generate clean, working Manim Community Edition code that creates beautiful animations."""
        
        prompt = f"""Generate Manim CE code for this scene:

Scene: {json.dumps(scene, indent=2)}

Context:
- Problem: {question.title}
- Concept: {solution.concept}
- Code Language: {solution.language.value}

Generate a complete Manim scene class that:
1. Creates visually appealing animations
2. Shows text, code, and diagrams as needed
3. Uses appropriate animations (Write, FadeIn, Transform, etc.)
4. Has proper timing and pacing

Return ONLY the Python code for the Manim scene class, no explanation.
The class should inherit from Scene and have a construct method.
Use manim.community edition syntax."""

        return self.generate(prompt, system_prompt)
