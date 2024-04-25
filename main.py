import boto3

aws_console = boto3.session.Session(profile_name= 'iam-boto', region_name= 'ap-southeast-1')
client = boto3.client('ec2')


# Getting the volume id's to snapshot
response_desc_volumes = client.describe_volumes(
    Filters=[
        {
            'Name': 'attachment.instance-id',
            'Values': [
                'i-012b86d8be326a048', 'i-01dedb132cb12b3f1'
            ],
        },
    ],
)

volume_ids = []
# Getting the specific volume id's from the instances defined in line 14
for volumes in response_desc_volumes['Volumes']:
    volume_ids.append(volumes['VolumeId'])

# Creating the snapshot

for volume in volume_ids:
    response = client.create_snapshot(
        Description = 'Adhoc Snapshot',
        VolumeId = volume,
        TagSpecifications = [
            {
                'ResourceType': 'snapshot',
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': 'snp-'+'test-name'
                    },
                    {
                        'Key': 'Application',
                        'Value': 'Terraform'
                    },
                    {
                        'Key': 'Environment',
                        'Value': 'DEV'
                    }
                ]
            },
        ],
        DryRun=False
    )

    print(f'{response['State']} *** {response['SnapshotId']}')
