param([string]$Env = "prod")
$out = az deployment sub show -n "contoso-health-$Env" --query properties.outputs | ConvertFrom-Json
# One Grafana data source per endpoint
foreach ($ep in $out.healthEndpoints.value) {
    New-GrafanaDataSource -Name "health-$($ep.region)" -Url $ep.url
}
