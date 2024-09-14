import openai
import os
import assemblyai as aai
from moviepy.editor import *
from moviepy.video.tools.subtitles import SubtitlesClip

openai.api_key = os.environ['OPENAI_API_KEY']
aai.settings.api_key = os.environ['ASSEMBLYAI_API_KEY']

def generate_script(topic):
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are a professional motivational speaker. Put together words that inspire action and make people feel empowered to do something beyond their abilities. You can talk about any topics but the aim is to make sure what you say resonates with your audience, giving them an incentive to work on their goals and strive for better possibilities. Avoid fancy words, focus on getting the point across. Provide actionable tips that listeners can apply to improve their lives.",
            },
            {
                "role": "user",
                "content": f"Write a script for a motivational youtube channel about {topic}."
            }
        ]
    )

    script = response.choices[0].message.content
    print("Saving script to script.txt")
    with open("script.txt", "w") as f:
        f.write(script)
    f.close()
    print("Script saved to script.txt")

def generate_voiceover(script_file):
    input = open(script_file, "r", encoding="utf-8").read()

    with openai.audio.speech.with_streaming_response.create(
        model="tts-1",
        voice="onyx",
        input=input,
    ) as response:
        print("Saving voiceover to voiceover.mp3")
        response.stream_to_file("voiceover.mp3")
        print("Voiceover saved to voiceover.mp3")

def generate_subtitles():
    transcript = aai.Transcriber().transcribe("voiceover.mp3")
    subtitles = transcript.export_subtitles_srt(
        chars_per_caption=50
    )

    print("Saving subtitles to subtitles.srt")
    with open("subtitles.srt", "w") as f:
        f.write(subtitles)
    f.close()
    print("Subtitles saved to subtitles.srt")

def create_video():
    # Load in voiceover
    voiceover = AudioFileClip("voiceover.mp3")

    # Load in subtitles
    subtitles = SubtitlesClip(
        "subtitles.srt",
        lambda txt: TextClip(
            txt,
            font="Garamond-bold",
            fontsize=24,
            color="white",
        )
    )

    # Load in background video
    background = VideoFileClip("example_background.mp4").subclip(0, voiceover.duration)

    # Combine the voiceover and background
    video_with_voiceover = background.set_audio(voiceover)

    final_clip = CompositeVideoClip([video_with_voiceover, subtitles.set_position(("center", "center"))])

    final_clip.fps = 20

    print("Saving final video to final_video.mp4")
    final_clip.write_videofile("final_video.mp4")
    print("Final video saved to final_video.mp4")

if __name__ == "__main__":
    print("Hello, welcome to Python video creator!")
    topic = input("Step 1: What is the topic of your video? ")

    # Generate and save script
    script = generate_script(topic)

    # Generate and save voiceover
    voiceover = generate_voiceover("script.txt")

    # Generate and save subtitles
    generate_subtitles()
    
    # Create video
    create_video()
