"""
Advanced usage examples for Dog Emotion SDK
"""

from dog_emotion_sdk import (
    DogEmotionClient,
    ImageAnalyzer,
    VideoAnalyzer,
    HumanToDogTranslator,
    DogToHumanTranslator
)
from dog_emotion_sdk.utils.config import Config
import os


def example_individual_modules():
    """Example using individual modules directly"""
    print("\n" + "=" * 60)
    print("Using Individual Modules")
    print("=" * 60)

    # Create custom config
    config = Config(
        api_key=os.getenv("DOG_EMOTION_API_KEY"),
        image_model="custom-model-v2",
        verbose=True,
        sample_rate=22050
    )

    # Use ImageAnalyzer directly
    print("\nUsing ImageAnalyzer module directly:")
    image_analyzer = ImageAnalyzer(config)
    result = image_analyzer.analyze(
        "path/to/dog.jpg",
        language='zh',
        detail_level='detailed'
    )
    print(f"Result: {result['text']}")


def example_batch_processing():
    """Example of batch processing multiple files"""
    print("\n" + "=" * 60)
    print("Batch Processing Multiple Images")
    print("=" * 60)

    client = DogEmotionClient()

    # List of image files
    image_files = [
        "dog1.jpg",
        "dog2.jpg",
        "dog3.jpg",
    ]

    results = []
    for image_file in image_files:
        try:
            result = client.analyze_image(
                image_file,
                return_confidence=True
            )
            results.append({
                'file': image_file,
                'emotion': result.get('emotion'),
                'confidence': result.get('confidence'),
                'text': result['text']
            })
        except Exception as e:
            print(f"Error processing {image_file}: {e}")

    # Summary
    print("\nBatch Processing Results:")
    for r in results:
        print(f"- {r['file']}: {r['emotion']} ({r['confidence']:.2f})")


def example_custom_configuration():
    """Example with custom configuration"""
    print("\n" + "=" * 60)
    print("Custom Configuration")
    print("=" * 60)

    # Create client with custom settings
    client = DogEmotionClient(
        config={
            'verbose': True,
            'timeout': 60,
            'max_retries': 5,
            'audio_format': 'mp3',
            'sample_rate': 44100,
            # Custom parameters
            'use_gpu': True,
            'batch_size': 32,
        }
    )

    print(f"Config: {client.config.to_dict()}")


def example_error_handling():
    """Example with proper error handling"""
    print("\n" + "=" * 60)
    print("Error Handling")
    print("=" * 60)

    from dog_emotion_sdk.utils.exceptions import (
        InvalidInputError,
        ProcessingError,
        APIError
    )

    client = DogEmotionClient()

    # Handle invalid input
    try:
        result = client.analyze_image("nonexistent_file.jpg")
    except InvalidInputError as e:
        print(f"Input validation error: {e}")
    except ProcessingError as e:
        print(f"Processing error: {e}")
    except APIError as e:
        print(f"API error (status {e.status_code}): {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


def example_save_outputs():
    """Example saving audio outputs to files"""
    print("\n" + "=" * 60)
    print("Saving Audio Outputs")
    print("=" * 60)

    client = DogEmotionClient()

    # Analyze image and save audio
    result = client.analyze_image("dog.jpg")

    # Save audio output
    output_path = "output_narration.wav"
    with open(output_path, 'wb') as f:
        f.write(result['audio'])
    print(f"Audio saved to: {output_path}")

    # Translate and save
    translation = client.translate_human_to_dog("command.wav")
    dog_audio_path = "dog_optimized_command.wav"
    with open(dog_audio_path, 'wb') as f:
        f.write(translation['audio'])
    print(f"Dog-optimized audio saved to: {dog_audio_path}")


def example_video_timeline_analysis():
    """Example analyzing video with timeline"""
    print("\n" + "=" * 60)
    print("Video Timeline Analysis")
    print("=" * 60)

    client = DogEmotionClient()

    result = client.analyze_video(
        "dog_playing.mp4",
        sample_rate=1,  # 1 frame per second
        return_timeline=True
    )

    print(f"Overall: {result['text']}")
    print(f"\nEmotion Timeline:")

    if 'timeline' in result:
        for entry in result['timeline']:
            timestamp = entry['timestamp']
            emotion = entry['emotion']
            confidence = entry.get('confidence', 0)
            print(f"  {timestamp:.1f}s: {emotion} ({confidence:.2f})")


def main():
    """Run all advanced examples"""
    example_individual_modules()
    example_batch_processing()
    example_custom_configuration()
    example_error_handling()
    example_save_outputs()
    example_video_timeline_analysis()


if __name__ == "__main__":
    main()
