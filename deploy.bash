#!/usr/bin/env bash
# My little crappy deploy script
# Uploads all files not ignored by git

TARGET=grzegorz@brzeczyszczykiewicz.pvv.ntnu.no
TARGET_PATH='grzegorz'

array=(); while IFS= read -rd '' item; do array+=("$item"); done < \
	<(git status -z --short | grep -z ^? | cut -z -d\  -f2-; git ls-files -z)
files_not_ignored=("${array[@]}")

ssh -T "$TARGET" "
	mv -v '$TARGET_PATH/config.py' /tmp/grzegorz_config.py
	rm -rfv $TARGET_PATH
	mkdir -pv $TARGET_PATH
	mv -v /tmp/grzegorz_config.py '$TARGET_PATH/config.py'
	"

echo '== Copying files to target: =='
tar -c "${files_not_ignored[@]}" |
	ssh -T "$TARGET" "
	tar -vxC $TARGET_PATH
	"
echo '== DONE: =='

ssh -T "$TARGET" "
	systemctl --user restart grzegorz@0
	"

sleep 1

ssh -T "$TARGET" "
	systemctl --user status grzegorz@0
	"
