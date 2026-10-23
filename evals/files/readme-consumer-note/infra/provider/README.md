# Provider registration

Registers the `Contoso.Health` resource provider in the subscription and deploys its endpoints.

## Deploy

```bash
az deployment sub create -l westeurope -f provider.bicep -p env=prod
```

## Parameters

| Name | Description |
|---|---|
| `env` | `dev`, `test` or `prod` |
| `regions` | Regions that get an endpoint. Default: all paired regions. |

## Outputs

- `providerId`: resource ID of the registration.
- `healthEndpoints`: array of `{ region, url }` objects.

## Troubleshooting

If registration hangs in `Registering`, run `az provider show -n Contoso.Health` and wait; it can take 15 minutes.
