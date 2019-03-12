#!/bin/bash
if [[ -n "$1" ]]; then
	exec 6>&1
	exec 1>$1
fi
version=$(python -V 2>&1 | grep -Po '(?<=Python )(.+)')
echo python $version
if [[ $version = 2* ]]; then
  python3 -m prospector supertool --profile-path=.prospector.yml
else
  python  -m prospector supertool --profile-path=.prospector.yml
fi
code=$? 
if [ $code != 0 ]; then
	if [[ -n "$1" ]]; then
		exec 1>&6 6>&-
		details='Details in '
	fi
  echo Static code analysis failed.  $details $1
fi
exit $code