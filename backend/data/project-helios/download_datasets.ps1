$slugs = Get-Content -Path "aneel_slugs.txt"
$baseUrl = "https://dadosabertos.aneel.gov.br/dataset/"
$downloadDir = "aneel_datasets"

foreach ($slug in $slugs) {
      $url = "$baseUrl$slug/download/csv"
      $outputFile = "$downloadDir\$slug.csv"
      Write-Host "Downloading $slug..."
      try {
            Invoke-WebRequest -Uri $url -OutFile $outputFile -TimeoutSec 30
            Write-Host "Downloaded $slug successfully."
      }
      catch {
            Write-Host "Failed to download $slug`: $($_.Exception.Message)"
      }
}

Write-Host "Download process completed."