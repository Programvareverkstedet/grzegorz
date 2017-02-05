#!/usr/bin/env bash
# My little crappy deploy script
# Uploads all files not ignored by git

TARGET=brzeczyszczykiewicz.pvv.ntnu.no
TARGET_PATH='grzegorz'

array=(); while IFS= read -rd '' item; do array+=("$item"); done < \
	<(git status -z --short | grep -z ^? | cut -z -d\  -f2-; git ls-files -z)
files_not_ignored=("${array[@]}")

ssh -T "grzegorz@$TARGET" "
	rm -rf $TARGET_PATH
	mkdir -p $TARGET_PATH
	"

tar -c "${files_not_ignored[@]}" |
	ssh -T "grzegorz@$TARGET" "
	tar -vxC $TARGET_PATH
	"
ssh -T "root@$TARGET" "
	systemctl restart grzegorz
	systemctl status grzegorz
	"
