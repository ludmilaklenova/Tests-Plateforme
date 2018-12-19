#!/bin/sh
#
#	This script checks if  CPP package has a correct content
#----------------------------------------------------------------------------


# Deployment directory
DEPLOY_DIR=/usr/LocalTESTING/prerelease/CPP

for dir in 'win32' 'linux' 'linux/lib'
do
	DIR_CHECK=$DEPLOY_DIR/$dir
	if [ ! -d "$DIR_CHECK" ] || [ `ls -A "$DIR_CHECK" | wc -c` -eq 0 ]; then
		echo "$DIR_CHECK directory does not exists or is empty. Package structure invalid"
		exit 1
fi

done

echo "Package Cpp Valide" 
exit 0
