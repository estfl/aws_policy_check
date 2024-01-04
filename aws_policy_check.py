import boto3
from datetime import datetime, timedelta

def get_unused_policies(profile_name, unused_days):
    session = boto3.Session(profile_name=profile_name)
    iam = session.client('iam')
    unused_policies = []
    marker = None
    
    while True:
        list_policies_args = {'Scope': 'Local'}
        if marker:
            list_policies_args['Marker'] = marker
            
        policies = iam.list_policies(**list_policies_args)['Policies']
        
        for policy in policies:
            policy_name = policy['PolicyName']
            policy_arn = policy['Arn']
            policy_version_id = policy['DefaultVersionId']
            policy_create_date = policy['CreateDate']
            
            attached_roles = iam.list_entities_for_policy(PolicyArn=policy_arn, EntityFilter='Role')['PolicyRoles']
            assigned_roles = []
            
            for role in attached_roles:
                role_name = role['RoleName']
                role_last_used = iam.get_role(RoleName=role_name)['Role'].get('RoleLastUsed', {}).get('LastUsedDate')
                if role_last_used is None or datetime.now() - role_last_used.replace(tzinfo=None) > timedelta(days=unused_days):
                    assigned_roles.append(role_name)

            if assigned_roles:
                unused_policies.append({
                    'PolicyName': policy_name,
                    'PolicyArn': policy_arn,
                    'AssignedRoles': assigned_roles,
                    'CreateDate': policy_create_date,
                    'VersionId': policy_version_id
                })
                
                print(f"Policy Name:\t{policy_name}")
                print(f"Policy ARN:\t{policy_arn}")
                print(f"Create Date:\t{policy_create_date}")
                print(f"Policy Version:\t{policy_version_id}")
                print(f"Assigned Roles:\t{assigned_roles}")
                print()
                
        if 'IsTruncated' in policies and policies['IsTruncated']:
            marker = policies['Marker']
        else:
            break
            
    if unused_policies:
        policy_names = "\n".join([p['PolicyName'] for p in unused_policies])
        print(f"[Unused Policies]\n {policy_names}")
    else:
        print("No unused policies found.")
        
def print_unused_policies(profile_name, unused_days):
    get_unused_policies(profile_name, unused_days)

print_unused_policies('', 90)