FOR /D %%G IN (*) DO (
	pushd %%G
	mkdir extracted
	FOR %%H IN (*.dll) DO (
		ilspycmd -o extracted -p %%H
	)
	popd
)