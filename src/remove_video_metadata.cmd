FOR %%i in (..\api\videos\source\*.mp4) DO (
	ffmpeg -i "%%i" -dn -map 0 -c copy -f mp4 -y -map_metadata -1 -fflags +bitexact -flags:v +bitexact -flags:a +bitexact "%%i.tmp_replace"
	MOVE "%%i.tmp_replace" "%%~pni.mp4"
)
