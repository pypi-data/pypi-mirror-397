# List of tools for rudi agent

import logging
import random
import json
from pydantic_ai import FunctionToolset, ModelRetry
from pydantic import HttpUrl

from rudi_node_read.rudi_node_reader import RudiNodeReader


logger = logging.getLogger(__name__)


RUDI_NODES = [
    "https://bacasable.fenix.rudi-univ-rennes1.fr",
    "https://exatow.fenix.rudi-univ-rennes1.fr",
    "https://rudi.keolis-rennes.com",
    "https://airbreizh.rudi.irisa.fr",
    "https://rm.fenix.rudi-univ-rennes1.fr",
    "https://amplisim.fenix.rudi-univ-rennes1.fr",
    "https://archives-rennes.rudi.irisa.fr",
    "https://audiar.fenix.rudi-univ-rennes1.fr",
    "https://bruz.rudi.irisa.fr",
    "https://conso-gaz.rudi.irisa.fr",
    "https://electricite.rudi.irisa.fr",
    "https://handimap.fenix.rudi-univ-rennes1.fr",
    "https://leschampslibres.fenix.rudi-univ-rennes1.fr",
    "https://montgermont.rudi.irisa.fr",
    "https://opendata.fenix.rudi-univ-rennes1.fr",
    "https://osm.fenix.rudi-univ-rennes1.fr",
    "https://eegle.fenix.rudi-univ-rennes1.fr",
    "https://cd35.fenix.rudi-univ-rennes1.fr",
    "https://kereval.fenix.rudi-univ-rennes1.fr",
    "https://tangent.fenix.rudi-univ-rennes1.fr",
    "https://tiare.rudi.univ-rennes.fr",
    "https://arkea.fenix.rudi-univ-rennes1.fr",
    "https://loiret.fenix.rudi-univ-rennes1.fr",
    "https://exatow.fenix.rudi-univ-rennes1.fr",
    "https://sib.fenix.rudi-univ-rennes1.fr",
    "https://citesource.fenix.rudi-univ-rennes1.fr",
    "https://eau-rennes.fenix.rudi-univ-rennes1.fr",
    "https://la-chapelle-thouarault.fenix.rudi-univ-rennes1.fr",
]


def get_all_nodes_urls() -> list[str] | str:
    """
    Returns the list of known Rudi Node urls.
    """
    try:
        if RUDI_NODES is None:
            return "No url was found"
        return RUDI_NODES
    except Exception as e:
        raise ModelRetry("Could not access nodes urls") from e


def load_rudi_node_reader(node_url: HttpUrl) -> RudiNodeReader:
    """
    Loads a RUDI Node Reader, an object that can access metadatas
    and files in a RUDI node.
    Args:
        node_url: the url of the rudi node
    """
    try:
        logger.info("load_rudi_node_reader: %s", node_url)
        return RudiNodeReader(str(node_url).strip("/"))
    except Exception as e:
        raise ModelRetry(
            f"Could not load RudiNodeReader from url {node_url}. Try method get_all_nodes_urls."
        ) from e


def get_node_description(node_url: HttpUrl, max_metadata: int = 5) -> str:
    """
    Uses a RudiNodeReader object to retrieve a description
    of a metadata catalogue located at url

    Args:
        node_url: the url of the rudi node

    Returns:
        a string containing a description of the node
    """
    try:
        logger.info("get_node_description: %s, %s", node_url, max_metadata)
        nr = load_rudi_node_reader(node_url)
        all_metadatas = nr.metadata_list
        if max_metadata > 5:
            max_metadata = 5
        result = nr.create_textual_description_metadata(
            all_metadatas[: min(5, len(all_metadatas))]
        )
        return result
    except Exception as e:
        raise ModelRetry(f"Could not get description of node {node_url}") from e


def get_metadata_with_uuid(uuid: str, node_url: HttpUrl) -> str | None:
    """
    Uses a RudiNodeReader object to retrieve a specific
    metadata in a rudi node.

    Args:
        uuid: a string containing the uuid v4 of a metadata
        node_url: the url of the rudi node

    Returns:
        a string containing the metadata
    """
    try:
        nr = load_rudi_node_reader(node_url)
        metadata = nr.find_metadata_with_uuid(uuid)
        logger.info("get_metadata_with_uuid : %s, %s", uuid, node_url)
        return json.dumps(metadata)
    except Exception as e:
        raise ModelRetry(
            f"Could not access metadata with uuid {uuid} from node {node_url}"
        ) from e


