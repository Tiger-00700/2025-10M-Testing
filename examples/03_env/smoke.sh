#!/usr/bin/env bash
echo "[smoke stub] examples/03_env smoke"
if command -v docker >/dev/null 2>&1; then
  echo "docker: available"
else
  echo "docker: not found"
fi
if [ -f docker-compose.yml ] || [ -f docker-compose.yaml ]; then
  echo "docker-compose file present (stub will not bring up services)"
else
  echo "no docker-compose in this example; this is a stub"
fi
echo "NO_SMOKE_IMPLEMENTED"
exit 0
