targetScope = 'subscription'
param env string
param regions array = [ 'westeurope', 'northeurope' ]

resource reg 'Microsoft.Resources/deployments@2022-09-01' = {
  name: 'contoso-health-${env}'
  location: 'westeurope'
  properties: { mode: 'Incremental', template: {} }
}

output providerId string = reg.id
output healthEndpoints array = [for r in regions: { region: r, url: 'https://${r}.health.contoso.example' }]