def get_metadata_with_title(title: str, node_url: HttpUrl) -> dict | None:
    """
    Uses a RudiNodeReader object to retrieve a specific
    metadata in a rudi node.

    Args:
        title: the title of a metadata
        node_url: the url of the rudi node

    Returns:
        a string containing the metadata
    """
    try:
        nr = load_rudi_node_reader(node_url)
        metadata = nr.find_metadata_with_title(title)
        logger.info("get_metadata_with_title : %s, %s", title, node_url)
        return metadata
    except Exception as e:
        raise ModelRetry(
            f"Could not access metadata with title {title} on node {node_url}"
        ) from e


def get_metadata_list(node_url: HttpUrl, sample: int | None = None):
    """
    Uses a RudiNodeReader object to retrieve the list
    of metadatas in a node

    Args:
        node_url: the url of the rudi node
        sample: None if no sample is taken, else the number of metadata
            to sample from the metadata list

    Returns:
        the list of all metadatas in the node
    """
    try:
        logger.info("get_metadata_list : %s, %s", node_url, sample)
        nr = load_rudi_node_reader(node_url)
        if sample is not None:
            if sample > nr.metadata_count:
                sample = nr.metadata_count
            return random.sample(nr.metadata_list, min(sample, nr.metadata_count))
        return nr.metadata_list
    except Exception as e:
        raise ModelRetry(f"Could not get metadata list on node {node_url}") from e


def get_metadata_with_keywords(node_url: HttpUrl, keywords: str | list[str]):
    """
    Uses a RudiNodeReader object to retrieve the list
    of metadatas in a node that match the given keyword.

    Args:
        node_url: the url of the rudi node
        keywords: either a keyword or a list of keywords

    Returns:
        the list of all metadatas in the node, with keywords matching
        given keywords
    """
    try:
        logger.info("get_metadata_with_keywords : %s, %s", node_url, keywords)
        nr = load_rudi_node_reader(node_url)
        return nr.get_metadata_with_keywords(keywords)
    except Exception as e:
        raise ModelRetry(
            f"Could not get metadata with keywords : {keywords} on node {node_url}"
        ) from e


def get_list_of_metadatas_uuids(node_url: HttpUrl, sample: int | None = 3) -> list[str]:
    """
    For a given url node, retrieve the list of uuid for all metadatas
    on the node. The uuid (or global id) can then be used to retrieve
    details about the metadata.

    Args:
        node_url: the url of the node
        sample: number of metadata to sample

    Returns:
        a list of uuids (as strings)
    """
    try:
        logger.info("get_list_of_metadatas_uuids : %s, %s", node_url, sample)
        nr = load_rudi_node_reader(node_url=node_url)
        if sample is not None:
            if sample > 10:
                sample = 10
            metadatas = random.sample(nr.metadata_list, sample)
        else:
            metadatas = nr.metadata_list
        res = [metadata["global_id"] for metadata in metadatas]
        return res
    except Exception as e:
        raise ModelRetry(
            f"Could not get list of uuids of metadatas on node {node_url}"
        ) from e


def create_textual_description_single_metadata(node_url: HttpUrl, metadata_uuid: str):
    """
    Return a small textual description of a single metadata,
    including title, metadata url and medias url

    Args:
        node_url: the url of the node
        metadata_uuid: the uuid of the metadata

    Return:
        a python str with the description of the metadata
    """
    try:
        logger.info(
            "create_textual_description_single_metadata: %s, %s",
            node_url,
            metadata_uuid,
        )
        nr = load_rudi_node_reader(node_url=node_url)
        metadata = nr.find_metadata_with_uuid(metadata_id=metadata_uuid)
        if metadata is None:
            raise ModelRetry(
                f"Could not access metadata : {metadata_uuid}. Check uuid is a vaild uuid and node url exists."
            )
        res = nr.create_textual_description_single_metadata(metadata)
        return res
    except Exception as e:
        raise ModelRetry(
            f"Could node create textual description of the metadata on node {node_url}"
        ) from e


rudi_toolset = FunctionToolset(
    tools=[
        get_node_description,
        get_all_nodes_urls,
        get_metadata_with_title,
        get_metadata_list,
        get_metadata_with_keywords,
        get_metadata_with_uuid,
        get_list_of_metadatas_uuids,
        create_textual_description_single_metadata,
    ]
)
