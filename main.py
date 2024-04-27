
import boto3
import datetime
import time

# Getting instance ID's to work with
print('#####################################\nWhen running the script...Please make sure to do the following:\n')
print('1. Do the snapshot for EACH environment (separate run for prod, uat, dev, and sit\n2. Original EBS volumes should be correctly named with the following naming convention: <app name>-<environment>-<mount name>) IE: terraform-uat-root')
print('3. Run the script')
print('\n#####################################\n')


# Take user input on what instances to snapshot. Use space as delimiter for multi instances (with the same environment)
instance_ids = list(input('Input the following details: Instance ID(s) separated by spaces (if more than one): ').split())

# Initiate connection to the AWS management console
aws_console = boto3.session.Session(profile_name= 'iam-boto', region_name= 'ap-southeast-1')
client = boto3.client('ec2')

# Input by user to be used for tagging the snapshot
description = input('Description: ')
application = input('Application: ').lower()
change_ticket = input('Change Ticket: ')
environment = input('Environment (prod | uat | dev | sit): ').lower()
date = str(datetime.datetime.now().date())

for instance in instance_ids:
    # Getting the volume id's attached to the input instance
    response_describe_volumes = client.describe_volumes(
        Filters = [
            {
                'Name': 'attachment.instance-id',
                'Values': [instance]
            }
        ]
    )
    
    # Getting the list of ebs volume_ids
    for volumes in response_describe_volumes['Volumes']:
        attached_ebs = list()
        attached_ebs.append(volumes['VolumeId'])
        # print(attached_ebs)


        # Getting the ebs_name (tag) for each {attached_ebs}
        for ebs in attached_ebs:
            response_get_ebs_name = client.describe_tags(
                Filters = [
                    {
                        'Name': 'resource-id',
                        'Values': [ebs]
                    }
                ]
            )
            # Initialize temporary variable {ebs_name} to store name tag for each EBS volume passed by the loop
            # Append to ebs_name variable once value of application and environment matches with default name of EBS volume
            ebs_name = list()
            for tags in response_get_ebs_name['Tags']:
                for v in tags.values():
                    if application in v and environment in v:
                        ebs_name.append(v)
                    else:
                        continue

                    # Creation of the snapshot per EBS
                    # Iterate through each EBS names stored in {ebs_name} variable -- create snapshot for each
                    for names in ebs_name:
                        response_create_snap = client.create_snapshot(
                            Description = description,
                            VolumeId = str(ebs),
                            TagSpecifications = [
                                {
                                    'ResourceType': 'snapshot',
                                    'Tags': [
                                        {
                                            'Key': 'Name',
                                            'Value': f'snp-{names}'
                                        },
                                        {
                                            'Key': 'Description',
                                            'Value': description
                                        },
                                        {
                                            'Key': 'Application',
                                            'Value': application
                                        },
                                        {
                                            'Key': 'Change Ticket',
                                            'Value': change_ticket
                                        },
                                        {
                                            'Key': 'Environment',
                                            'Value': environment
                                        },
                                        {
                                            'Key': 'Creation Date',
                                            'Value': date
                                        }
                                    ]
                                },
                            ],
                            DryRun = False
                        )

print('\n\nTaking snapshots...')
time.sleep(2)
print('#####################################')
time.sleep(1)
print('Snapshot done! Please check via management console!')