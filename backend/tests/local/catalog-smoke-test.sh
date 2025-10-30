#!/bin/bash

# Catalog SKU List - Smoke Test
# Tests the DDD pilot route GET /store/catalog/skus

BASE_URL="${BASE_URL:-http://localhost:9000}"
ENDPOINT="$BASE_URL/store/catalog/skus"

echo "====================================="
echo "Catalog SKU List - Smoke Test"
echo "====================================="
echo ""
echo "Testing endpoint: $ENDPOINT"
echo ""

# Test 1: Basic list (first page)
echo "[Test 1] Basic list (limit=10)"
curl -s "$ENDPOINT?limit=10" | jq -r '
  "Status: \(.success // false)",
  "Items count: \(.data.skus | length)",
  "Total: \(.data.pagination.total)",
  "Has more: \(.data.pagination.hasMore)"
'
echo ""

# Test 2: Pagination (page 2)
echo "[Test 2] Pagination (page=2, limit=5)"
curl -s "$ENDPOINT?page=2&limit=5" | jq -r '
  "Status: \(.success // false)",
  "Items count: \(.data.skus | length)",
  "Offset: \(.data.pagination.offset)",
  "Next offset: \(.data.pagination.nextOffset // "none")"
'
echo ""

# Test 3: Category filter
echo "[Test 3] Category filter (category=inverters)"
curl -s "$ENDPOINT?category=inverters&limit=5" | jq -r '
  "Status: \(.success // false)",
  "Items count: \(.data.skus | length)",
  "First SKU category: \(.data.skus[0].category // "N/A")"
'
echo ""

# Test 4: Search filter
echo "[Test 4] Search filter (search=solar)"
curl -s "$ENDPOINT?search=solar&limit=5" | jq -r '
  "Status: \(.success // false)",
  "Items count: \(.data.skus | length)",
  "First SKU name: \(.data.skus[0].name // "N/A")"
'
echo ""

# Test 5: Cache hit (repeat Test 1)
echo "[Test 5] Cache hit test (repeat Test 1)"
START_TIME=$(date +%s%3N)
curl -s "$ENDPOINT?limit=10" > /dev/null
END_TIME=$(date +%s%3N)
DURATION=$((END_TIME - START_TIME))
echo "Response time: ${DURATION}ms (should be fast if cached)"
echo ""

echo "====================================="
echo "Smoke test complete!"
echo "====================================="
echo ""
echo "Expected results:"
echo "- All tests should return success: true"
echo "- Test 5 should be faster (<50ms) due to caching"
echo "- Check server logs for cache HIT/MISS messages"
