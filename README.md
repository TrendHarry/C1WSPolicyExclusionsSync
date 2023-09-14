# C1WSPolicyExclusionsSync - Sample Solution

User Input:
  API key
  C1 Region 
  
Fetch All Policies:
  API Used: GET /api/policies
  Retrieve all policies and their details.
  
Group Policies by Role and Environment:
  Categorize the policies into roles(sql, domino, print server, etc..) and groups (dev-WinSvr, prd-WinSvr, qas-WinSvr).
  
Compare Exclusion Lists Across Roles:
  API Used: GET /api/policies/{policy_id}
  Fetch the details of each policy and compare the exclusion lists across different groups for each role.
  
Identify Discrepancies:
  Display the roles and lists where discrepancies are found.
  
User Selection:
  Prompt the user to select the discrepancies they want to synchronize 
  note:  The script is designed to operate on a sequential priority basis,following the order of dev -> qas -> prd. This means that any discrepancies between dev and qas will result in qas aligning its exclusion lists with dev. Similarly, discrepancies between qas and prd will be resolved by making prd align with qas.
         Before proceeding with synchronization, please review policies, for sample role dev exclusions should always contains or eqaul qas, qas exclusions should always contains or eqaul prd.
  
Sync Selected Exclusion Lists:
  API Used: POST /api/policies/{policy_id}
  Synchronize the exclusion lists based on the user's selection.
