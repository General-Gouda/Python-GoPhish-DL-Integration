import gophish
import json
import math
import logging
from GoPhish_DL_Integration.Active_Directory_Helper import *
from GoPhish_DL_Integration.GoPhish_Helper import *
from GoPhish_DL_Integration.Configuration_Helper import Configuration

def main():
    config_contents = Configuration()

    if config_contents.Testing:
        api_key = config_contents.Testing_API_Key
        host_name = config_contents.Testing_Gophish_Hostname
        ad_server = config_contents.Testing_ADServer
        search_base = config_contents.Testing_Search_Base
    else:
        api_key = config_contents.API_Key
        host_name = config_contents.Gophish_Hostname
        ad_server = config_contents.ADServer
        search_base = config_contents.Search_Base

    logging.info("Connecting to Gophish server.")
    gophish_helper = Gophish_Helper(
        api_key=api_key,
        host_name=host_name
    )

    logging.info("Connecting to Active Directory server.")
    ad_helper = AD_Helper(
        servername=ad_server,
        search_base=search_base
    )

    logging.info("Extracting list of Distribution groups in Active Directory.")
    ad_groups_list = get_ad_distribution_group_list(
        exclusion_search_filters=ad_helper.exclusion_search_filters,
        connection=ad_helper.Connection,
        search_base=search_base
    )

    logging.info("Extracting list of group names in Gophish.")
    gophish_groups_list = gophish_helper.Client.groups.get()

    with ThreadPoolExecutor(max_workers=(multiprocessing.cpu_count() * 2)) as executor:
        for ad_group in ad_groups_list:
            executor.submit(
                gophish_group_processing,
                gophish_groups_list,
                ad_group,
                ad_helper,
                gophish_helper,
                search_base
            )
            
    ad_helper.close_connection()
