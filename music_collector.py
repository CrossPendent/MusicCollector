import chart_crawler as cc
import youtube_explorer as ye

IMAGE_DIR = 'cover_img'
MUSIC_FILE_DIR = 'music_files'

def main():
  chart = cc.getMelonChart()
  for song in chart:
    ye.getSongFromYouTube(song.artist, song.title, song.songID, song.lyric, song.albumInfo)

if __name__ == '__main__':
  main()