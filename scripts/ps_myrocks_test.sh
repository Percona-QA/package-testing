#!/usr/bin/env bash

LOGFILE=""

# Check for RocksDB log file
if [ -f /var/lib/mysql/.rocksdb/LOG ]; then
  LOGFILE="/var/lib/mysql/.rocksdb/LOG"
else
  echo "Can't find RocksDB LOG file!"
  exit 1
fi

# Check CPU architecture
arch=$(uname -m)
if [ "${arch}" != "x86_64" ]; then
  echo "Unsupported architecture: ${arch}. Skipping CRC test."
  exit 0
else
  echo "Architecture is x86_64. Proceeding with CRC test."
fi

# Check if FastCRC32 is enabled
fastcrc=$(grep -c "Fast CRC32 supported: Supported on x86" "${LOGFILE}")
if [ ${fastcrc} -eq 0 ]; then
  echo "Fast CRC32 doesn't seem to be enabled."
  exit 1
else
  echo "Fast CRC32 seems to be enabled."
fi
