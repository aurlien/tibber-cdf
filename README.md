# tibber-cdf
Read data from Tibber's API into Cognite Data Fusion

## Usage
You will need to set the following variables as environment variables, or in an env file called `.env`:
```
TIBBER_ACCESS_TOKEN
AZURE_TENANT_ID
AZURE_CLIENT_ID
CDF_CLUSTER=
COGNITE_PROJECT=
AZURE_CLIENT_SECRET=
```

You also need to create a time series with external ID `TIBBER/live/power` before running the program.

## Dependencies
Run `pip install -r requirements.txt` 
