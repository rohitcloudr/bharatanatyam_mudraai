$ErrorActionPreference = 'Continue'
$root = $PSScriptRoot
$results = @()

function Check($name, $passed, $detail = "") {
    $script:results += [PSCustomObject]@{ Name = $name; Pass = $passed; Detail = $detail }
}

Check "vercel.json exists"          (Test-Path "$root\vercel.json")
Check ".vercelignore exists"        (Test-Path "$root\.vercelignore")
Check "web/index.html exists"       (Test-Path "$root\web\index.html")
Check "app.py exists"               (Test-Path "$root\app.py")
Check ".venv exists"                (Test-Path "$root\.venv\Scripts\python.exe")
Check "No stray DTapp.venv folder"  (-not (Test-Path "$root\DTapp.venv"))

try {
    $v = Get-Content "$root\vercel.json" -Raw | ConvertFrom-Json
    Check "vercel.json valid JSON"  $true
    Check "  outputDirectory = web" ($v.outputDirectory -eq 'web')
    $hasCamHeader = $false
    foreach ($entry in $v.headers) {
        foreach ($h in $entry.headers) {
            if ($h.key -eq 'Permissions-Policy' -and $h.value.Contains('camera=(self)')) { $hasCamHeader = $true }
        }
    }
    Check "  camera permission set" $hasCamHeader
} catch {
    Check "vercel.json valid JSON" $false $_.Exception.Message
}

$vi = Get-Content "$root\.vercelignore" -Raw
Check ".vercelignore excludes .venv/"     ($vi -match '\.venv/')
Check ".vercelignore excludes app.py"     ($vi -match '(?m)^app\.py')
Check ".vercelignore excludes templates/" ($vi -match 'templates/')

$html = Get-Content "$root\web\index.html" -Raw
Check "HTML: <!DOCTYPE>"                   ($html -match '^<!DOCTYPE html>')
Check "HTML: closing </html>"              ($html -match '</html>\s*$')
Check "HTML: <h1> tags balanced"           (([regex]::Matches($html,'<h1[^>]*>')).Count -eq ([regex]::Matches($html,'</h1>')).Count)
Check "HTML: <div> tags balanced"          (([regex]::Matches($html,'<div[^>]*>')).Count -eq ([regex]::Matches($html,'</div>')).Count)
Check "HTML: <script> tags balanced"       (([regex]::Matches($html,'<script[^>]*>')).Count -eq ([regex]::Matches($html,'</script>')).Count)
Check "HTML: MediaPipe ES import"          ($html -match 'tasks-vision@[\d.]+/vision_bundle\.mjs')
Check "HTML: hand model URL"               ($html -match 'mediapipe-models/hand_landmarker')
Check "HTML: getUserMedia call"            ($html -match 'navigator\.mediaDevices\.getUserMedia')
Check "HTML: no Flask url_for leftover"    (-not ($html -match 'url_for'))
Check "HTML: 16 mudras defined"            (([regex]::Matches($html,'(?m)^\s+(Pataka|Tripataka|Shikaram|Ardhapataka|Kartharimukha|Mayura|Ardhachandra|Arala|Katamukaha|Simhamukaha|Kapitha|Mushti|Soochi|Chandrakala|Mrigashirsha|Alapadmakam):')).Count -eq 16)

if (Test-Path "$root\.venv\Scripts\python.exe") {
    & "$root\.venv\Scripts\python.exe" -c "import py_compile; py_compile.compile(r'$root\app.py', doraise=True)" 2>&1 | Out-Null
    Check "app.py: Python syntax compiles" ($LASTEXITCODE -eq 0)
}

$pass = ($results | Where-Object { $_.Pass }).Count
$fail = ($results | Where-Object { -not $_.Pass }).Count
Write-Host ""
Write-Host ("=" * 60)
foreach ($r in $results) {
    $mark = if ($r.Pass) { "[OK]  " } else { "[FAIL]" }
    $line = "$mark  $($r.Name)"
    if ($r.Detail) { $line += "  --  $($r.Detail)" }
    Write-Host $line
}
Write-Host ("=" * 60)
$color = if ($fail -eq 0) { 'Green' } else { 'Red' }
Write-Host ("TOTAL: {0} passed, {1} failed" -f $pass, $fail) -ForegroundColor $color
