#!/usr/bin/env bash
# My little crappy deploy script
# It will upload all files not ignored by git

files_not_ignored="$(git status --short | grep ^? | cut -d\  -f2- ; git ls-files)"
scp -r $files_not_ignored root@brzeczyszczykiewicz.pvv.ntnu.no:~grzegorz/grzegorz
ssh root@brzeczyszczykiewicz.pvv.ntnu.no systemctl restart grzegorz