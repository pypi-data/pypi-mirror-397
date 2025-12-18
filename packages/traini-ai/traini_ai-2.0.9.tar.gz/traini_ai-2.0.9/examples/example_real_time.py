"""
Real-time audio processing example
"""

from dog_emotion_sdk import DogEmotionClient
import time


def simulate_real_time_processing():
    """
    Simulate real-time dog sound monitoring and translation
    """
    print("=" * 60)
    print("Real-time Dog Sound Monitoring")
    print("=" * 60)

    client = DogEmotionClient()

    # Simulate audio stream chunks
    # In real implementation, this would be live audio capture
    audio_chunks = [
        "bark_sample_1.wav",
        "whine_sample_2.wav",
        "growl_sample_3.wav",
    ]

    print("\nMonitoring dog sounds...")
    print("(Press Ctrl+C to stop)\n")

    try:
        for i, audio_chunk in enumerate(audio_chunks):
            print(f"[{time.strftime('%H:%M:%S')}] Processing audio chunk {i+1}...")

            try:
                # Translate dog sound
                result = client.translate_dog_to_human(
                    audio_chunk,
                    detail_level='simple'
                )

                print(f"  Sound Type: {result.get('sound_type', 'unknown')}")
                print(f"  Emotion: {result.get('emotion', 'unknown')}")
                print(f"  Interpretation: {result['text']}")
                print()

                # Alert on specific emotions
                emotion = result.get('emotion', '')
                if emotion in ['pain', 'distress', 'anxious']:
                    print("  ⚠️  ALERT: Dog may need attention!")
                    print()

            except Exception as e:
                print(f"  Error: {e}\n")

            # Simulate delay
            time.sleep(2)

    except KeyboardInterrupt:
        print("\nStopped monitoring.")


def main():
    simulate_real_time_processing()


if __name__ == "__main__":
    main()
