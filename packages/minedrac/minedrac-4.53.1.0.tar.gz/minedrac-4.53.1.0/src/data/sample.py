import logging

import icat_plus_client
from dotenv import load_dotenv
from icat_plus_client.models.sample import Sample

from config import configuration

# Load .env if needed
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_samples_by(
    token: str,
    investigation_id: str | None = None,
) -> list[Sample]:
    with icat_plus_client.ApiClient(configuration) as api_client:
        # Create an instance of the API class
        api_instance = icat_plus_client.CatalogueApi(api_client)
        investigation_id = investigation_id
        try:
            # Gets samples
            samples = api_instance.catalogue_session_id_samples_get(
                token, investigation_id=str(investigation_id)
            )
            if samples:
                logger.debug("Fetched %d samples successfully.", len(samples))
                return samples
            else:
                logger.debug("No samples found for the given parameters.")
                return []
        except Exception as e:
            print(f"Exception when CatalogueApi->catalogue_session_id_samples_get: {e}")
