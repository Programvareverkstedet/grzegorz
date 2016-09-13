#!/usr/bin/env bash
# My little crappy deploy script
# It will upload all files not ignored by git

files_not_ignored="$(git status --short | grep ^? | cut -d\  -f2- ; git ls-files)"
tar -c $files_not_ignored | ssh grzegorz@brzeczyszczykiewicz.pvv.ntnu.no tar -xC ~grzegorz/grzegorz
ssh root@brzeczyszczykiewicz.pvv.ntnu.no "systemctl restart grzegorz"
