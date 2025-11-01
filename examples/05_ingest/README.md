# 05_ingest

Ingest examples used by Chapter 5 (数据采集). This folder contains quick smoke checks and minimal scaffolding for data ingestion scenarios.

## Contents

- smoke.sh — quick smoke test script for ingestion pipeline checks
- .skeleton/ — placeholder for extended examples or templates

## How to run

- Bash (Linux/macOS/Wsl):

  ./smoke.sh

- PowerShell (Windows):

  pwsh -NoProfile -ExecutionPolicy Bypass -File ./smoke.sh

## Notes

- Scripts are intentionally minimal; adjust endpoints/paths as needed for your environment.
- Pair with the book's guidance for backpressure and drop simulation scenarios.
