import json
import requests

def human_readable_list_path(list_path):
    parts = list_path.split('/')
    scan_type = parts[0].split('Scan')[0].replace('Excluded', '').replace('manual', 'Manual') + ' Scan'
    list_type = parts[1].replace('Lists', ' List').replace('Setting', '')
    return f"{scan_type} - {list_type}"

def fetch_policy_by_id(api_key, region, policy_id):
    url = f"https://workload.{region}.cloudone.trendmicro.com/api/policies/{policy_id}"
    headers = {
        'Authorization': f'ApiKey {api_key}',
        'api-version': 'v1',
        'Content-Type': 'application/json',
    }
    response = requests.get(url, headers=headers)
    return json.loads(response.text) if response.status_code == 200 else None

def fetch_policies(api_key, region):
    url = f"https://workload.{region}.cloudone.trendmicro.com/api/policies"
    headers = {
        'Authorization': f'ApiKey {api_key}',
        'api-version': 'v1',
        'Content-Type': 'application/json',
    }
    response = requests.get(url, headers=headers)
    return json.loads(response.text)['policies'] if response.status_code == 200 else None

def filter_and_group_child_policies(policies, target_groups):
    grouped_policies = {group: {} for group in target_groups}
    for policy in policies:
        name = policy.get('name', '')
        policy_id = policy.get('ID', '')
        for group in target_groups:
            if name.startswith(f"{group}-"):
                role = name.split('-')[-1]
                grouped_policies[group][role] = policy_id
    return grouped_policies

def sync_lists(api_key, region, policy_id, list_path, new_list):
    payload = {"antiMalware": {list_path.split('/')[0]: {list_path.split('/')[1]: new_list}}}
    url = f"https://workload.{region}.cloudone.trendmicro.com/api/policies/{policy_id}"
    headers = {
        'Authorization': f'ApiKey {api_key}',
        'api-version': 'v1',
        'Content-Type': 'application/json',
    }
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    if response.status_code != 200:
        print(f"Failed to sync. HTTP Status Code: {response.status_code}")
        print("Response:", response.text)
    return response.status_code == 200

def compare_and_sync_exclusion_lists(api_key, region, grouped_policies):
    list_paths = [
        "realTimeScanExcludedFileSetting/fileLists",
        "manualExcludedScanFileSetting/fileLists",
        "scheduledScanExcludedFileSetting/fileLists",
        "realTimeScanExcludedDirectorySetting/directoryLists",
        "manualScanExcludedDirectorySetting/directoryLists",
        "scheduledScanExcludedDirectorySetting/directoryLists",
        "realTimeScanExcludedFileExtensionSetting/fileExtensionLists",
        "manualScanExcludedFileExtensionSetting/fileExtensionLists",
        "scheduledScanExcludedFileExtensionSetting/fileExtensionLists",
    ]

    priority_order = ['dev-WinSvr', 'qas-WinSvr', 'prd-WinSvr']
    all_aligned = True
    discrepancies = {}
    print("Scanning started. Please wait...")  
    for role in grouped_policies[priority_order[0]].keys():
        print(f"Scanning role: {role}...")
        reference_policy_ids = [grouped_policies[group].get(role) for group in priority_order if grouped_policies[group].get(role)]
        if len(reference_policy_ids) < 2:
            continue

        reference_policies = [fetch_policy_by_id(api_key, region, policy_id) for policy_id in reference_policy_ids]

        for i in range(len(reference_policies) - 1):
            ref_policy = reference_policies[i]
            target_policy = reference_policies[i + 1]

            for list_path in list_paths:
                path_parts = list_path.split('/')
                ref_list = ref_policy['antiMalware'][path_parts[0]][path_parts[1]]
                target_list = target_policy['antiMalware'][path_parts[0]][path_parts[1]]

                if ref_list != target_list:
                    all_aligned = False
                    key = (role, human_readable_list_path(list_path))
                    involved_groups = [priority_order[i], priority_order[i + 1]]
                    discrepancies[key] = discrepancies.get(key, {'groups': set(), 'details': [], 'original_path': ''})
                    discrepancies[key]['groups'].update(involved_groups)
                    discrepancies[key]['details'].append((priority_order[i], priority_order[i + 1], ref_list, target_list))
                    discrepancies[key]['original_path'] = list_path  



    if discrepancies:
        print("Discrepancies found in the following roles and lists:")
        for i, ((role, list_name), discrepancy_info) in enumerate(discrepancies.items()):
            involved_groups = ', '.join(discrepancy_info['groups'])
            print(f"{i+1}. Role: {role}, List: {list_name}, Groups: {involved_groups}")

        selected_indices = input("Select the indices of the discrepancies you want to sync (comma-separated): ").split(',')

        for index in selected_indices:
            role, list_name = list(discrepancies.keys())[int(index) - 1]
            original_path = discrepancies[(role, list_name)]['original_path']  
            for group1, group2, list1, list2 in discrepancies[(role, list_name)]['details']:
                target_policy_id = grouped_policies[group2][role]
                sync_success = sync_lists(api_key, region, target_policy_id, original_path, list1)
                if sync_success:
                    print(f"Successfully synced {list_name} for role {role} in group {group2}.")


    else:
        print("All roles are aligned.")


def main():
    region = input("Enter your region: ")
    api_key = input("Enter your C1 API key: ")

    policies = fetch_policies(api_key, region)
    if not policies:
        print("Exiting...")
        return

    target_groups = ['dev-WinSvr', 'prd-WinSvr', 'qas-WinSvr']
    grouped_policies = filter_and_group_child_policies(policies, target_groups)
    compare_and_sync_exclusion_lists(api_key, region, grouped_policies)

if __name__ == "__main__":
    main()