:: Use ffmpeg to trim video

:: -i: This specifies the input file. In that case, it is (input.mp4).
:: -ss: Used with -i, this seeks in the input file (input.mp4) to position.
:: 00:01:00: This is the time your trimmed video will start with.
:: -to: This specifies duration from start (00:01:00) to end (00:02:00).
:: -t: Use duration instead or end time
:: 00:02:00: This is the time your trimmed video will end with.
:: -c copy: This is an option to trim via stream copy. (NB: Very fast but loss of keyframes)
:: -async 1: re-encode to create keyframe at start time (slower)


ffmpeg -i input.mp4 -ss 00:08:41 -to 00:09:58 -async 1 demo.mp4