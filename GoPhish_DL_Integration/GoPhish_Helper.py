import gophish
import logging
from GoPhish_DL_Integration.Active_Directory_Helper import get_ad_group_member_list

class Gophish_Helper:
    def __init__(self, api_key, host_name):
        self.Client = gophish.Gophish(api_key, host=host_name, verify=False)

    def convert_ad_user_to_gophish_user_object_list(self, ad_user_object_list):
        gophish_users = []

        for ad_user_object in ad_user_object_list:
            gophish_user = gophish.models.User(
                first_name=ad_user_object.First_Name,
                last_name=ad_user_object.Last_Name,
                email=ad_user_object.Email,
                position=ad_user_object.Position
            )

            gophish_users.append(gophish_user)

        return gophish_users

    def create_new_gophish_group(self, group_object):
        logging.info(f"Adding new group {group_object.name} to Gophish.")
        self.Client.groups.post(group_object)

    def modify_gophish_group(self, group_object):
        logging.info(f"Updating existing group {group_object.name} in Gophish.")
        self.Client.groups.put(group_object)

def gophish_group_processing(gophish_groups_list, ad_group, ad_helper, gophish_helper, search_base):
    group_name = ad_group['name']

    logging.info(f"Gathering group information for {group_name}")
    ad_group_members = get_ad_group_member_list(
        group_name=group_name,
        connection=ad_helper.Connection,
        search_base=search_base
    )

    if ad_group_members:
        targets_list = gophish_helper.convert_ad_user_to_gophish_user_object_list(ad_group_members)

        if [group for group in gophish_groups_list if group_name == group.name]:
            logging.info(f"\t- Group {group_name} exists in Gophish. Adding to existing groups list.")
            group_id = [group.id for group in gophish_groups_list if group_name == group.name][0]
            group_object = gophish.models.Group(
                id=group_id,
                targets=targets_list,
                name=group_name
            )

            gophish_helper.Client.groups.put(group_object)
        else:
            logging.info(f"\t- Group {group_name} does not exist in Gophish. Adding to new groups list.")
            group_object = gophish.models.Group(
                targets=targets_list,
                name=group_name
            )

            gophish_helper.Client.groups.post(group_object)
    else:
        logging.info(f"\t- Group {group_name} has no members and will not be added to a list.")
