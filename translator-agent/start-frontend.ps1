# Start IMX Frontend Server (Static Files)
Write-Host "Starting IMX Frontend Server..." -ForegroundColor Green
Write-Host ""

$PORT = 3000
$BASE_DIR = $PSScriptRoot

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "Starting Frontend Server (Static Files)..." -ForegroundColor Green
Write-Host ""
Write-Host "Frontend UI:  http://localhost:$PORT" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "NOTE: Make sure the backend is running at http://localhost:8080" -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Create HTTP listener
$listener = New-Object System.Net.HttpListener
$listener.Prefixes.Add("http://localhost:$PORT/")

try {
    $listener.Start()
    Write-Host "Server started successfully at http://localhost:$PORT" -ForegroundColor Green
    Write-Host ""

    # MIME type mapping
    $mimeTypes = @{
        '.html' = 'text/html'
        '.css'  = 'text/css'
        '.js'   = 'application/javascript'
        '.json' = 'application/json'
        '.png'  = 'image/png'
        '.jpg'  = 'image/jpeg'
        '.jpeg' = 'image/jpeg'
        '.gif'  = 'image/gif'
        '.svg'  = 'image/svg+xml'
        '.ico'  = 'image/x-icon'
        '.woff' = 'font/woff'
        '.woff2' = 'font/woff2'
        '.ttf'  = 'font/ttf'
        '.eot'  = 'application/vnd.ms-fontobject'
        '.txt'  = 'text/plain'
    }

    while ($listener.IsListening) {
        $context = $listener.GetContext()
        $request = $context.Request
        $response = $context.Response
        
        $path = $request.Url.AbsolutePath
        Write-Host "Request: $($request.HttpMethod) $path" -ForegroundColor Gray

        # Determine file path
        $filePath = $null
        if ($path -eq '/' -or $path -eq '/index.html') {
            $filePath = Join-Path $BASE_DIR "templates\index.html"
        }
        elseif ($path -match '^/static/') {
            $filePath = Join-Path $BASE_DIR ($path.TrimStart('/') -replace '/', '\')
        }
        elseif ($path -match '^/templates/') {
            $filePath = Join-Path $BASE_DIR ($path.TrimStart('/') -replace '/', '\')
        }
        else {
            $filePath = Join-Path $BASE_DIR ($path.TrimStart('/') -replace '/', '\')
        }

        # Serve file if it exists
        if (Test-Path $filePath -PathType Leaf) {
            try {
                $content = [System.IO.File]::ReadAllBytes($filePath)
                $response.ContentLength64 = $content.Length
                
                # Set MIME type
                $extension = [System.IO.Path]::GetExtension($filePath)
                if ($mimeTypes.ContainsKey($extension)) {
                    $response.ContentType = $mimeTypes[$extension]
                }
                else {
                    $response.ContentType = 'application/octet-stream'
                }
                
                $response.StatusCode = 200
                $response.OutputStream.Write($content, 0, $content.Length)
                Write-Host "  -> 200 OK ($($content.Length) bytes)" -ForegroundColor Green
            }
            catch {
                Write-Host "  -> Error reading file: $_" -ForegroundColor Red
                $response.StatusCode = 500
            }
        }
        else {
            # 404 Not Found
            $response.StatusCode = 404
            $html = "<html><body><h1>404 Not Found</h1><p>$path</p></body></html>"
            $buffer = [System.Text.Encoding]::UTF8.GetBytes($html)
            $response.ContentType = 'text/html'
            $response.ContentLength64 = $buffer.Length
            $response.OutputStream.Write($buffer, 0, $buffer.Length)
            Write-Host "  -> 404 Not Found" -ForegroundColor Yellow
        }
        
        $response.Close()
    }
}
catch {
    Write-Host "Error: $_" -ForegroundColor Red
}
finally {
    if ($listener.IsListening) {
        $listener.Stop()
    }
    $listener.Close()
    Write-Host ""
    Write-Host "Frontend server stopped." -ForegroundColor Yellow
}
