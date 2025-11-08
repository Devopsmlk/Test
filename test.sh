#!/bin/bash

echo "=== Testing Qashqade API ==="
echo ""

echo "1. Testing /api/health"
curl -s http://localhost:4004/api/health | jq
echo ""

echo "2. Testing /api/mirror with fOoBar25"
curl -s "http://localhost:4004/api/mirror?word=fOoBar25" | jq
echo ""

echo "3. Testing /api/mirror with Hello"
curl -s "http://localhost:4004/api/mirror?word=Hello" | jq
echo ""

echo "4. Testing /api/mirror with World123"
curl -s "http://localhost:4004/api/mirror?word=World123" | jq
echo ""

echo "5. Testing /api/mirror with ABC"
curl -s "http://localhost:4004/api/mirror?word=ABC" | jq
echo ""

echo "=== Tests Complete ==="
echo ""
echo "Now verify in database:"
echo "docker exec -it qashqade-postgres psql -U postgres -d qashqade -c \"SELECT * FROM word_transformations;\""