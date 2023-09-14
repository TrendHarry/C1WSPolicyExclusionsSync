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
  Prompt the user to select the discrepancies they want to synchronize.
  
Sync Selected Exclusion Lists:
  API Used: POST /api/policies/{policy_id}
  Synchronize the exclusion lists based on the user's selection.
