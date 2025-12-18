"""
Integrated Image Analysis Pipeline with Emotion Detection

Combines emotion detection with multi-model visual analysis.

Emotion Injection Strategy:
- Emotion information is injected at visual analysis stage (GPT/Gemini/Claude)
- Synthesis and anthropomorphic stages inherit emotion info naturally
- Maintains natural flow without over-emphasis
"""

import base64
import os
from typing import Dict, Optional, Union
from pathlib import Path
from openai import OpenAI
import google.generativeai as genai
from anthropic import Anthropic
import PIL.Image
import io
from concurrent.futures import ThreadPoolExecutor, as_completed

# Import Traini AI SDK
from traini_ai.modules import ImageAnalyzerEnsemble
from traini_ai.utils.config import Config


class IntegratedImageAnalysisWithEmotion:
    """
    Integrated Image Analysis Pipeline

    Components:
    - Traini emotion detection
    - Function 1: GPT image analysis (with emotion context)
    - Function 2: Gemini image analysis (with emotion context)
    - Function 3: Claude image analysis (with emotion context)
    - Function 4: Three-model synthesis (objective third-person)
    - Function 10: Anthropomorphic first-person description

    Emotion Injection Strategy:
    - Inject emotion info only at visual analysis stage (Functions 1-3)
    - Later synthesis and anthropomorphic stages inherit naturally
    - Avoids redundant emphasis, maintains natural flow
    """

    def __init__(
        self,
        openai_api_key: str = None,
        google_api_key: str = None,
        anthropic_api_key: str = None,
        use_ensemble: bool = True
    ):
        """
        Initialize analyzer

        Args:
            openai_api_key: OpenAI API key
            google_api_key: Google API key
            anthropic_api_key: Anthropic API key
            use_ensemble: Whether to use ensemble model (default True for higher accuracy)
        """
        # Initialize Traini emotion analyzer
        print("🐕 Initializing Traini Emotion Analyzer...")
        config = Config()
        self.emotion_analyzer = ImageAnalyzerEnsemble(
            config,
            use_ensemble=use_ensemble
        )

        # Initialize OpenAI
        openai_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        if not openai_key:
            raise ValueError(
                "OpenAI API key is required. Provide it via:\n"
                "1. Parameter: IntegratedImageAnalysisWithEmotion(openai_api_key='your-key')\n"
                "2. Environment variable: export OPENAI_API_KEY='your-key'"
            )
        self.openai_client = OpenAI(api_key=openai_key)

        # Initialize Google Gemini
        google_key = google_api_key or os.getenv('GOOGLE_API_KEY')
        if not google_key:
            raise ValueError(
                "Google API key is required. Provide it via:\n"
                "1. Parameter: IntegratedImageAnalysisWithEmotion(google_api_key='your-key')\n"
                "2. Environment variable: export GOOGLE_API_KEY='your-key'"
            )
        genai.configure(api_key=google_key)
        self.gemini_model = genai.GenerativeModel('gemini-2.5-flash-lite')

        # Initialize Anthropic Claude
        anthropic_key = anthropic_api_key or os.getenv('ANTHROPIC_API_KEY')
        if not anthropic_key:
            raise ValueError(
                "Anthropic API key is required. Provide it via:\n"
                "1. Parameter: IntegratedImageAnalysisWithEmotion(anthropic_api_key='your-key')\n"
                "2. Environment variable: export ANTHROPIC_API_KEY='your-key'"
            )
        self.anthropic_client = Anthropic(api_key=anthropic_key)

        self.model_name = 'gpt-4o-mini'

        # Emotion mapping (English to Chinese)
        self.emotion_mapping = {
            'happy': '快乐',
            'relaxed': '放松',
            'sad': '悲伤',
            'angry': '愤怒',
            'fear': '恐惧',
            'anxiety': '焦虑',
            'alert': '警觉',
            'anticipation': '期待',
            'appeasement': '安抚',
            'caution': '谨慎',
            'confident': '自信',
            'curiosity': '好奇',
            'sleepy': '困倦'
        }

    def _detect_emotion(self, image_path: str) -> Dict[str, any]:
        """
        Detect dog emotion using Traini SDK

        Args:
            image_path: Path to image file

        Returns:
            Emotion analysis result dictionary
        """
        print("😊 Detecting dog emotion with Traini AI...")

        result = self.emotion_analyzer.analyze(
            image_path,
            language='zh',
            detail_level='detailed',
            return_confidence=True,
            return_all_predictions=True
        )

        # Get Chinese emotion name
        emotion = result['emotion']
        emotion_zh = self.emotion_mapping.get(emotion, emotion)

        print(f"   Detected: {emotion} ({emotion_zh}) - {result['confidence']:.2%}")

        return {
            'emotion': result['emotion'],
            'emotion_zh': emotion_zh,
            'confidence': result['confidence'],
            'all_predictions': result.get('all_predictions', {}),
            'ensemble_size': result.get('ensemble_size', 1)
        }

    def _load_image_base64(self, image_path: str) -> tuple:
        """
        Load image and convert to base64

        Args:
            image_path: Path to image file

        Returns:
            (base64 encoded image string, media_type)
        """
        import imghdr

        with open(image_path, 'rb') as image_file:
            image_data = image_file.read()
            base64_str = base64.b64encode(image_data).decode('utf-8')

            # Detect image format
            img_type = imghdr.what(None, h=image_data)
            if img_type == 'jpeg':
                media_type = 'image/jpeg'
            elif img_type == 'png':
                media_type = 'image/png'
            elif img_type == 'gif':
                media_type = 'image/gif'
            elif img_type == 'webp':
                media_type = 'image/webp'
            else:
                # Default to jpeg
                media_type = 'image/jpeg'

            return base64_str, media_type

    def _gpt_image_analysis(
        self,
        image_base64: str,
        emotion_info: Optional[Dict] = None
    ) -> str:
        """
        Function 1: GPT image analysis (with optional emotion context)

        Args:
            image_base64: Base64 encoded image
            emotion_info: Emotion detection info (optional)

        Returns:
            GPT analysis result
        """
        print("🤖 Running GPT image analysis...")

        base_prompt = """Please analyze this dog image in detail, focusing on:
1. Physical characteristics (breed, color, size, distinctive features)
2. Posture and body language (ears, tail, facial expression, stance)
3. Behavior and actions
4. Environment and context
5. Overall mood and emotional state

Provide a thorough, objective description."""

        # Add emotion context if available
        if emotion_info:
            emotion_prompt = f"""

IMPORTANT CONTEXT - AI Emotion Detection Result:
Our specialized dog emotion AI has analyzed this image:
- Detected Emotion: {emotion_info['emotion']} ({emotion_info['emotion_zh']})
- Confidence Level: {emotion_info['confidence']:.1%}
- Analysis Method: {emotion_info['ensemble_size']}-model ensemble

Please validate and incorporate this emotion assessment in your analysis."""
            prompt = base_prompt + emotion_prompt
        else:
            prompt = base_prompt

        response = self.openai_client.chat.completions.create(
            model=self.model_name,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ],
            max_tokens=500
        )

        return response.choices[0].message.content

    def _gemini_image_analysis(
        self,
        image_base64: str,
        emotion_info: Optional[Dict] = None
    ) -> str:
        """
        Function 2: Gemini image analysis (with optional emotion context)

        Args:
            image_base64: Base64 encoded image
            emotion_info: Emotion detection info (optional)

        Returns:
            Gemini analysis result
        """
        print("🔍 Running Gemini image analysis...")

        base_prompt = """Analyze this dog image carefully. Describe:
1. The dog's physical appearance and breed characteristics
2. Body language and posture details
3. Facial expression and emotional cues
4. Environmental context
5. Overall behavioral state"""

        # Add emotion context if available
        if emotion_info:
            emotion_prompt = f"""

EMOTION DETECTION CONTEXT:
AI analysis detected: {emotion_info['emotion']} ({emotion_info['emotion_zh']})
Confidence: {emotion_info['confidence']:.1%}
Models used: {emotion_info['ensemble_size']}

Please consider this emotion assessment in your analysis."""
            prompt = base_prompt + emotion_prompt
        else:
            prompt = base_prompt

        # Convert base64 to PIL Image for Gemini
        image_data = base64.b64decode(image_base64)
        image = PIL.Image.open(io.BytesIO(image_data))

        # Generate content
        result = self.gemini_model.generate_content([prompt, image])

        return result.text

    def _claude_image_analysis(
        self,
        image_base64: str,
        media_type: str = 'image/jpeg',
        emotion_info: Optional[Dict] = None
    ) -> str:
        """
        Function 3: Claude image analysis (with optional emotion context)

        Args:
            image_base64: Base64 encoded image
            media_type: Image media type (e.g. 'image/jpeg', 'image/png')
            emotion_info: Emotion detection info (optional)

        Returns:
            Claude analysis result
        """
        print("🧠 Running Claude image analysis...")

        base_prompt = """Please analyze the image carefully, focusing specifically on:
1. The environmental context (e.g., indoor/outdoor, furniture, weather, ground texture, lighting conditions, and any visible objects).
2. Precise behaviors and posture of the dog(s) (e.g., tail position, ear posture, mouth expression, paw positioning, interaction with objects or humans, specific gaze direction).
3. Emotional or behavioral implications based on these observed details.
Provide a detailed, structured response highlighting your observations and interpretations."""

        # Add emotion context if available
        if emotion_info:
            emotion_prompt = f"""

IMPORTANT CONTEXT - AI Emotion Detection Result:
Our specialized dog emotion AI has analyzed this image:
- Detected Emotion: {emotion_info['emotion']} ({emotion_info['emotion_zh']})
- Confidence Level: {emotion_info['confidence']:.1%}
- Analysis Method: {emotion_info['ensemble_size']}-model ensemble

Please validate this emotion assessment with the visual cues you observe and provide a comprehensive analysis."""
            prompt = base_prompt + emotion_prompt
        else:
            prompt = base_prompt

        response = self.anthropic_client.messages.create(
            model='claude-3-haiku-20240307',
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": image_base64
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ]
        )

        return response.content[0].text

    def _synthesize_three_models(
        self,
        gpt_answer: str,
        gemini_answer: str,
        claude_answer: str
    ) -> str:
        """
        Function 4: Three-model synthesis

        Args:
            gpt_answer: GPT analysis result (already contains emotion info)
            gemini_answer: Gemini analysis result (already contains emotion info)
            claude_answer: Claude analysis result (already contains emotion info)

        Returns:
            Synthesized analysis (objective third-person description)
        """
        print("📊 Synthesizing results from three models...")

        system_prompt = """You are an expert dog behavior analyst. Your task is to synthesize multiple AI model analyses into a single, comprehensive objective description."""

        user_prompt = f"""Below are three AI model analyses of the same dog image:

[Analysis 1 - Claude] {claude_answer}
[Analysis 2 - Gemini] {gemini_answer}
[Analysis 3 - GPT] {gpt_answer}

Task: Synthesize these three analyses into ONE coherent paragraph using THIRD-PERSON OBJECTIVE perspective.

Requirements:
1. Use third-person perspective ONLY (e.g., "The dog is...", "It appears...", "The dog seems...")
2. Include: physical characteristics, posture, body language, behavior, environment, and emotional state
3. Reconcile any conflicting details intelligently
4. Make it flowing and natural (one detailed paragraph)
5. Be objective and descriptive

Output the synthesized paragraph now:"""

        response = self.openai_client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=400
        )

        return response.choices[0].message.content

    def _anthropomorphic_first_person(
        self,
        intention: str
    ) -> str:
        """
        Function 10: Anthropomorphic first-person description

        Args:
            intention: Pet intention/state description (already contains emotion info)

        Returns:
            Anthropomorphic first-person description
        """
        print("💬 Generating anthropomorphic first-person description...")

        style_guide = """You are expressing the dog's feelings in first person.

Style requirements:
- Choose the appropriate tone based on the emotional context in the input:
  - If happy/playful: Humorous, energetic
  - If sad/anxious: Gentle, vulnerable
  - If angry: Frustrated but cute
  - If relaxed: Calm, content
  - If alert/curious: Excited, inquisitive
- Add adj/adv onto verbs and nouns: to be vivid, expressive, emotive, intimate, anthropomorphic (human-like), exaggerated and dialogue-vibe.
- Use 1-2 onomatopoeias to add playful sound effects: to make it sound extra endearing!
- Grammar doesn't always have to be correct.
- Use spoken English, Internet slang or meme language. You would be punished $1000 for any jargon or difficult word.
- Add 1-2 emoji that match the emotion.
- Use '!', '~','...' for emphasis.
- Mimic/quote famous characters' words if there is a similar scenario as in the movies, cartoons or fictions.
- Adjust paragraph length based on detail granularity of the input, but in total no more than 6 sentences or 100 words.
- MOST IMPORTANT: Make sure the tone and content naturally reflect the emotion expressed in the input."""

        user_prompt = f"""This is the dog's current state and intention:
{intention}

Please describe the dog's needs in the first person, making sure the emotion is clearly expressed through the tone and words."""

        response = self.openai_client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": style_guide},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=300
        )

        return response.choices[0].message.content

    def analyze_image(self, image_path: str) -> Dict[str, str]:
        """
        Complete image analysis pipeline (with emotion detection)

        Pipeline:
        0. Use Traini SDK to detect emotion
        1. Load image
        2. Run GPT, Gemini, Claude analysis (with emotion context injected)
        3. Synthesize three model results (emotion info already embedded)
        4. Generate anthropomorphic first-person description (based on synthesis with emotion)

        Note: Emotion info is injected only at step 2 (visual analysis stage).
              Steps 3 and 4 naturally inherit emotion info, no redundant injection.

        Args:
            image_path: Path to image file

        Returns:
            Dictionary containing:
            - third_person_description: Objective third-person analysis
            - first_person_description: Anthropomorphic first-person narrative
        """
        print(f"\n🐕 Starting integrated image analysis with emotion detection\n")
        print(f"📸 Image: {image_path}\n")

        # Step 0: Traini emotion detection
        print("=" * 60)
        print("STEP 0: Emotion Detection (Traini AI)")
        print("=" * 60)
        emotion_info = self._detect_emotion(image_path)

        # Step 1: Load image
        print("\n📸 Loading image...")
        image_base64, media_type = self._load_image_base64(image_path)

        # Step 2: Run three model analyses in parallel (inject emotion info)
        print("\n" + "=" * 60)
        print("STEP 1-3: Three-Model Visual Analysis (Parallel Execution)")
        print("=" * 60)

        # Use ThreadPoolExecutor to run all three models in parallel
        with ThreadPoolExecutor(max_workers=3) as executor:
            # Submit all three tasks
            future_gpt = executor.submit(
                self._gpt_image_analysis,
                image_base64,
                emotion_info
            )
            future_gemini = executor.submit(
                self._gemini_image_analysis,
                image_base64,
                emotion_info
            )
            future_claude = executor.submit(
                self._claude_image_analysis,
                image_base64,
                media_type,
                emotion_info
            )

            # Wait for all results
            gpt_answer = future_gpt.result()
            gemini_answer = future_gemini.result()
            claude_answer = future_claude.result()

        # Step 3: Synthesis
        print("\n" + "=" * 60)
        print("STEP 4: Synthesizing Results")
        print("=" * 60)
        synthesis_result = self._synthesize_three_models(
            gpt_answer,
            gemini_answer,
            claude_answer
        )

        # Step 4: Anthropomorphic description
        print("\n" + "=" * 60)
        print("STEP 5: Anthropomorphic Description")
        print("=" * 60)
        anthropomorphic_result = self._anthropomorphic_first_person(
            synthesis_result
        )

        print("\n✅ Analysis complete!\n")

        # Return only third-person and first-person descriptions
        return {
            'third_person_description': synthesis_result,
            'first_person_description': anthropomorphic_result
        }


def main():
    """
    Example usage
    """
    # Initialize analyzer
    analyzer = IntegratedImageAnalysisWithEmotion(use_ensemble=True)

    # Example image path (update with your image)
    image_path = '/Users/pengchenghong/Downloads/dog_emotion_balanced/test/happy/test_0001.jpg'

    # Run analysis
    print("\n" + "=" * 80)
    print("🐕 TRAINI AI - INTEGRATED IMAGE ANALYSIS")
    print("=" * 80)

    results = analyzer.analyze_image(image_path)

    # Display results
    print("\n" + "=" * 80)
    print("📊 RESULTS")
    print("=" * 80)

    print("\n📝 THIRD-PERSON DESCRIPTION:")
    print("=" * 80)
    print(results['third_person_description'])

    print("\n" + "=" * 80)
    print("💭 FIRST-PERSON DESCRIPTION:")
    print("=" * 80)
    print(results['first_person_description'])


if __name__ == '__main__':
    main()
