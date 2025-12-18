"""
Basic usage examples for Dog Emotion SDK
"""

from dog_emotion_sdk import DogEmotionClient


def main():
    # Initialize the client
    # You can provide API key if using cloud services
    client = DogEmotionClient(
        api_key="your_api_key_here",  # Optional
        config={
            'verbose': True,
            'timeout': 30
        }
    )

    print("=" * 60)
    print("Dog Emotion SDK - Basic Usage Examples")
    print("=" * 60)

    # Example 1: Analyze dog emotion from image
    print("\n1. Image Analysis")
    print("-" * 40)
    try:
        result = client.analyze_image(
            "path/to/dog_image.jpg",
            language='en',
            detail_level='detailed',
            return_confidence=True
        )
        print(f"Text: {result['text']}")
        print(f"Emotion: {result.get('emotion', 'N/A')}")
        print(f"Confidence: {result.get('confidence', 'N/A')}")
        print(f"Audio data length: {len(result['audio'])} bytes")
    except Exception as e:
        print(f"Error: {e}")

    # Example 2: Analyze dog emotion from video
    print("\n2. Video Analysis")
    print("-" * 40)
    try:
        result = client.analyze_video(
            "path/to/dog_video.mp4",
            sample_rate=2,  # Sample 2 frames per second
            aggregate_method='dominant',
            return_timeline=True
        )
        print(f"Text: {result['text']}")
        print(f"Dominant emotion: {result.get('dominant_emotion', 'N/A')}")
        if 'timeline' in result:
            print(f"Timeline entries: {len(result['timeline'])}")
    except Exception as e:
        print(f"Error: {e}")

    # Example 3: Translate human speech to dog
    print("\n3. Human to Dog Translation")
    print("-" * 40)
    try:
        result = client.translate_human_to_dog(
            "path/to/human_speech.wav",
            tone='friendly',
            include_transcription=True
        )
        print(f"Text: {result['text']}")
        print(f"Transcription: {result.get('transcription', 'N/A')}")
        print(f"Audio data length: {len(result['audio'])} bytes")
    except Exception as e:
        print(f"Error: {e}")

    # Example 4: Translate dog sounds to human
    print("\n4. Dog to Human Translation")
    print("-" * 40)
    try:
        result = client.translate_dog_to_human(
            "path/to/dog_bark.wav",
            language='en',
            detail_level='detailed',
            include_sound_type=True
        )
        print(f"Text: {result['text']}")
        print(f"Sound type: {result.get('sound_type', 'N/A')}")
        print(f"Emotion: {result.get('emotion', 'N/A')}")
        print(f"Context: {result.get('context', 'N/A')}")
    except Exception as e:
        print(f"Error: {e}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
