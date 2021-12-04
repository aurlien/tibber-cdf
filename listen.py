import asyncio
import aiohttp
import calendar
import tibber
from cognite.client import CogniteClient
from cognite.client.data_classes import ExtractionPipelineRun
from datetime import datetime

ACCESS_TOKEN = '' # from Tibber's API
TENANT_ID = '' # Azure AD tenant ID associated with CDF project
CLIENT_ID = '' # Client ID of Azure AD app used to authenticate
CDF_CLUSTER = 'api'  # api, westeurope-1 etc
COGNITE_PROJECT = ''  # Name of CDF project

SCOPES = [f"https://{CDF_CLUSTER}.cognitedata.com/.default"]

CLIENT_SECRET = "" # Client secret from Azure AD app used to authenticate

TOKEN_URL = "https://login.microsoftonline.com/%s/oauth2/v2.0/token" % TENANT_ID

client = CogniteClient(
    token_url=TOKEN_URL,
    token_client_id=CLIENT_ID,
    token_client_secret=CLIENT_SECRET,
    token_scopes=SCOPES,
    project=COGNITE_PROJECT,
    base_url=f"https://{CDF_CLUSTER}.cognitedata.com",
    client_name="tibber_extractor"
)

async def _callback(pkg):
    data = pkg.get("data")
    if data is None:
        return
    datapoints = []
    try:
        time_obj = datetime.strptime(data.get('liveMeasurement')['timestamp'], '%Y-%m-%dT%H:%M:%S%z')
    except ValueError:
        time_obj = datetime.strptime(data.get('liveMeasurement')['timestamp'], '%Y-%m-%dT%H:%M:%S.%f%z')

    timestamp = int(datetime.timestamp(time_obj)*1000)
    datapoints.append((timestamp, data.get('liveMeasurement')['power']))
    tsPointList = []
    tsPointList.append({'externalId': 'TIBBER/live/power', 'datapoints': datapoints})
    client.datapoints.insert_multiple(tsPointList)
    client.extraction_pipeline_runs.create(ExtractionPipelineRun(status="success", external_id="tibber-extractor"))

async def run():
    async with aiohttp.ClientSession() as session:
        tibber_connection = tibber.Tibber(ACCESS_TOKEN, websession=session)
        await tibber_connection.update_info()
    print(tibber_connection.name)
    homes = tibber_connection.get_homes(only_active=False)
    print(homes)
    if len(homes) > 0:
    	home = homes[0]
    	await home.rt_subscribe(_callback)

loop = asyncio.get_event_loop()
asyncio.ensure_future(run())
loop.run_forever()

