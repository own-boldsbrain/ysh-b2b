# Catalog SKU List - Smoke Test (PowerShell)
# Tests the DDD pilot route GET /store/catalog/skus

$BASE_URL = if ($env:BASE_URL) { $env:BASE_URL } else { "http://localhost:9000" }
$ENDPOINT = "$BASE_URL/store/catalog/skus"

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Catalog SKU List - Smoke Test" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Testing endpoint: $ENDPOINT"
Write-Host ""

# Test 1: Basic list (first page)
Write-Host "[Test 1] Basic list (limit=10)" -ForegroundColor Yellow
$response1 = Invoke-RestMethod -Uri "$ENDPOINT?limit=10" -Method Get
Write-Host "Status: $($response1.success)"
Write-Host "Items count: $($response1.data.skus.Count)"
Write-Host "Total: $($response1.data.pagination.total)"
Write-Host "Has more: $($response1.data.pagination.hasMore)"
Write-Host ""

# Test 2: Pagination (page 2)
Write-Host "[Test 2] Pagination (page=2, limit=5)" -ForegroundColor Yellow
$response2 = Invoke-RestMethod -Uri "$ENDPOINT?page=2&limit=5" -Method Get
Write-Host "Status: $($response2.success)"
Write-Host "Items count: $($response2.data.skus.Count)"
Write-Host "Offset: $($response2.data.pagination.offset)"
Write-Host "Next offset: $($response2.data.pagination.nextOffset)"
Write-Host ""

# Test 3: Category filter
Write-Host "[Test 3] Category filter (category=inverters)" -ForegroundColor Yellow
$response3 = Invoke-RestMethod -Uri "$ENDPOINT?category=inverters&limit=5" -Method Get
Write-Host "Status: $($response3.success)"
Write-Host "Items count: $($response3.data.skus.Count)"
if ($response3.data.skus.Count -gt 0) {
      Write-Host "First SKU category: $($response3.data.skus[0].category)"
}
Write-Host ""

# Test 4: Search filter
Write-Host "[Test 4] Search filter (search=solar)" -ForegroundColor Yellow
$response4 = Invoke-RestMethod -Uri "$ENDPOINT?search=solar&limit=5" -Method Get
Write-Host "Status: $($response4.success)"
Write-Host "Items count: $($response4.data.skus.Count)"
if ($response4.data.skus.Count -gt 0) {
      Write-Host "First SKU name: $($response4.data.skus[0].name)"
}
Write-Host ""

# Test 5: Cache hit (repeat Test 1)
Write-Host "[Test 5] Cache hit test (repeat Test 1)" -ForegroundColor Yellow
$startTime = Get-Date
$response5 = Invoke-RestMethod -Uri "$ENDPOINT?limit=10" -Method Get
$endTime = Get-Date
$duration = ($endTime - $startTime).TotalMilliseconds
Write-Host "Response time: $([math]::Round($duration, 2))ms (should be fast if cached)"
Write-Host ""

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Smoke test complete!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Expected results:"
Write-Host "- All tests should return success: True"
Write-Host "- Test 5 should be faster (<50ms) due to caching"
Write-Host "- Check server logs for cache HIT/MISS messages"
