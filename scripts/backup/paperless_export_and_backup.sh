#!/bin/bash
PAPERLESS_DIR="ASDF"
TARGET_DIR="GHJK"
SOURCE_DIR="${PAPERLESS_DIR}"
LOGFILE="${SOURCE_DIR}export_rsync.log"

## making sure all the directories exist
if [ ! -d  "${TARGET_DIR}" ]; then
  echo Target directory: "'"${TARGET_DIR}"'" does not exits.
  echo Quitting.
  exit
else
  echo Using target directory: "'"${TARGET_DIR}"'".
fi

if [ ! -d  "${PAPERLESS_DIR}" ]; then
  echo Paperless directory: "'"${PAPERLESS_DIR}"'" does not exits.
  echo Quitting.
  exit
else
  echo Using paperless directory: "'"${PAPERLESS_DIR}"'".
fi

if [ ! -d  "${SOURCE_DIR}" ]; then
  echo Source directory: "'"${SOURCE_DIR}"'" does not exits.
  echo Quitting.
  exit
else
  echo Using source directory: "'"${SOURCE_DIR}"'".
fi

## running export of paperless-ngx
(cd "${PAPERLESS_DIR}"
echo "Running the exporter of the paperless-ngx instance"
docker compose exec webserver document_exporter /usr/src/paperless/export --use-filename-format --use-folder-prefix --delete

exec 1> >(tee -a "${LOGFILE}") 2>&1
echo    "=================================="
echo -n "== "
date
echo    "== Synchronizing paperless export"
echo    "== From: '${SOURCE_DIR}'"
echo    "== To:   '${TARGET_DIR}'"
echo    "== -------------------------------"

## this was the command line I used when I was backing up the whole docker volumes
#rsync -av --exclude="consume/" --exclude="export/" --delete "${SOURCE_DIR}" "${TARGET_DIR}"
## this is the command line I use to only backup the exported files or zip file, the config files and the scripts
rsync -av --exclude={"consume/","data/","media/","redisdata/"} --delete "${SOURCE_DIR}" "${TARGET_DIR}"

echo    "== -------------------------------"
echo -n "== "
date
echo    "== Done synchronizing rsync instance"
echo    "=================================="

## now send logfile
exec 1> /dev/null
rsync -av "${LOGFILE}" "${TARGET_DIR}"
