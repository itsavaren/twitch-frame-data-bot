import ffmpeg, streamlink, requests, os

def identify_song(streamer):

    try:
        os.remove('output.mp3')
    except:
        pass

    with open('audd_token.txt') as fp:
        auth_token = fp.read()

    stream_url = streamlink.streams(f'https://www.twitch.tv/{streamer}')['best'].url
    print(stream_url)

    stream = ffmpeg.input(stream_url, t=10)
    stream = ffmpeg.output(stream, 'output.mp3')
    ffmpeg.run(stream)


    data = {
        'api_token': auth_token,
        'return': 'apple_music,spotify',
    }
    files = {
        'file': open('output.mp3', 'rb'),
    }
    result = requests.post('https://api.audd.io/', data=data, files=files)
    result_json = result.json()

    return f"The song playing now is {result_json['result']['artist']} - {result_json['result']['title']}"

