# Configuration
$config = @{
    CustomerServiceUrl = "http://localhost:8001"
    ProductServiceUrl = "http://localhost:8002"
    OrderServiceUrl = "http://localhost:8003"
    Token = "cb16c60747d64813e48f05307f299ea9d8fc8122"
}

# Set TLS security protocol
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.SecurityProtocolType]::Tls12

# Create certificate validation callback
$certCallback = @"
    using System;
    using System.Net;
    using System.Net.Security;
    using System.Security.Cryptography.X509Certificates;
    public class ServerCertificateValidationCallback
    {
        public static RemoteCertificateValidationCallback GetDelegate()
        {
            return new RemoteCertificateValidationCallback(Validate);
        }

        private static bool Validate(object sender, X509Certificate certificate, X509Chain chain, SslPolicyErrors sslPolicyErrors)
        {
            return true;  // Accept all certificates
        }
    }
"@

# Add the certificate validation type and set the callback
Add-Type -TypeDefinition $certCallback
[System.Net.ServicePointManager]::ServerCertificateValidationCallback = [ServerCertificateValidationCallback]::GetDelegate()

# Set up authentication headers
$headers = @{
    "Authorization" = "Token $($config.Token)"
    "Content-Type" = "application/json"
}

# Function to test service health
function Test-ServiceHealth {
    param (
        [string]$ServiceUrl,
        [string]$ServiceName
    )
    try {
        $null = Invoke-RestMethod -Method Get -Uri "$ServiceUrl/api/health/" -Headers $headers
        Write-Host "$ServiceName service is available" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "$ServiceName service is not available" -ForegroundColor Red
        return $false
    }
}

# Function to verify token
function Test-TokenValidity {
    try {
        $response = Invoke-RestMethod `
            -Method Get `
            -Uri "$($config.CustomerServiceUrl)/api/customers/" `
            -Headers $headers
        return $true
    }
    catch {
        if ($_.Exception.Response.StatusCode.value__ -eq 401) {
            Write-Host "Invalid token. Please check your authentication credentials." -ForegroundColor Red
            return $false
        }
        return $true
    }
}

# Main script
try {
    # Verify token
    if (-not (Test-TokenValidity)) {
        exit 1
    }

    # Check services
    $services = @(
        @{Url=$config.CustomerServiceUrl; Name="Customer"},
        @{Url=$config.ProductServiceUrl; Name="Product"},
        @{Url=$config.OrderServiceUrl; Name="Order"}
    )

    $allServicesOk = $true
    foreach ($service in $services) {
        if (-not (Test-ServiceHealth -ServiceUrl $service.Url -ServiceName $service.Name)) {
            $allServicesOk = $false
        }
    }

    if (-not $allServicesOk) {
        throw "Some services are not available. Please check and try again."
    }

    # ... rest of your script ...
}
catch {
    Write-Host "`nError occurred:" -ForegroundColor Red
    
    if ($_.Exception.Response) {
        $statusCode = $_.Exception.Response.StatusCode.value__
        Write-Host "Status Code: $statusCode" -ForegroundColor Red
        
        switch ($statusCode) {
            401 { Write-Host "Authentication failed. Please verify your token." -ForegroundColor Red }
            403 { Write-Host "Access forbidden. Check your permissions." -ForegroundColor Red }
            404 { Write-Host "Resource not found. Check your URLs and IDs." -ForegroundColor Red }
            500 { Write-Host "Server error. Check service logs." -ForegroundColor Red }
            default { Write-Host "Unexpected error occurred." -ForegroundColor Red }
        }
        
        if ($_.ErrorDetails.Message) {
            try {
                $errorDetails = $_.ErrorDetails.Message | ConvertFrom-Json
                Write-Host "Details: $($errorDetails.detail)" -ForegroundColor Red
            }
            catch {
                Write-Host "Details: $($_.ErrorDetails.Message)" -ForegroundColor Red
            }
        }
    }
    else {
        Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    }
    exit 1
}