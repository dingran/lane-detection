from moviepy.editor import *

clip = (VideoFileClip("test_videos_output/solidYellowLeft.mp4").resize(0.1))
clip.write_gif("showcase2.gif")

clip = (VideoFileClip("test_videos_output/solidWhiteRight.mp4").resize(0.1))
clip.write_gif("showcase1.gif")

clip = (VideoFileClip("test_videos_output/challenge.mp4").resize(0.1))
clip.write_gif("showcase3.gif")


# clip = (VideoFileClip("test_videos_output_DEBUG/challenge.mp4").resize(0.1))
# clip.write_gif("showcase4.gif")
