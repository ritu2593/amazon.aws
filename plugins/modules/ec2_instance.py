#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r"""
---
module: ec2_instance
version_added: 1.0.0
short_description: Create & manage EC2 instances
description:
  - Create and manage AWS EC2 instances.
  - This module does not support creating
    L(EC2 Spot instances,https://aws.amazon.com/ec2/spot/).
  - The M(amazon.aws.ec2_spot_instance) module can create and manage spot instances.
author:
  - Ryan Scott Brown (@ryansb)
options:
  instance_ids:
    description:
      - If you specify one or more instance IDs, only instances that have the specified IDs are returned.
      - Mutually exclusive with O(exact_count).
    type: list
    elements: str
    default: []
  state:
    description:
      - Goal state for the instances.
      - "O(state=present): ensures instances exist, but does not guarantee any state (e.g. running). Newly-launched instances will be run by EC2."
      - "O(state=running): O(state=present) + ensures the instances are running."
      - "O(state=started): O(state=running) + waits for EC2 status checks to report OK if O(wait=true)."
      - "O(state=stopped): ensures an existing instance is stopped."
      - "O(state=rebooted): convenience alias for O(state=stopped) immediately followed by O(state=running)."
      - "O(state=restarted): convenience alias for O(state=stopped) immediately followed by O(state=started)."
      - "O(state=terminated): ensures an existing instance is terminated."
      - "O(state=absent): alias for O(state=terminated)."
    choices: [present, terminated, running, started, stopped, restarted, rebooted, absent]
    default: present
    type: str
  wait:
    description:
      - Whether or not to wait for the desired O(state) (use O(wait_timeout) to customize this).
    default: true
    type: bool
  wait_timeout:
    description:
      - How long to wait (in seconds) for the instance to finish booting/terminating.
    default: 600
    type: int
  instance_type:
    description:
      - Instance type to use for the instance, see
        U(https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/instance-types.html).
      - At least one of O(instance_type) or O(launch_template) must be specificed when launching an
        instance.
      - When the instance is present and the O(instance_type) specified value is different from the current value,
        the instance will be stopped and the instance type will be updated.
    type: str
  alternate_instance_types:
    description:
      - A list of alternate instance types to try if the primary O(instance_type) fails with V(InsufficientInstanceCapacity).
      - The module will attempt to launch with each alternate type in order until one succeeds or all are exhausted.
      - Only used when launching new instances, not when modifying existing instances.
    type: list
    elements: str
    version_added: 8.3.0
  count:
    description:
      - Number of instances to launch.
      - Setting this value will result in always launching new instances.
      - Mutually exclusive with O(exact_count).
    type: int
    version_added: 2.2.0
  exact_count:
    description:
      - An integer value which indicates how many instances that match the O(filters) parameter should be running.
      - Instances are either created or terminated based on this value.
      - If termination takes place, least recently created instances will be terminated based on Launch Time.
      - Mutually exclusive with O(count), O(instance_ids).
    type: int
    version_added: 2.2.0
  user_data:
    description:
      - Opaque blob of data which is made available to the EC2 instance.
    type: str
  aap_callback:
    description:
      - Preconfigured user-data to enable an instance to perform an Ansible Automation Platform
        callback (Linux only).
      - For Windows instances, to enable remote access via Ansible set O(aap_callback.windows) to V(true), and
        optionally set an admin password.
      - If using O(aap_callback.windows) and O(aap_callback.set_password), callback to Ansible Automation Platform will not
        be performed but the instance will be ready to receive winrm connections from Ansible.
      - Mutually exclusive with O(user_data).
    type: dict
    aliases: ['tower_callback']
    suboptions:
      windows:
        description:
          - Set O(aap_callback.windows=True) to use powershell instead of bash for the callback script.
        type: bool
        default: False
      set_password:
        description:
          - Optional admin password to use if O(aap_callback.windows=True).
        type: str
      tower_address:
        description:
          - IP address or DNS name of Tower server. Must be accessible via this address from the
            VPC that this instance will be launched in.
          - Required if O(aap_callback.windows=False).
        type: str
      job_template_id:
        description:
          - Either the integer ID of the Tower Job Template, or the name.
            Using a name for the job template is not supported by Ansible Tower prior to version
            3.2.
          - Required if O(aap_callback.windows=False).
        type: str
      host_config_key:
        description:
          - Host configuration secret key generated by the Tower job template.
          - Required if O(aap_callback.windows=False).
        type: str
  image:
    description:
      - An image to use for the instance. The M(amazon.aws.ec2_ami_info) module may be used to retrieve images.
        One of O(image) or O(image_id) are required when instance is not already present.
    type: dict
    suboptions:
      id:
        description:
        - The AMI ID.
        type: str
      ramdisk:
        description:
        - Overrides the AMI's default ramdisk ID.
        type: str
      kernel:
        description:
        - a string AKI to override the AMI kernel.
        type: str
  image_id:
    description:
       - I(ami) ID to use for the instance. One of O(image) or O(image_id) are required when instance is not already present.
       - This is an alias for O(image.id).
    type: str
  security_groups:
    description:
      - A list of security group IDs or names (strings).
      - Mutually exclusive with O(security_group).
      - Mutually exclusive with O(network_interfaces_ids).
    type: list
    elements: str
    default: []
  security_group:
    description:
      - A security group ID or name.
      - Mutually exclusive with O(security_groups).
      - Mutually exclusive with O(network_interfaces_ids).
    type: str
  name:
    description:
      - The Name tag for the instance.
    type: str
  vpc_subnet_id:
    description:
      - The subnet ID in which to launch the instance (VPC).
      - If none is provided, M(amazon.aws.ec2_instance) will chose the default zone of the default VPC.
      - If used along with O(network), O(vpc_subnet_id) is used as a fallback to prevent errors when O(network.subnet_id) is not specified.
    aliases: ['subnet_id']
    type: str
  network:
    description:
      - Either a dictionary containing the key C(interfaces) corresponding to a list of network interface IDs or
        containing specifications for a single network interface.
      - Use the M(amazon.aws.ec2_eni) module to create ENIs with special settings.
      - This field is deprecated and will be removed in a release after 2026-12-01, use O(network_interfaces) or O(network_interfaces_ids) instead.
      - Mutually exclusive with O(network_interfaces).
      - Mutually exclusive with O(network_interfaces_ids).
      - If used along with O(vpc_subnet_id), O(vpc_subnet_id)  is used as a fallback to prevent errors when O(network.subnet_id) is not specified.
    type: dict
    suboptions:
      interfaces:
        description:
          - A list of ENI IDs (strings) or a list of objects containing the key id.
        type: list
        elements: str
      assign_public_ip:
        description:
          - When C(true) assigns a public IP address to the interface.
        type: bool
      private_ip_address:
        description:
          - An IPv4 address to assign to the interface.
        type: str
      ipv6_addresses:
        description:
          - A list of IPv6 addresses to assign to the network interface.
        type: list
        elements: str
      source_dest_check:
        description:
          - Controls whether source/destination checking is enabled on the interface.
          - This field with be ignored when O(source_dest_check) is provided.
        type: bool
      description:
        description:
          - A description for the network interface.
        type: str
      private_ip_addresses:
        description:
          - A list of IPv4 addresses to assign to the network interface.
        type: list
        elements: str
      subnet_id:
        description:
          - The subnet to connect the network interface to.
        type: str
      delete_on_termination:
        description:
          - Delete the interface when the instance it is attached to is
            terminated.
        type: bool
      device_index:
        description:
          - The index of the interface to modify.
        type: int
      groups:
        description:
          - A list of security group IDs to attach to the interface.
        type: list
        elements: str
  source_dest_check:
    description:
      - Controls whether source/destination checking is enabled on the interface.
    type: bool
    version_added: 8.2.0
  network_interfaces:
    description:
      - A list of dictionaries containing specifications for network interfaces.
      - Use the M(amazon.aws.ec2_eni) module to create ENIs with special settings.
      - Mutually exclusive with O(network).
    type: list
    elements: dict
    version_added: 8.2.0
    suboptions:
      assign_public_ip:
        description:
          - When V(true) assigns a public IP address to the interface.
        type: bool
      private_ip_address:
        description:
          - An IPv4 address to assign to the interface.
        type: str
      ipv6_addresses:
        description:
          - A list of IPv6 addresses to assign to the network interface.
        type: list
        elements: str
      description:
        description:
          - A description for the network interface.
        type: str
      subnet_id:
        description:
          - The subnet to connect the network interface to.
        type: str
      delete_on_termination:
        description:
          - Delete the interface when the instance it is attached to is terminated.
        type: bool
        default: True
      device_index:
        description:
          - The position of the network interface in the attachment order.
          - Use device index V(0) for a primary network interface.
        type: int
        default: 0
      groups:
        description:
          - A list of security group IDs or names to attach to the interface.
        type: list
        elements: str
      private_ip_addresses:
        description:
          - A list of private IPv4 addresses to assign to the network interface.
          - Only one private IPv4 address can be designated as primary.
          - You cannot specify this option if you're launching more than one instance.
        type: list
        elements: dict
        suboptions:
          private_ip_address:
            description:
              - The private IPv4 address.
            type: str
            required: true
          primary:
            description:
              - Indicates whether the private IPv4 address is the primary private IPv4 address.
              - Only one IPv4 address can be designated as primary.
            type: bool
  network_interfaces_ids:
    description:
      - A list of ENI ids to attach to the instance.
      - Mutually exclusive with O(network).
      - Mutually exclusive with O(security_group).
      - Mutually exclusive with O(security_groups).
    type: list
    elements: dict
    version_added: 8.2.0
    suboptions:
      id:
        description:
          - The ID of the network interface.
        type: str
        required: True
      device_index:
        description:
          - The position of the network interface in the attachment order.
        type: int
        default: 0
  volumes:
    description:
      - A list of block device mappings, by default this will always use the AMI root device so the volumes option is primarily for adding more storage.
      - A mapping contains the (optional) keys V(device_name), V(virtual_name), V(ebs.volume_type), V(ebs.volume_size), V(ebs.kms_key_id),
        V(ebs.snapshot_id), V(ebs.iops), and V(ebs.delete_on_termination).
      - For more information about each parameter, see U(https://docs.aws.amazon.com/AWSEC2/latest/APIReference/API_BlockDeviceMapping.html).
    type: list
    elements: dict
  launch_template:
    description:
      - The EC2 launch template to base instance configuration on.
      - At least one of O(instance_type) or O(launch_template) must be specificed when launching an
        instance.
    type: dict
    suboptions:
      id:
        description:
          - The ID of the launch template (optional if name is specified).
        type: str
      name:
        description:
          - The pretty name of the launch template (optional if id is specified).
        type: str
      version:
        description:
          - The specific version of the launch template to use. If unspecified, the template default is chosen.
  key_name:
    description:
      - Name of the SSH access key to assign to the instance - must exist in the region the instance is created.
      - Use M(amazon.aws.ec2_key) to manage SSH keys.
    type: str
  availability_zone:
    description:
      - Specify an availability zone to use the default subnet it. Useful if not specifying the O(vpc_subnet_id) parameter.
      - If no subnet, ENI, or availability zone is provided, the default subnet in the default VPC will be used in the first AZ (alphabetically sorted).
    type: str
  instance_initiated_shutdown_behavior:
    description:
      - Whether to stop or terminate an instance upon shutdown.
    choices: ['stop', 'terminate']
    type: str
  tenancy:
    description:
      - What type of tenancy to allow an instance to use. Default is V(shared) tenancy. Dedicated tenancy will incur additional charges.
      - This field is deprecated and will be removed in a release after 2025-12-01, use O(placement) instead.
    choices: ['dedicated', 'default']
    type: str
  termination_protection:
    description:
      - Whether to enable termination protection.
      - This module will not terminate an instance with termination protection active, it must be turned off first.
    type: bool
  hibernation_options:
    description:
      - Indicates whether an instance is enabled for hibernation.
        Refer U(https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/hibernating-prerequisites.html)
        for Hibernation prerequisits.
    type: bool
    default: False
    version_added: 5.0.0
  cpu_credit_specification:
    description:
      - For T series instances, choose whether to allow increased charges to buy CPU credits if the default pool is depleted.
      - Choose V(unlimited) to enable buying additional CPU credits.
    choices: ['unlimited', 'standard']
    type: str
  cpu_options:
    description:
      - Reduce the number of vCPU exposed to the instance.
      - Those parameters can only be set at instance launch. The two suboptions O(cpu_options.threads_per_core) and  O(cpu_options.core_count) are mandatory.
      - See U(https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/instance-optimize-cpu.html) for combinations available.
    type: dict
    suboptions:
      threads_per_core:
        description:
          - Select the number of threads per core to enable. Disable or Enable Intel HT.
        choices: [1, 2]
        required: true
        type: int
      core_count:
        description:
          - Set the number of core to enable.
        required: true
        type: int
  detailed_monitoring:
    description:
      - Whether to allow detailed CloudWatch metrics to be collected, enabling more detailed alerting.
    type: bool
  ebs_optimized:
    description:
      - Whether instance is should use optimized EBS volumes, see U(https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/EBSOptimized.html).
    type: bool
  filters:
    description:
      - A dict of filters to apply when deciding whether existing instances match and should be altered. Each dict item
        consists of a filter key and a filter value. See
        U(https://docs.aws.amazon.com/AWSEC2/latest/APIReference/API_DescribeInstances.html).
        for possible filters. Filter names and values are case sensitive.
      - By default, instances are filtered for counting by their "Name" tag, base AMI, state (running, by default), and
        subnet ID. Any queryable filter can be used. Good candidates are specific tags, SSH keys, or security groups.
    type: dict
  iam_instance_profile:
    description:
      - The ARN or name of an EC2-enabled IAM instance profile to be used.
      - If a name is not provided in ARN format then the ListInstanceProfiles permission must also be granted.
        U(https://docs.aws.amazon.com/IAM/latest/APIReference/API_ListInstanceProfiles.html)
      - If no full ARN is provided, the role with a matching name will be used from the active AWS account.
    type: str
    aliases: ['instance_role']
  placement_group:
    description:
      - The placement group that needs to be assigned to the instance.
      - This field is deprecated and will be removed in a release after 2025-12-01, use O(placement) instead.
    type: str
  placement:
    description:
      - The location where the instance launched, if applicable.
    type: dict
    version_added: 7.0.0
    suboptions:
      affinity:
        description: The affinity setting for the instance on the Dedicated Host.
        type: str
        required: false
      availability_zone:
        description: The Availability Zone of the instance.
        type: str
        required: false
      group_name:
        description: The name of the placement group the instance is in.
        type: str
        required: false
      host_id:
        description: The ID of the Dedicated Host on which the instance resides.
        type: str
        required: false
      host_resource_group_arn:
        description: The ARN of the host resource group in which to launch the instances.
        type: str
        required: false
      partition_number:
        description: The number of the partition the instance is in.
        type: int
        required: false
      tenancy:
        description:
          - Type of tenancy to allow an instance to use. Default is shared tenancy. Dedicated tenancy will incur additional charges.
          - Support for O(tenancy=host) was added in amazon.aws 7.6.0.
        type: str
        required: false
        choices: ['dedicated', 'default', 'host']
  license_specifications:
    description:
      - The license specifications to be used for the instance.
    type: list
    elements: dict
    suboptions:
      license_configuration_arn:
        description: The Amazon Resource Name (ARN) of the license configuration.
        type: str
        required: true
  additional_info:
    description:
      - Reserved for Amazon's internal use.
    type: str
    version_added: 7.1.0
  metadata_options:
    description:
      - Modify the metadata options for the instance.
      - See U(https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-instance-metadata.html) for more information.
      - The two suboptions O(metadata_options.http_endpoint) and O(metadata_options.http_tokens) are supported.
    type: dict
    version_added: 2.0.0
    suboptions:
      http_endpoint:
        description:
          - Enables or disables the HTTP metadata endpoint on instances.
          - If specified a value of disabled, metadata of the instance will not be accessible.
        choices: [enabled, disabled]
        default: enabled
        type: str
      http_tokens:
        description:
          - Set the state of token usage for instance metadata requests.
          - If the state is optional (v1 and v2), instance metadata can be retrieved with or without a signed token header on request.
          - If the state is required (v2), a signed token header must be sent with any instance metadata retrieval requests.
        choices: [optional, required]
        default: optional
        type: str
      http_put_response_hop_limit:
        version_added: 4.0.0
        type: int
        description:
          - The desired HTTP PUT response hop limit for instance metadata requests.
          - The larger the number, the further instance metadata requests can travel.
        default: 1
      http_protocol_ipv6:
        version_added: 4.0.0
        type: str
        description:
          - Whether the instance metadata endpoint is available via IPv6 (V(enabled)) or not (V(disabled)).
        choices: [enabled, disabled]
        default: 'disabled'
      instance_metadata_tags:
        version_added: 4.0.0
        type: str
        description:
          - Whether the instance tags are availble (V(enabled)) via metadata endpoint or not (V(disabled)).
        choices: [enabled, disabled]
        default: 'disabled'

extends_documentation_fragment:
  - amazon.aws.common.modules
  - amazon.aws.region.modules
  - amazon.aws.tags
  - amazon.aws.boto3
"""

EXAMPLES = r"""
# Note: These examples do not set authentication details, see the AWS Guide for details.

- name: Terminate every running instance in a region. Use with EXTREME caution.
  amazon.aws.ec2_instance:
    state: absent
    filters:
      instance-state-name: running

- name: restart a particular instance by its ID
  amazon.aws.ec2_instance:
    state: restarted
    instance_ids:
      - i-12345678

- name: start an instance with a public IP address
  amazon.aws.ec2_instance:
    name: "public-compute-instance"
    key_name: "prod-ssh-key"
    vpc_subnet_id: subnet-5ca1ab1e
    instance_type: c5.large
    security_group: default
    network_interfaces:
      - assign_public_ip: true
    image_id: ami-123456
    tags:
      Environment: Testing

- name: start an instance and Add EBS
  amazon.aws.ec2_instance:
    name: "public-withebs-instance"
    vpc_subnet_id: subnet-5ca1ab1e
    instance_type: t2.micro
    key_name: "prod-ssh-key"
    security_group: default
    volumes:
      - device_name: /dev/sda1
        ebs:
          volume_size: 16
          delete_on_termination: true

- name: start an instance and Add EBS volume from a snapshot
  amazon.aws.ec2_instance:
    name: "public-withebs-instance"
    instance_type: t2.micro
    image_id: ami-1234567890
    vpc_subnet_id: subnet-5ca1ab1e
    volumes:
      - device_name: /dev/sda2
        ebs:
          snapshot_id: snap-1234567890

- name: Create EC2 instance with termination protection turned on
  amazon.aws.ec2_instance:
    name: "my-ec2-instance"
    vpc_subnet_id: subnet-5ca1ab1e
    instance_type: t3.small
    image_id: ami-123456
    termination_protection: true
    wait: true

- name: start an instance with a cpu_options
  amazon.aws.ec2_instance:
    name: "public-cpuoption-instance"
    vpc_subnet_id: subnet-5ca1ab1e
    tags:
      Environment: Testing
    instance_type: c4.large
    volumes:
      - device_name: /dev/sda1
        ebs:
          delete_on_termination: true
    cpu_options:
      core_count: 1
      threads_per_core: 1

- name: start an instance and have it begin a Tower callback on boot
  amazon.aws.ec2_instance:
    name: "tower-callback-test"
    key_name: "prod-ssh-key"
    vpc_subnet_id: subnet-5ca1ab1e
    security_group: default
    tower_callback:
      # IP or hostname of tower server
      tower_address: 1.2.3.4
      job_template_id: 876
      host_config_key: '[secret config key goes here]'
    network_interfaces:
      - assign_public_ip: true
    image_id: ami-123456
    cpu_credit_specification: unlimited
    tags:
      SomeThing: "A value"

- name: start an instance with ENI (An existing ENI ID is required)
  amazon.aws.ec2_instance:
    name: "public-eni-instance"
    key_name: "prod-ssh-key"
    vpc_subnet_id: subnet-5ca1ab1e
    network_interfaces_ids:
      - id: "eni-12345"
        device_index: 0
    tags:
      Env: "eni_on"
    volumes:
      - device_name: /dev/sda1
        ebs:
          delete_on_termination: true
    instance_type: t2.micro
    image_id: ami-123456

- name: start an instance with alternate instance types for capacity failures
  amazon.aws.ec2_instance:
    name: "resilient-instance"
    vpc_subnet_id: subnet-5ca1ab1e
    instance_type: t3.medium
    alternate_instance_types:
      - t3.small
      - t2.medium
      - t2.small
    image_id: ami-123456
    key_name: "prod-ssh-key"
    security_group: default
    tags:
      Environment: Testing

- name: add second ENI interface
  amazon.aws.ec2_instance:
    name: "public-eni-instance"
    network_interfaces_ids:
      - id: "eni-12345"
        device_index: 0
      - id: "eni-67890"
        device_index: 1
    image_id: ami-123456
    tags:
      Env: "eni_on"
    instance_type: t2.micro

- name: start an instance with metadata options
  amazon.aws.ec2_instance:
    name: "public-metadataoptions-instance"
    vpc_subnet_id: subnet-5calable
    instance_type: t3.small
    image_id: ami-123456
    tags:
      Environment: Testing
    metadata_options:
      http_endpoint: enabled
      http_tokens: optional

# ensure number of instances running with a tag matches exact_count
- name: start multiple instances
  amazon.aws.ec2_instance:
    instance_type: t3.small
    image_id: ami-123456
    exact_count: 5
    region: us-east-2
    vpc_subnet_id: subnet-0123456
    network_interfaces:
      - assign_public_ip: true
        groups:
          - default
    tags:
      foo: bar

# launches multiple instances - specific number of instances
- name: start specific number of multiple instances
  amazon.aws.ec2_instance:
    instance_type: t3.small
    image_id: ami-123456
    count: 3
    region: us-east-2
    network_interfaces:
      - assign_public_ip: true
        groups:
          - default
        subnet_id: subnet-0123456
    state: present
    tags:
      foo: bar

# launches an instance with a primary and a secondary network interfaces
- name: start an instance with a primary and secondary network interfaces
  amazon.aws.ec2_instance:
    instance_type: t2.large
    image_id: ami-123456
    region: us-east-2
    network_interfaces:
      - assign_public_ip: true
        groups:
          - default
        subnet_id: subnet-0123456
        private_ip_addresses:
          - primary: true
            private_ip_address: 168.50.4.239
          - primary: false
            private_ip_address: 168.50.4.237
    state: present
    tags:
      foo: bar

# launches a mac instance with HostResourceGroupArn and LicenseSpecifications
- name: start a mac instance with a host resource group and license specifications
  amazon.aws.ec2_instance:
    name: "mac-compute-instance"
    key_name: "prod-ssh-key"
    vpc_subnet_id: subnet-5ca1ab1e
    instance_type: mac1.metal
    security_group: default
    placement:
      host_resource_group_arn: arn:aws:resource-groups:us-east-1:123456789012:group/MyResourceGroup
    license_specifications:
      - license_configuration_arn: arn:aws:license-manager:us-east-1:123456789012:license-configuration:lic-0123456789
    image_id: ami-123456
    tags:
      Environment: Testing
"""

RETURN = r"""
instance_ids:
    description: A list of EC2 instance IDs matching the provided specification and filters.
    returned: always
    type: list
    sample: ["i-0123456789abcdef0", "i-0123456789abcdef1"]
    version_added: 5.3.0
changed_ids:
    description: A list of the set of EC2 instance IDs changed by the module action.
    returned: when instances that must be present are launched
    type: list
    sample: ["i-0123456789abcdef0"]
    version_added: 5.3.0
terminated_ids:
    description: A list of the set of EC2 instance IDs terminated by the module action.
    returned: when instances that must be absent are terminated
    type: list
    sample: ["i-0123456789abcdef1"]
    version_added: 5.3.0
instances:
    description: A list of EC2 instances.
    returned: when O(wait=true) or when matching instances already exist
    type: complex
    contains:
        ami_launch_index:
            description: The AMI launch index, which can be used to find this instance in the launch group.
            returned: always
            type: int
            sample: 0
        architecture:
            description: The architecture of the image.
            returned: always
            type: str
            sample: x86_64
        block_device_mappings:
            description: Any block device mapping entries for the instance.
            returned: always
            type: complex
            contains:
                device_name:
                    description: The device name exposed to the instance (for example, /dev/sdh or xvdh).
                    returned: always
                    type: str
                    sample: /dev/sdh
                ebs:
                    description: Parameters used to automatically set up EBS volumes when the instance is launched.
                    returned: always
                    type: complex
                    contains:
                        attach_time:
                            description: The time stamp when the attachment initiated.
                            returned: always
                            type: str
                            sample: "2017-03-23T22:51:24+00:00"
                        delete_on_termination:
                            description: Indicates whether the volume is deleted on instance termination.
                            returned: always
                            type: bool
                            sample: true
                        status:
                            description: The attachment state.
                            returned: always
                            type: str
                            sample: attached
                        volume_id:
                            description: The ID of the EBS volume.
                            returned: always
                            type: str
                            sample: vol-12345678
        capacity_reservation_specification:
            description: Information about the Capacity Reservation targeting option.
            type: complex
            contains:
                capacity_reservation_preference:
                    description: Describes the Capacity Reservation preferences.
                    type: str
                    sample: open
        client_token:
            description: The idempotency token you provided when you launched the instance, if applicable.
            returned: always
            type: str
            sample: mytoken
        cpu_options:
            description: The CPU options for the instance.
            type: complex
            contains:
                core_count:
                    description: The number of CPU cores for the instance.
                    type: int
                    sample: 1
                threads_per_core:
                    description: The number of threads per CPU core.
                    type: int
                    sample: 2
                amd_sev_snp:
                    description: Indicates whether the instance is enabled for AMD SEV-SNP.
                    type: str
                    sample: enabled
        current_instance_boot_mode:
            description: The boot mode that is used to boot the instance at launch or start.
            type: str
            sample: legacy-bios
        ebs_optimized:
            description: Indicates whether the instance is optimized for EBS I/O.
            returned: always
            type: bool
            sample: false
        ena_support:
            description: Specifies whether enhanced networking with ENA is enabled.
            returned: always
            type: bool
            sample: true
        enclave_options:
            description: Indicates whether the instance is enabled for Amazon Web Services Nitro Enclaves.
            type: dict
            contains:
                enabled:
                    description: If this parameter is set to true, the instance is enabled for Amazon Web Services Nitro Enclaves.
                    returned: always
                    type: bool
                    sample: false
        hibernation_options:
            description: Indicates whether the instance is enabled for hibernation.
            type: dict
            contains:
                configured:
                    description: If true, your instance is enabled for hibernation; otherwise, it is not enabled for hibernation.
                    returned: always
                    type: bool
                    sample: false
        hypervisor:
            description: The hypervisor type of the instance.
            returned: always
            type: str
            sample: xen
        iam_instance_profile:
            description: The IAM instance profile associated with the instance, if applicable.
            returned: always
            type: complex
            contains:
                arn:
                    description: The Amazon Resource Name (ARN) of the instance profile.
                    returned: always
                    type: str
                    sample: "arn:aws:iam::123456789012:instance-profile/myprofile"
                id:
                    description: The ID of the instance profile.
                    returned: always
                    type: str
                    sample: JFJ397FDG400FG9FD1N
        image_id:
            description: The ID of the AMI used to launch the instance.
            returned: always
            type: str
            sample: ami-0011223344
        instance_id:
            description: The ID of the instance.
            returned: always
            type: str
            sample: i-012345678
        instance_type:
            description: The instance type size of the running instance.
            returned: always
            type: str
            sample: t2.micro
        key_name:
            description: The name of the key pair, if this instance was launched with an associated key pair.
            returned: always
            type: str
            sample: my-key
        launch_time:
            description: The time the instance was launched.
            returned: always
            type: str
            sample: "2017-03-23T22:51:24+00:00"
        licenses:
            description: The license configurations for the instance.
            returned: When license specifications are provided.
            type: list
            elements: dict
            contains:
                license_configuration_arn:
                    description: The Amazon Resource Name (ARN) of the license configuration.
                    returned: always
                    type: str
                    sample: arn:aws:license-manager:us-east-1:123456789012:license-configuration:lic-0123456789
        metadata_options:
            description: The metadata options for the instance.
            returned: always
            type: complex
            contains:
                http_endpoint:
                    description: Indicates whether the HTTP metadata endpoint on your instances is enabled or disabled.
                    type: str
                    sample: enabled
                http_protocol_ipv6:
                    description: Indicates whether the IPv6 endpoint for the instance metadata service is enabled or disabled.
                    type: str
                    sample: disabled
                http_put_response_hop_limit:
                    description: The maximum number of hops that the metadata token can travel.
                    type: int
                    sample: 1
                http_tokens:
                    description: Indicates whether IMDSv2 is required.
                    type: str
                    sample: optional
                instance_metadata_tags:
                    description: Indicates whether access to instance tags from the instance metadata is enabled or disabled.
                    type: str
                    sample: disabled
                state:
                    description: The state of the metadata option changes.
                    type: str
                    sample: applied
        monitoring:
            description: The monitoring for the instance.
            returned: always
            type: complex
            contains:
                state:
                    description: Indicates whether detailed monitoring is enabled. Otherwise, basic monitoring is enabled.
                    returned: always
                    type: str
                    sample: disabled
        network_interfaces:
            description: One or more network interfaces for the instance.
            returned: always
            type: list
            elements: dict
            contains:
                association:
                    description: The association information for an Elastic IPv4 associated with the network interface.
                    returned: always
                    type: complex
                    contains:
                        ip_owner_id:
                            description: The ID of the owner of the Elastic IP address.
                            returned: always
                            type: str
                            sample: amazon
                        public_dns_name:
                            description: The public DNS name.
                            returned: always
                            type: str
                            sample: ""
                        public_ip:
                            description: The public IP address or Elastic IP address bound to the network interface.
                            returned: always
                            type: str
                            sample: 1.2.3.4
                attachment:
                    description: The network interface attachment.
                    returned: always
                    type: complex
                    contains:
                        attach_time:
                            description: The time stamp when the attachment initiated.
                            returned: always
                            type: str
                            sample: "2017-03-23T22:51:24+00:00"
                        attachment_id:
                            description: The ID of the network interface attachment.
                            returned: always
                            type: str
                            sample: eni-attach-3aff3f
                        delete_on_termination:
                            description: Indicates whether the network interface is deleted when the instance is terminated.
                            returned: always
                            type: bool
                            sample: true
                        device_index:
                            description: The index of the device on the instance for the network interface attachment.
                            returned: always
                            type: int
                            sample: 0
                        network_card_index:
                            description: The index of the network card.
                            returned: always
                            type: int
                            sample: 0
                        status:
                            description: The attachment state.
                            returned: always
                            type: str
                            sample: attached
                description:
                    description: The description.
                    returned: always
                    type: str
                    sample: My interface
                groups:
                    description: One or more security groups.
                    returned: always
                    type: list
                    elements: dict
                    contains:
                        group_id:
                            description: The ID of the security group.
                            returned: always
                            type: str
                            sample: sg-abcdef12
                        group_name:
                            description: The name of the security group.
                            returned: always
                            type: str
                            sample: mygroup
                interface_type:
                    description: The type of network interface.
                    returned: always
                    type: str
                    sample: interface
                ipv6_addresses:
                    description: One or more IPv6 addresses associated with the network interface.
                    returned: always
                    type: list
                    elements: dict
                    contains:
                        ipv6_address:
                            description: The IPv6 address.
                            returned: always
                            type: str
                            sample: "2001:0db8:85a3:0000:0000:8a2e:0370:7334"
                mac_address:
                    description: The MAC address.
                    returned: always
                    type: str
                    sample: "00:11:22:33:44:55"
                network_interface_id:
                    description: The ID of the network interface.
                    returned: always
                    type: str
                    sample: eni-01234567
                owner_id:
                    description: The AWS account ID of the owner of the network interface.
                    returned: always
                    type: str
                    sample: 01234567890
                private_dns_name:
                    description: The private DNS hostname name assigned to the instance.
                    type: str
                    returned: always
                    sample: ip-10-1-0-156.ec2.internal
                private_ip_address:
                    description: The IPv4 address of the network interface within the subnet.
                    returned: always
                    type: str
                    sample: 10.0.0.1
                private_ip_addresses:
                    description: The private IPv4 addresses associated with the network interface.
                    returned: always
                    type: list
                    elements: dict
                    contains:
                        association:
                            description: The association information for an Elastic IP address (IPv4) associated with the network interface.
                            type: complex
                            contains:
                                ip_owner_id:
                                    description: The ID of the owner of the Elastic IP address.
                                    returned: always
                                    type: str
                                    sample: amazon
                                public_dns_name:
                                    description: The public DNS name.
                                    returned: always
                                    type: str
                                    sample: ""
                                public_ip:
                                    description: The public IP address or Elastic IP address bound to the network interface.
                                    returned: always
                                    type: str
                                    sample: 1.2.3.4
                        primary:
                            description: Indicates whether this IPv4 address is the primary private IP address of the network interface.
                            returned: always
                            type: bool
                            sample: true
                        private_dns_name:
                            description: The private DNS hostname name assigned to the instance.
                            type: str
                            returned: always
                            sample: ip-10-1-0-156.ec2.internal
                        private_ip_address:
                            description: The private IPv4 address of the network interface.
                            returned: always
                            type: str
                            sample: 10.0.0.1
                source_dest_check:
                    description: Indicates whether source/destination checking is enabled.
                    returned: always
                    type: bool
                    sample: true
                status:
                    description: The status of the network interface.
                    returned: always
                    type: str
                    sample: in-use
                subnet_id:
                    description: The ID of the subnet for the network interface.
                    returned: always
                    type: str
                    sample: subnet-0123456
                vpc_id:
                    description: The ID of the VPC for the network interface.
                    returned: always
                    type: str
                    sample: vpc-0123456
        placement:
            description: The location where the instance launched, if applicable.
            returned: always
            type: complex
            contains:
                availability_zone:
                    description: The Availability Zone of the instance.
                    returned: always
                    type: str
                    sample: ap-southeast-2a
                affinity:
                    description: The affinity setting for the instance on the Dedicated Host.
                    returned: When a placement group is specified.
                    type: str
                group_id:
                    description: The ID of the placement group the instance is in (for cluster compute instances).
                    type: str
                    sample: "pg-01234566"
                group_name:
                    description: The name of the placement group the instance is in (for cluster compute instances).
                    returned: always
                    type: str
                    sample: "my-placement-group"
                host_id:
                    description: The ID of the Dedicated Host on which the instance resides.
                    type: str
                host_resource_group_arn:
                    description:  The ARN of the host resource group in which the instance is in.
                    type: str
                    sample: "arn:aws:resource-groups:us-east-1:123456789012:group/MyResourceGroup"
                partition_number:
                    description: The number of the partition the instance is in.
                    type: int
                    sample: 1
                tenancy:
                    description: Type of tenancy to allow an instance to use. Default is shared tenancy. Dedicated tenancy will incur additional charges.
                    returned: always
                    type: str
                    sample: default
        additional_info:
            description: Reserved for Amazon's internal use.
            returned: always
            type: str
            version_added: 7.1.0
            sample:
        platform_details:
            description: The platform details value for the instance.
            returned: always
            type: str
            sample: Linux/UNIX
        private_dns_name:
            description: The private DNS name.
            returned: always
            type: str
            sample: ip-10-0-0-1.ap-southeast-2.compute.internal
        private_dns_name_options:
            description: The options for the instance hostname.
            type: dict
            contains:
                enable_resource_name_dns_a_record:
                    description: Indicates whether to respond to DNS queries for instance hostnames with DNS A records.
                    type: bool
                    sample: false
                enable_resource_name_dns_aaaa_record:
                    description: Indicates whether to respond to DNS queries for instance hostnames with DNS AAAA records.
                    type: bool
                    sample: false
                hostname_type:
                    description: The type of hostname to assign to an instance.
                    type: str
                    sample: ip-name
        private_ip_address:
            description: The IPv4 address of the network interface within the subnet.
            returned: always
            type: str
            sample: 10.0.0.1
        product_codes:
            description: One or more product codes.
            returned: always
            type: list
            elements: dict
            contains:
                product_code_id:
                    description: The product code.
                    returned: always
                    type: str
                    sample: aw0evgkw8ef3n2498gndfgasdfsd5cce
                product_code_type:
                    description: The type of product code.
                    returned: always
                    type: str
                    sample: marketplace
        public_dns_name:
            description: The public DNS name assigned to the instance.
            returned: always
            type: str
            sample:
        public_ip_address:
            description: The public IPv4 address assigned to the instance
            returned: always
            type: str
            sample: 52.0.0.1
        root_device_name:
            description: The device name of the root device
            returned: always
            type: str
            sample: /dev/sda1
        root_device_type:
            description: The type of root device used by the AMI.
            returned: always
            type: str
            sample: ebs
        security_groups:
            description: One or more security groups for the instance.
            returned: always
            type: list
            elements: dict
            contains:
                group_id:
                    description: The ID of the security group.
                    returned: always
                    type: str
                    sample: sg-0123456
                group_name:
                    description: The name of the security group.
                    returned: always
                    type: str
                    sample: my-security-group
        source_dest_check:
            description: Indicates whether source/destination checking is enabled.
            returned: always
            type: bool
            sample: true
        state:
            description: The current state of the instance.
            returned: always
            type: complex
            contains:
                code:
                    description: The low byte represents the state.
                    returned: always
                    type: int
                    sample: 16
                name:
                    description: The name of the state.
                    returned: always
                    type: str
                    sample: running
        state_transition_reason:
            description: The reason for the most recent state transition.
            returned: always
            type: str
            sample:
        subnet_id:
            description: The ID of the subnet in which the instance is running.
            returned: always
            type: str
            sample: subnet-00abcdef
        tags:
            description: Any tags assigned to the instance.
            returned: always
            type: dict
            sample:
        virtualization_type:
            description: The type of virtualization of the AMI.
            returned: always
            type: str
            sample: hvm
        vpc_id:
            description: The ID of the VPC the instance is in.
            returned: always
            type: dict
            sample: vpc-0011223344
"""

import time
import uuid
import copy
from collections import namedtuple
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Set
from typing import Tuple
from typing import Union

try:
    import botocore
except ImportError:
    pass  # caught by AnsibleAWSModule


from ansible.module_utils._text import to_native
from ansible.module_utils.common.dict_transformations import camel_dict_to_snake_dict
from ansible.module_utils.common.dict_transformations import snake_dict_to_camel_dict
from ansible.module_utils.six import string_types

from ansible_collections.amazon.aws.plugins.module_utils.ec2 import AnsibleEC2Error
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import associate_iam_instance_profile
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import attach_network_interface
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import describe_iam_instance_profile_associations
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import describe_instance_attribute
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import describe_instance_status
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import describe_instances
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import describe_subnets
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import describe_vpcs
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import determine_iam_arn_from_name
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import ensure_ec2_tags
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import get_ec2_security_group_ids_from_names
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import modify_instance_attribute
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import modify_instance_metadata_options
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import replace_iam_instance_profile_association
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import run_instances as run_ec2_instances
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import start_instances
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import stop_instances
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import terminate_instances
from ansible_collections.amazon.aws.plugins.module_utils.exceptions import AnsibleAWSError
from ansible_collections.amazon.aws.plugins.module_utils.exceptions import is_ansible_aws_error_code
from ansible_collections.amazon.aws.plugins.module_utils.exceptions import is_ansible_aws_error_message
from ansible_collections.amazon.aws.plugins.module_utils.modules import AnsibleAWSModule
from ansible_collections.amazon.aws.plugins.module_utils.retries import AWSRetry
from ansible_collections.amazon.aws.plugins.module_utils.tagging import boto3_tag_list_to_ansible_dict
from ansible_collections.amazon.aws.plugins.module_utils.tagging import boto3_tag_specifications
from ansible_collections.amazon.aws.plugins.module_utils.tower import tower_callback_script
from ansible_collections.amazon.aws.plugins.module_utils.transformation import ansible_dict_to_boto3_filter_list


def build_volume_spec(params: Dict[str, Any]) -> List[Dict[str, Any]]:
    volumes = params.get("volumes") or []
    for volume in volumes:
        if "ebs" in volume:
            for int_value in ["volume_size", "iops"]:
                if int_value in volume["ebs"]:
                    volume["ebs"][int_value] = int(volume["ebs"][int_value])
            if "volume_type" in volume["ebs"] and volume["ebs"]["volume_type"] == "gp3":
                if not volume["ebs"].get("iops"):
                    volume["ebs"]["iops"] = 3000
                if "throughput" in volume["ebs"]:
                    volume["ebs"]["throughput"] = int(volume["ebs"]["throughput"])
                else:
                    volume["ebs"]["throughput"] = 125

    return [snake_dict_to_camel_dict(v, capitalize_first=True) for v in volumes]


def add_or_update_instance_profile(
    client, module: AnsibleAWSModule, instance: Dict[str, Any], desired_profile_name: str
) -> bool:
    instance_profile_setting = instance.get("IamInstanceProfile")
    iam_client = None
    if instance_profile_setting and desired_profile_name:
        if desired_profile_name in (instance_profile_setting.get("Name"), instance_profile_setting.get("Arn")):
            # great, the profile we asked for is what's there
            return False
        else:
            iam_client = module.client("iam")
            desired_arn = determine_iam_arn_from_name(iam_client, desired_profile_name)
            if instance_profile_setting.get("Arn") == desired_arn:
                return False

        # update association
        try:
            association = describe_iam_instance_profile_associations(
                client, Filters=[{"Name": "instance-id", "Values": [instance["InstanceId"]]}]
            )
        except AnsibleEC2Error as e:
            # check for InvalidAssociationID.NotFound
            module.fail_json_aws(e, "Could not find instance profile association")
        try:
            iam_client = iam_client or module.client("iam")
            replace_iam_instance_profile_association(
                client,
                association_id=association[0]["AssociationId"],
                iam_instance_profile={"Arn": determine_iam_arn_from_name(iam_client, desired_profile_name)},
            )
            return True
        except AnsibleEC2Error as e:
            module.fail_json_aws(e, "Could not associate instance profile")

    if not instance_profile_setting and desired_profile_name:
        # create association
        try:
            iam_client = iam_client or module.client("iam")
            associate_iam_instance_profile(
                client,
                iam_instance_profile={"Arn": determine_iam_arn_from_name(iam_client, desired_profile_name)},
                instance_id=instance["InstanceId"],
            )
            return True
        except AnsibleEC2Error as e:
            module.fail_json_aws(e, "Could not associate new instance profile")

    return False


def validate_assign_public_ip(module: AnsibleAWSModule) -> None:
    """
    Validate Network interface public IP configuration
        Parameters:
            module: The ansible AWS module.
    """
    network_interfaces = module.params.get("network_interfaces") or []
    network_interfaces_ids = module.params.get("network_interfaces_ids") or []
    if len(network_interfaces + network_interfaces_ids) > 1 and any(
        i.get("assign_public_ip") for i in network_interfaces if i.get("assign_public_ip") is not None
    ):
        module.fail_json(msg="The option 'assign_public_ip' cannot be set to true with multiple network interfaces.")


def validate_network_params(module: AnsibleAWSModule, nb_instances: int) -> None:
    """
    This function is used to validate network specifications with the following constraints
        - 'assign_public_ip' cannot set to True when multiple network interfaces are specified
        - 'private_ip_addresses' only one IP can be set as primary
        - 'private_ip_addresses' or 'private_ip_address' can't be specified if launching more than one instance
        Parameters:
            module: The ansible AWS module.
            nb_instances: number of instance to create.
    """
    validate_assign_public_ip(module)

    network_interfaces = module.params.get("network_interfaces")
    if network_interfaces:
        # private_ip_addresses: ensure only one private ip is set as primary
        for inty in network_interfaces:
            if len([i for i in inty.get("private_ip_addresses") or [] if i.get("primary")]) > 1:
                module.fail_json(
                    msg="Only one primary private IP address can be specified when creating network interface."
                )

        # Ensure none of 'private_ip_address', 'private_ip_addresses', 'ipv6_addresses' were provided
        # when launching more than one instance
        if nb_instances > 1:
            for opt in ("private_ip_address", "private_ip_addresses", "ipv6_addresses"):
                if any(True for inty in network_interfaces if inty.get(opt)):
                    module.fail_json(
                        msg=f"The option '{opt}' cannot be specified when launching more than one instance."
                    )


def ansible_to_boto3_eni_specification(
    client,
    module: AnsibleAWSModule,
    interface: Dict[str, Any],
    subnet_id: Optional[str],
    groups: Optional[Union[List[str], str]],
) -> Dict[str, Any]:
    """
    Converts Ansible network interface specifications into AWS network interface spec
        Parameters:
            interface: Ansible network interface specification
            subnet_id: Subnet Id
            security_groups: Optional list of security groups.
            security_group: Optional security group.
        Returns:
            AWS network interface specification.
    """
    spec = {
        "DeviceIndex": interface.get("device_index", 0),
    }
    if interface.get("assign_public_ip"):
        spec["AssociatePublicIpAddress"] = interface["assign_public_ip"]

    if interface.get("subnet_id"):
        spec["SubnetId"] = interface["subnet_id"]
    elif subnet_id:
        spec["SubnetId"] = subnet_id
    else:
        spec["SubnetId"] = describe_default_subnet(client, module)

    if interface.get("ipv6_addresses"):
        spec["Ipv6Addresses"] = [{"Ipv6Address": a} for a in interface["ipv6_addresses"]]

    if interface.get("private_ip_address"):
        spec["PrivateIpAddress"] = interface["private_ip_address"]

    if interface.get("private_ip_addresses"):
        spec["PrivateIpAddresses"] = []
        for addr in interface["private_ip_addresses"]:
            d = {"PrivateIpAddress": addr}
            if isinstance(addr, dict):
                d = {"PrivateIpAddress": addr.get("private_ip_address")}
                if addr.get("primary") is not None:
                    d.update({"Primary": addr.get("primary")})
            spec["PrivateIpAddresses"].append(d)

    spec["DeleteOnTermination"] = interface.get("delete_on_termination", True)

    interface_groups = interface.get("groups") or groups
    if interface_groups:
        spec["Groups"] = discover_security_groups(client, module, groups=interface_groups, subnet_id=spec["SubnetId"])
    if interface.get("description") is not None:
        spec["Description"] = interface["description"]
    return spec


def build_network_spec(client, module: AnsibleAWSModule) -> List[Dict[str, Any]]:
    """
    Returns network interface specifications for instance to be created.
        Parameters:
            module: The ansible AWS module.
        Returns:
            network specs (list): List of network interfaces specifications
    """

    # They specified network_interfaces_ids (mutually exclusive with security_group(s) options)
    interfaces = []
    params = module.params
    network_interfaces_ids = params.get("network_interfaces_ids")
    if network_interfaces_ids:
        interfaces = [
            {"NetworkInterfaceId": eni.get("id"), "DeviceIndex": eni.get("device_index")}
            for eni in network_interfaces_ids
        ]

    network = params.get("network")
    groups = params.get("security_groups") or params.get("security_group")
    vpc_subnet_id = params.get("vpc_subnet_id")
    network_interfaces = params.get("network_interfaces")
    if (network and not network.get("interfaces")) or network_interfaces:
        # They specified network interfaces using `network` or `network_interfaces` options
        if network and not network.get("interfaces"):
            network_interfaces = [network]
        interfaces.extend(
            [
                ansible_to_boto3_eni_specification(client, module, inty, vpc_subnet_id, groups)
                for inty in network_interfaces
            ]
        )
    elif not network and not network_interfaces_ids and not module.params.get("launch_template"):
        # No network interface configuration specified and no launch template
        # Build network interface using subnet_id and security group(s) defined in the module
        interfaces.append(ansible_to_boto3_eni_specification(client, module, {}, vpc_subnet_id, groups))
    elif network:
        # handle list of `network.interfaces` options
        interfaces.extend(
            [
                {"DeviceIndex": idx, "NetworkInterfaceId": inty if isinstance(inty, string_types) else inty.get("id")}
                for idx, inty in enumerate(network.get("interfaces", []))
            ]
        )
    return interfaces


def warn_if_public_ip_assignment_changed(module: AnsibleAWSModule, instance: Dict[str, Any]) -> None:
    # This is a non-modifiable attribute.
    assign_public_ip = (module.params.get("network") or {}).get("assign_public_ip")
    validate_assign_public_ip(module)
    network_interfaces = module.params.get("network_interfaces")
    if network_interfaces:
        # Either we only have one network interface or multiple network interface with 'assign_public_ip=false'
        # Anyways the value 'assign_public_ip' in the first item should be enough to determine whether
        # the user wants to update the public IP or not
        assign_public_ip = network_interfaces[0].get("assign_public_ip")
    if assign_public_ip is None:
        return

    # Check that public ip assignment is the same and warn if not
    public_dns_name = instance.get("PublicDnsName")
    if (public_dns_name and not assign_public_ip) or (assign_public_ip and not public_dns_name):
        module.warn(
            f"Unable to modify public ip assignment to {assign_public_ip} for instance {instance['InstanceId']}."
            " Whether or not to assign a public IP is determined during instance creation."
        )


def warn_if_cpu_options_changed(module: AnsibleAWSModule, instance: Dict[str, Any]) -> None:
    # This is a non-modifiable attribute.
    cpu_options = module.params.get("cpu_options")
    if cpu_options is None:
        return

    # Check that the CpuOptions set are the same and warn if not
    core_count_curr = instance["CpuOptions"].get("CoreCount")
    core_count = cpu_options.get("core_count")
    threads_per_core_curr = instance["CpuOptions"].get("ThreadsPerCore")
    threads_per_core = cpu_options.get("threads_per_core")
    if core_count_curr != core_count:
        module.warn(
            f"Unable to modify core_count from {core_count_curr} to {core_count}. Assigning a number of core is"
            " determinted during instance creation"
        )

    if threads_per_core_curr != threads_per_core:
        module.warn(
            f"Unable to modify threads_per_core from {threads_per_core_curr} to {threads_per_core}. Assigning a number"
            " of threads per core is determined during instance creation."
        )


def discover_security_groups(
    client,
    module: AnsibleAWSModule,
    groups: Union[str, List[str]],
    parent_vpc_id: Optional[str] = None,
    subnet_id: Optional[str] = None,
) -> List[str]:
    if subnet_id is not None:
        try:
            sub = describe_subnets(client, SubnetIds=[subnet_id])
        except is_ansible_aws_error_code("InvalidGroup.NotFound"):
            module.fail_json(
                f"Could not find subnet {subnet_id} to associate security groups. Please check the vpc_subnet_id and"
                " security_groups parameters."
            )
        except AnsibleAWSError as e:  # pylint: disable=duplicate-except
            module.fail_json_aws(e, msg=f"Error while searching for subnet {subnet_id} parent VPC.")
        parent_vpc_id = sub[0]["VpcId"]

    return get_ec2_security_group_ids_from_names(groups, client, vpc_id=parent_vpc_id)


def build_userdata(params):
    if params.get("user_data") is not None:
        return {"UserData": to_native(params.get("user_data"))}
    if params.get("aap_callback"):
        userdata = tower_callback_script(
            tower_address=params.get("aap_callback").get("tower_address"),
            job_template_id=params.get("aap_callback").get("job_template_id"),
            host_config_key=params.get("aap_callback").get("host_config_key"),
            windows=params.get("aap_callback").get("windows"),
            passwd=params.get("aap_callback").get("set_password"),
        )
        return {"UserData": userdata}
    return {}


def build_top_level_options(module: AnsibleAWSModule) -> Dict[str, Any]:
    spec = {}
    params = module.params
    if params.get("image_id"):
        spec["ImageId"] = params["image_id"]
    elif params.get("image"):
        image = params.get("image")
        spec["ImageId"] = image.get("id")
        if image.get("ramdisk"):
            spec["RamdiskId"] = image["ramdisk"]
        if image.get("kernel"):
            spec["KernelId"] = image["kernel"]
    if not spec.get("ImageId") and not params.get("launch_template"):
        module.fail_json(
            msg="You must include an image_id or image.id parameter to create an instance, or use a launch_template."
        )

    if params.get("key_name") is not None:
        spec["KeyName"] = params.get("key_name")

    spec.update(build_userdata(params))

    if params.get("launch_template") is not None:
        spec["LaunchTemplate"] = {}
        if not params.get("launch_template").get("id") and not params.get("launch_template").get("name"):
            module.fail_json(
                msg=(
                    "Could not create instance with launch template. Either launch_template.name or launch_template.id"
                    " parameters are required"
                )
            )

        if params.get("launch_template").get("id") is not None:
            spec["LaunchTemplate"]["LaunchTemplateId"] = params.get("launch_template").get("id")
        if params.get("launch_template").get("name") is not None:
            spec["LaunchTemplate"]["LaunchTemplateName"] = params.get("launch_template").get("name")
        if params.get("launch_template").get("version") is not None:
            spec["LaunchTemplate"]["Version"] = to_native(params.get("launch_template").get("version"))

    if params.get("detailed_monitoring", False):
        spec["Monitoring"] = {"Enabled": True}
    if params.get("cpu_credit_specification") is not None:
        spec["CreditSpecification"] = {"CpuCredits": params.get("cpu_credit_specification")}
    if params.get("tenancy") is not None:
        spec["Placement"] = {"Tenancy": params.get("tenancy")}
    if params.get("placement_group"):
        if "Placement" in spec:
            spec["Placement"]["GroupName"] = str(params.get("placement_group"))
        else:
            spec.setdefault("Placement", {"GroupName": str(params.get("placement_group"))})
    if params.get("placement") is not None:
        spec["Placement"] = {}
        if params.get("placement").get("availability_zone") is not None:
            spec["Placement"]["AvailabilityZone"] = params.get("placement").get("availability_zone")
        if params.get("placement").get("affinity") is not None:
            spec["Placement"]["Affinity"] = params.get("placement").get("affinity")
        if params.get("placement").get("group_name") is not None:
            spec["Placement"]["GroupName"] = params.get("placement").get("group_name")
        if params.get("placement").get("host_id") is not None:
            spec["Placement"]["HostId"] = params.get("placement").get("host_id")
        if params.get("placement").get("host_resource_group_arn") is not None:
            spec["Placement"]["HostResourceGroupArn"] = params.get("placement").get("host_resource_group_arn")
        if params.get("placement").get("partition_number") is not None:
            spec["Placement"]["PartitionNumber"] = params.get("placement").get("partition_number")
        if params.get("placement").get("tenancy") is not None:
            spec["Placement"]["Tenancy"] = params.get("placement").get("tenancy")
    if params.get("ebs_optimized") is not None:
        spec["EbsOptimized"] = params.get("ebs_optimized")
    if params.get("instance_initiated_shutdown_behavior"):
        spec["InstanceInitiatedShutdownBehavior"] = params.get("instance_initiated_shutdown_behavior")
    if params.get("termination_protection") is not None:
        spec["DisableApiTermination"] = params.get("termination_protection")
    if params.get("hibernation_options") and params.get("volumes"):
        for vol in params["volumes"]:
            if vol.get("ebs") and vol["ebs"].get("encrypted"):
                spec["HibernationOptions"] = {"Configured": True}
            else:
                module.fail_json(
                    msg=(
                        "Hibernation prerequisites not satisfied. Refer to"
                        " https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/hibernating-prerequisites.html"
                    )
                )
    if params.get("cpu_options") is not None:
        spec["CpuOptions"] = {}
        spec["CpuOptions"]["ThreadsPerCore"] = params.get("cpu_options").get("threads_per_core")
        spec["CpuOptions"]["CoreCount"] = params.get("cpu_options").get("core_count")
    if params.get("metadata_options"):
        spec["MetadataOptions"] = {}
        spec["MetadataOptions"]["HttpEndpoint"] = params.get("metadata_options").get("http_endpoint")
        spec["MetadataOptions"]["HttpTokens"] = params.get("metadata_options").get("http_tokens")
        spec["MetadataOptions"]["HttpPutResponseHopLimit"] = params.get("metadata_options").get(
            "http_put_response_hop_limit"
        )
        spec["MetadataOptions"]["HttpProtocolIpv6"] = params.get("metadata_options").get("http_protocol_ipv6")
        spec["MetadataOptions"]["InstanceMetadataTags"] = params.get("metadata_options").get("instance_metadata_tags")
    if params.get("additional_info"):
        spec["AdditionalInfo"] = params.get("additional_info")
    if params.get("license_specifications"):
        spec["LicenseSpecifications"] = []
        for license_configuration in params.get("license_specifications"):
            spec["LicenseSpecifications"].append(
                {"LicenseConfigurationArn": license_configuration.get("license_configuration_arn")}
            )
    return spec


def build_instance_tags(params: Dict[str, Any]) -> List[Dict[str, Any]]:
    tags = params.get("tags") or {}
    if params.get("name") is not None:
        tags["Name"] = params.get("name")
    specs = boto3_tag_specifications(tags, ["volume", "instance"])
    return specs


def build_run_instance_spec(client, module: AnsibleAWSModule, current_count: int = 0) -> Dict[str, Any]:
    spec = dict(
        ClientToken=uuid.uuid4().hex,
    )
    params = module.params
    spec.update(**build_top_level_options(module))

    nb_instances = params.get("count") or 1
    if params.get("exact_count"):
        nb_instances = params.get("exact_count") - current_count

    spec["MinCount"] = nb_instances
    spec["MaxCount"] = nb_instances

    # Validate network parameters
    validate_network_params(module, nb_instances)
    # Build network specs
    network_specs = build_network_spec(client, module)
    if network_specs:
        spec["NetworkInterfaces"] = network_specs
    # Build volume specs
    volume_specs = build_volume_spec(params)
    if volume_specs:
        spec["BlockDeviceMappings"] = volume_specs

    tag_spec = build_instance_tags(params)
    if tag_spec is not None:
        spec["TagSpecifications"] = tag_spec

    # IAM profile
    if params.get("iam_instance_profile"):
        spec["IamInstanceProfile"] = dict(
            Arn=determine_iam_arn_from_name(module.client("iam"), params.get("iam_instance_profile"))
        )

    if params.get("instance_type"):
        spec["InstanceType"] = params["instance_type"]

    if not (params.get("instance_type") or params.get("launch_template")):
        raise AnsibleEC2Error(
            "At least one of 'instance_type' and 'launch_template' must be passed when launching instances."
        )

    return spec


def await_instances(
    client, module: AnsibleAWSModule, ids: List[str], desired_module_state: str = "present", force_wait: bool = False
) -> None:
    if not module.params.get("wait", True) and not force_wait:
        # the user asked not to wait for anything
        return

    if module.check_mode:
        # In check mode, there is no change even if you wait.
        return

    # Map ansible state to boto3 waiter type
    state_to_boto3_waiter = {
        "present": "instance_exists",
        "started": "instance_status_ok",
        "running": "instance_running",
        "stopped": "instance_stopped",
        "restarted": "instance_status_ok",
        "rebooted": "instance_running",
        "terminated": "instance_terminated",
        "absent": "instance_terminated",
    }
    if desired_module_state not in state_to_boto3_waiter:
        module.fail_json(msg=f"Cannot wait for state {desired_module_state}, invalid state")
    boto3_waiter_type = state_to_boto3_waiter[desired_module_state]
    waiter = client.get_waiter(boto3_waiter_type)
    try:
        waiter.wait(
            InstanceIds=ids,
            WaiterConfig={
                "Delay": 15,
                "MaxAttempts": module.params.get("wait_timeout", 600) // 15,
            },
        )
    except botocore.exceptions.WaiterConfigError as e:
        instance_ids = ", ".join(ids)
        module.fail_json(
            msg=f"{to_native(e)}. Error waiting for instances {instance_ids} to reach state {boto3_waiter_type}"
        )
    except botocore.exceptions.WaiterError as e:
        instance_ids = ", ".join(ids)
        module.warn(f"Instances {instance_ids} took too long to reach state {boto3_waiter_type}. {to_native(e)}")


def diff_instance_and_params(
    client, module: AnsibleAWSModule, instance: Dict[str, Any], skip: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """boto3 instance obj, module params"""

    if skip is None:
        skip = []

    changes_to_apply = []
    id_ = instance["InstanceId"]

    ParamMapper = namedtuple("ParamMapper", ["param_key", "instance_key", "attribute_name", "add_value"])

    def value_wrapper(v):
        return {"Value": v}

    param_mappings = [
        ParamMapper("ebs_optimized", "EbsOptimized", "ebsOptimized", value_wrapper),
        ParamMapper("termination_protection", "DisableApiTermination", "disableApiTermination", value_wrapper),
        ParamMapper("instance_type", "InstanceType", "instanceType", value_wrapper),
        # user data is an immutable property
        # ParamMapper('user_data', 'UserData', 'userData', value_wrapper),
    ]

    for mapping in param_mappings:
        if module.params.get(mapping.param_key) is None:
            continue
        if mapping.instance_key in skip:
            continue

        try:
            value = describe_instance_attribute(client, instance_id=id_, attribute=mapping.attribute_name)
        except AnsibleEC2Error as e:
            module.fail_json_aws(e, msg=f"Could not describe attribute {mapping.attribute_name} for instance {id_}")
        if value[mapping.instance_key]["Value"] != module.params.get(mapping.param_key):
            arguments = dict(
                InstanceId=instance["InstanceId"],
                # Attribute=mapping.attribute_name,
            )
            arguments[mapping.instance_key] = mapping.add_value(module.params.get(mapping.param_key))
            changes_to_apply.append(arguments)

    network_interfaces = module.params.get("network_interfaces")
    if not network_interfaces and module.params.get("network") and not module.params["network"].get("interfaces"):
        network_interfaces = [module.params["network"]]
    if network_interfaces or module.params.get("security_groups") or module.params.get("security_group"):
        if len(network_interfaces or []) > 1 or len(instance["NetworkInterfaces"]) > 1:
            module.warn("Skipping group modification because instance contains mutiple network interfaces.")
        else:
            try:
                value = describe_instance_attribute(client, instance_id=id_, attribute="groupSet")
            except AnsibleEC2Error as e:
                module.fail_json_aws(e, msg=f"Could not describe attribute groupSet for instance {id_}")

            # Read interface subnet
            subnet_id = None
            groups = None
            if network_interfaces:
                subnet_id = network_interfaces[0].get("subnet_id")
                groups = network_interfaces[0].get("groups")
                if not subnet_id and module.params.get("vpc_subnet_id"):
                    subnet_id = module.params.get("vpc_subnet_id")
            elif module.params.get("vpc_subnet_id"):
                subnet_id = module.params.get("vpc_subnet_id")
            else:
                subnet_id = describe_default_subnet(client, module, use_availability_zone=False)

            # Read groups
            groups = groups or module.params.get("security_groups") or module.params.get("security_group")
            if groups:
                groups = discover_security_groups(client, module, groups=groups, subnet_id=subnet_id)
                instance_groups = [g["GroupId"] for g in value["Groups"]]
                if set(instance_groups) != set(groups):
                    changes_to_apply.append(dict(Groups=groups, InstanceId=instance["InstanceId"]))

    source_dest_check = module.params.get("source_dest_check")
    if source_dest_check is None:
        source_dest_check = (module.params.get("network") or {}).get("source_dest_check")
        # network.source_dest_check is nested, so needs to be treated separately
        if source_dest_check is not None:
            source_dest_check = bool(source_dest_check)
    if source_dest_check is not None and instance["SourceDestCheck"] != source_dest_check:
        changes_to_apply.append(
            dict(
                InstanceId=instance["InstanceId"],
                SourceDestCheck={"Value": source_dest_check},
            )
        )

    return changes_to_apply


def change_instance_metadata_options(client, module: AnsibleAWSModule, instance: Dict[str, str]) -> bool:
    metadata_options_to_apply = module.params.get("metadata_options")

    if metadata_options_to_apply is None:
        return False

    existing_metadata_options = camel_dict_to_snake_dict(instance.get("MetadataOptions"))

    changes_to_apply = {
        key: metadata_options_to_apply[key]
        for key in set(existing_metadata_options) & set(metadata_options_to_apply)
        if existing_metadata_options[key] != metadata_options_to_apply[key]
    }

    if not changes_to_apply:
        return False

    request_args = {
        "HttpTokens": changes_to_apply.get("http_tokens") or existing_metadata_options.get("http_tokens"),
        "HttpPutResponseHopLimit": changes_to_apply.get("http_put_response_hop_limit")
        or existing_metadata_options.get("http_put_response_hop_limit"),
        "HttpEndpoint": changes_to_apply.get("http_endpoint") or existing_metadata_options.get("http_endpoint"),
        "HttpProtocolIpv6": changes_to_apply.get("http_protocol_ipv6")
        or existing_metadata_options.get("http_protocol_ipv6"),
        "InstanceMetadataTags": changes_to_apply.get("instance_metadata_tags")
        or existing_metadata_options.get("instance_metadata_tags"),
    }

    changed = True
    if not module.check_mode:
        try:
            modify_instance_metadata_options(client, instance["InstanceId"], **request_args)
        except AnsibleEC2Error as e:
            module.fail_json_aws(
                e, msg=f"Failed to update instance metadata options for instance ID: {instance['InstanceId']}"
            )
    return changed


def change_network_attachments(client, module: AnsibleAWSModule, instance: Dict[str, Any]) -> bool:
    """
    Attach Network interfaces to the instance
        Parameters:
            client: AWS API client.
            module: The ansible AWS module.
            instance: A dictionnary describing the instance.
        Returns:
            A boolean set to True if changes have been done.
    """
    new_enis = [
        eni.get("id")
        for eni in module.params.get("network_interfaces_ids")
        or (module.params.get("network") or {}).get("interfaces")
        or []
    ]
    if not new_enis:
        return False

    new_ids = map(lambda x: x.get("id") if isinstance(x, dict) else x, new_enis)
    old_ids = [inty["NetworkInterfaceId"] for inty in instance["NetworkInterfaces"]]
    to_attach = set(new_ids) - set(old_ids)
    if not module.check_mode:
        for idx, eni in enumerate(new_enis):
            eni_id = eni
            device_index = idx
            if isinstance(eni, dict):
                eni_id = eni.get("id")
                device_index = eni.get("device_index") or idx
            if eni_id in to_attach:
                try:
                    attach_network_interface(
                        client,
                        DeviceIndex=device_index,
                        InstanceId=instance["InstanceId"],
                        NetworkInterfaceId=eni_id,
                    )
                except AnsibleEC2Error as e:
                    module.fail_json_aws(
                        e, msg=f"Could not attach interface {eni_id} to instance {instance['InstanceId']}"
                    )
    return bool(to_attach)


def find_instances(
    client, module: AnsibleAWSModule, ids: Optional[List[str]] = None, filters: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    sanitized_filters = dict()

    if ids:
        params = dict(InstanceIds=ids)
    elif filters is None:
        module.fail_json(msg="No filters provided when they were required")
    else:
        for key in list(filters.keys()):
            if not key.startswith("tag:"):
                sanitized_filters[key.replace("_", "-")] = filters[key]
            else:
                sanitized_filters[key] = filters[key]
        params = dict(Filters=ansible_dict_to_boto3_filter_list(sanitized_filters))

    instances = []
    for reservation in describe_instances(client, **params):
        instances.extend(reservation["Instances"])
    return instances


def get_default_vpc(client, module: AnsibleAWSModule) -> Optional[Dict[str, Any]]:
    try:
        vpcs = describe_vpcs(client, Filters=ansible_dict_to_boto3_filter_list({"isDefault": "true"}))
    except AnsibleEC2Error as e:
        module.fail_json_aws(e, msg="Could not describe default VPC")
    return vpcs[0] if vpcs else None


def get_default_subnet(
    client, module: AnsibleAWSModule, vpc: Dict[str, Any], availability_zone=None
) -> Optional[Dict[str, Any]]:
    try:
        subnets = describe_subnets(
            client,
            Filters=ansible_dict_to_boto3_filter_list(
                {
                    "vpc-id": vpc["VpcId"],
                    "state": "available",
                    "default-for-az": "true",
                }
            ),
        )
    except AnsibleEC2Error as e:
        module.fail_json_aws(e, msg=f"Could not describe default subnets for VPC {vpc['VpcId']}")
    result = None
    if subnets:
        if availability_zone is not None:
            subs_by_az = dict((subnet["AvailabilityZone"], subnet) for subnet in subnets)
            if availability_zone in subs_by_az:
                return subs_by_az[availability_zone]

        # to have a deterministic sorting order, we sort by AZ so we'll always pick the `a` subnet first
        # there can only be one default-for-az subnet per AZ, so the AZ key is always unique in this list
        by_az = sorted(subnets, key=lambda s: s["AvailabilityZone"])
        result = by_az[0]
    return result


def ensure_instance_state(
    client, module: AnsibleAWSModule, desired_module_state: str, filters: Optional[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Sets return keys depending on the desired instance state
    """
    results = dict()
    changed = False
    if desired_module_state in ("running", "started"):
        _changed, failed, instances, failure_reason = change_instance_state(
            client, module, filters=filters, desired_module_state=desired_module_state
        )
        changed |= bool(len(_changed))

        if failed:
            module.fail_json(
                msg=f"Unable to start instances: {failure_reason}",
                reboot_success=list(_changed),
                reboot_failed=failed,
            )

        results = dict(
            msg="Instances started",
            start_success=list(_changed),
            start_failed=[],
            # Avoid breaking things 'reboot' is wrong but used to be returned
            reboot_success=list(_changed),
            reboot_failed=[],
            changed=changed,
            instances=[pretty_instance(i) for i in instances],
        )
    elif desired_module_state in ("restarted", "rebooted"):
        # https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-instance-reboot.html
        # The Ansible behaviour of issuing a stop/start has a minor impact on user billing
        # This will need to be changelogged if we ever change to client.reboot_instance
        _changed, failed, instances, failure_reason = change_instance_state(
            client,
            module,
            filters=filters,
            desired_module_state="stopped",
        )

        if failed:
            module.fail_json(
                msg=f"Unable to stop instances: {failure_reason}",
                stop_success=list(_changed),
                stop_failed=failed,
            )

        changed |= bool(len(_changed))
        _changed, failed, instances, failure_reason = change_instance_state(
            client,
            module,
            filters=filters,
            desired_module_state=desired_module_state,
        )
        changed |= bool(len(_changed))

        if failed:
            module.fail_json(
                msg=f"Unable to restart instances: {failure_reason}",
                reboot_success=list(_changed),
                reboot_failed=failed,
            )

        results = dict(
            msg="Instances restarted",
            reboot_success=list(_changed),
            changed=changed,
            reboot_failed=[],
            instances=[pretty_instance(i) for i in instances],
        )
    elif desired_module_state in ("stopped",):
        _changed, failed, instances, failure_reason = change_instance_state(
            client,
            module,
            filters=filters,
            desired_module_state=desired_module_state,
        )
        changed |= bool(len(_changed))

        if failed:
            module.fail_json(
                msg=f"Unable to stop instances: {failure_reason}",
                stop_success=list(_changed),
                stop_failed=failed,
            )

        results = dict(
            msg="Instances stopped",
            stop_success=list(_changed),
            changed=changed,
            stop_failed=[],
            instances=[pretty_instance(i) for i in instances],
        )
    elif desired_module_state in ("absent", "terminated"):
        terminated, terminate_failed, instances, failure_reason = change_instance_state(
            client,
            module,
            filters=filters,
            desired_module_state=desired_module_state,
        )

        if terminate_failed:
            module.fail_json(
                msg=f"Unable to terminate instances: {failure_reason}",
                terminate_success=list(terminated),
                terminate_failed=terminate_failed,
            )
        results = dict(
            msg="Instances terminated",
            terminate_success=list(terminated),
            changed=bool(len(terminated)),
            terminate_failed=[],
            instances=[pretty_instance(i) for i in instances],
        )
    return results


def change_instance_state(
    client, module: AnsibleAWSModule, filters: Optional[Dict[str, Any]], desired_module_state: str
) -> Tuple[Set[str], List[str], Optional[List[Dict[str, Any]]], str]:
    # Map ansible state to ec2 state
    ec2_instance_states = {
        "present": "running",
        "started": "running",
        "running": "running",
        "stopped": "stopped",
        "restarted": "running",
        "rebooted": "running",
        "terminated": "terminated",
        "absent": "terminated",
    }
    desired_ec2_state = ec2_instance_states[desired_module_state]
    changed = set()
    instances = find_instances(client, module, filters=filters)
    to_change = set(i["InstanceId"] for i in instances if i["State"]["Name"] != desired_ec2_state)
    unchanged = set()
    failure_reason = ""

    for inst in instances:
        try:
            if desired_ec2_state == "terminated":
                # Before terminating an instance we need for them to leave
                # 'pending' or 'stopping' (if they're in those states)
                if inst["State"]["Name"] == "stopping":
                    await_instances(
                        client, module, [inst["InstanceId"]], desired_module_state="stopped", force_wait=True
                    )
                elif inst["State"]["Name"] == "pending":
                    await_instances(
                        client, module, [inst["InstanceId"]], desired_module_state="running", force_wait=True
                    )

                if module.check_mode:
                    changed.add(inst["InstanceId"])
                    continue

                # TODO use a client-token to prevent double-sends of these start/stop/terminate commands
                # https://docs.aws.amazon.com/AWSEC2/latest/APIReference/Run_Instance_Idempotency.html
                resp = terminate_instances(client, instance_ids=[inst["InstanceId"]])
                changed.update([i["InstanceId"] for i in resp])
            if desired_ec2_state == "stopped":
                # Before stopping an instance we need for them to leave
                # 'pending'
                if inst["State"]["Name"] == "pending":
                    await_instances(
                        client, module, [inst["InstanceId"]], desired_module_state="running", force_wait=True
                    )
                # Already moving to the relevant state
                elif inst["State"]["Name"] in ("stopping", "stopped"):
                    unchanged.add(inst["InstanceId"])
                    continue

                if module.check_mode:
                    changed.add(inst["InstanceId"])
                    continue
                resp = stop_instances(client, instance_ids=[inst["InstanceId"]])
                changed.update([i["InstanceId"] for i in resp])
            if desired_ec2_state == "running":
                if inst["State"]["Name"] in ("pending", "running"):
                    unchanged.add(inst["InstanceId"])
                    continue
                if inst["State"]["Name"] == "stopping":
                    await_instances(
                        client, module, [inst["InstanceId"]], desired_module_state="stopped", force_wait=True
                    )

                if module.check_mode:
                    changed.add(inst["InstanceId"])
                    continue

                resp = start_instances(client, instance_ids=[inst["InstanceId"]])
                changed.update([i["InstanceId"] for i in resp])
        except AnsibleEC2Error as e:
            failure_reason = str(e)

    if changed:
        await_instances(client, module, ids=list(changed) + list(unchanged), desired_module_state=desired_module_state)

    change_failed = list(to_change - changed)

    if instances:
        instances = find_instances(client, module, ids=list(i["InstanceId"] for i in instances))
    return changed, change_failed, instances, failure_reason


def pretty_instance(i):
    instance = camel_dict_to_snake_dict(i, ignore_list=["Tags"])
    instance["tags"] = boto3_tag_list_to_ansible_dict(i.get("Tags", {}))
    return instance


def modify_instance_type(
    client,
    module: AnsibleAWSModule,
    state: str,
    instance_id: str,
    changes: Dict[str, Dict[str, str]],
) -> None:
    filters = {
        "instance-id": [instance_id],
    }
    # Ensure that the instance is stopped before changing the instance type
    ensure_instance_state(client, module, "stopped", filters)

    # force wait for the instance to be stopped
    await_instances(client, module, ids=[instance_id], desired_module_state="stopped", force_wait=True)

    # Modify instance type
    modify_instance_attribute(client, instance_id=instance_id, **changes)

    # Ensure instance state
    desired_module_state = "running" if state == "present" else state
    ensure_instance_state(client, module, desired_module_state, filters)


def modify_ec2_instance_attribute(client, module: AnsibleAWSModule, state: str, changes: List[Dict[str, Any]]) -> None:
    if not module.check_mode:
        for c in changes:
            instance_id = c.pop("InstanceId")
            try:
                if "InstanceType" in c:
                    modify_instance_type(client, module, state, instance_id, c)
                else:
                    modify_instance_attribute(client, instance_id=instance_id, **c)
            except AnsibleEC2Error as e:
                module.fail_json_aws(e, msg=f"Could not apply change {str(c)} to existing instance.")


def handle_existing(
    client,
    module: AnsibleAWSModule,
    existing_matches: List[Dict[str, Any]],
    state: str,
    filters: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    tags = module.params.get("tags")
    purge_tags = module.params.get("purge_tags")
    name = module.params.get("name")

    # Name is a tag rather than a direct parameter, we need to inject 'Name'
    # into tags, but since tags isn't explicitly passed we'll treat it not being
    # set as purge_tags == False
    if name:
        if tags is None:
            purge_tags = False
            tags = {}
        tags.update({"Name": name})

    changed = False
    all_changes = list()

    for instance in existing_matches:
        changed |= ensure_ec2_tags(client, module, instance["InstanceId"], tags=tags, purge_tags=purge_tags)

        changed |= change_instance_metadata_options(client, module, instance)

        changes = diff_instance_and_params(client, module, instance)
        # modify instance attributes
        modify_ec2_instance_attribute(client, module, state, changes)

        all_changes.extend(changes)
        changed |= bool(changes)
        changed |= add_or_update_instance_profile(client, module, instance, module.params.get("iam_instance_profile"))
        changed |= change_network_attachments(client, module, instance)

    altered = find_instances(client, module, ids=[i["InstanceId"] for i in existing_matches])
    alter_config_result = dict(
        changed=changed,
        instances=[pretty_instance(i) for i in altered],
        instance_ids=[i["InstanceId"] for i in altered],
        changes=changes,
    )

    state_results = ensure_instance_state(client, module, state, filters)
    alter_config_result["changed"] |= state_results.pop("changed", False)
    result = {**state_results, **alter_config_result}

    return result


def enforce_count(
    client,
    module: AnsibleAWSModule,
    existing_matches: List[Dict[str, Any]],
    desired_module_state: str,
    filters: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    exact_count = module.params.get("exact_count")

    current_count = len(existing_matches)
    if current_count == exact_count:
        if desired_module_state not in ("absent", "terminated"):
            results = handle_existing(client, module, existing_matches, desired_module_state, filters)
        else:
            results = ensure_instance_state(client, module, desired_module_state, filters)
        if results["changed"]:
            return results
        return dict(
            changed=False,
            instances=[pretty_instance(i) for i in existing_matches],
            instance_ids=[i["InstanceId"] for i in existing_matches],
            msg=f"{exact_count} instances already {desired_module_state}, nothing to do.",
        )

    if current_count < exact_count:
        # launch instances
        results = ensure_present(
            client,
            module,
            existing_matches=existing_matches,
            desired_module_state=desired_module_state,
            current_count=current_count,
        )
    else:
        # terminate instances
        to_terminate = current_count - exact_count
        # sort the instances from least recent to most recent based on launch time
        existing_matches = sorted(existing_matches, key=lambda inst: inst["LaunchTime"])
        # get the instance ids of instances with the count tag on them
        all_instance_ids = [x["InstanceId"] for x in existing_matches]
        terminate_ids = all_instance_ids[0:to_terminate]
        results = dict(
            changed=True,
            terminated_ids=terminate_ids,
            instance_ids=all_instance_ids,
            msg=f"Would have terminated following instances if not in check mode {terminate_ids}",
        )
        if not module.check_mode:
            # terminate instances
            try:
                terminate_instances(client, terminate_ids)
            except AnsibleAWSError as e:
                module.fail_json(e, msg="Unable to terminate instances")
            await_instances(client, module, terminate_ids, desired_module_state="terminated", force_wait=True)

            # include data for all matched instances in addition to the list of terminations
            # allowing for recovery of metadata from the destructive operation
            results = dict(
                changed=True,
                msg="Successfully terminated instances.",
                terminated_ids=terminate_ids,
                instance_ids=all_instance_ids,
                instances=existing_matches,
            )

    if not module.check_mode:
        # Find instances
        existing_matches = find_instances(client, module, filters=filters)
        # Update instance attributes
        updated_results = handle_existing(client, module, existing_matches, desired_module_state, filters)
        if updated_results["changed"]:
            results = updated_results
    return results


def ensure_present(
    client,
    module: AnsibleAWSModule,
    existing_matches: Optional[List[Dict[str, Any]]],
    desired_module_state: str,
    current_count: Optional[int] = None,
) -> Dict[str, Any]:
    tags = dict(module.params.get("tags") or {})
    name = module.params.get("name")
    if name:
        tags["Name"] = name

    instance_spec = build_run_instance_spec(client, module, current_count)
    # If check mode is enabled,suspend 'ensure function'.
    if module.check_mode:
        if existing_matches:
            instance_ids = [x["InstanceId"] for x in existing_matches]
            return dict(
                changed=True,
                instance_ids=instance_ids,
                instances=existing_matches,
                spec=instance_spec,
                msg="Would have launched instances if not in check_mode.",
            )
        else:
            return dict(
                changed=True,
                spec=instance_spec,
                msg="Would have launched instances if not in check_mode.",
            )
    instance_response = run_instances(client, module, **instance_spec)
    instances = instance_response["Instances"]
    instance_ids = [i["InstanceId"] for i in instances]

    # Wait for instances to exist in the EC2 API before
    # attempting to modify them
    await_instances(client, module, instance_ids, desired_module_state="present", force_wait=True)

    for ins in instances:
        # Wait for instances to exist (don't check state)
        try:
            describe_instance_status(
                client,
                InstanceIds=[ins["InstanceId"]],
                IncludeAllInstances=True,
            )
        except AnsibleEC2Error as e:
            module.fail_json_aws(e, msg="Failed to fetch status of new EC2 instance")
        changes = diff_instance_and_params(client, module, ins, skip=["UserData", "EbsOptimized"])
        # modify instance attributes
        modify_ec2_instance_attribute(client, module, desired_module_state, changes)

    if existing_matches:
        # If we came from enforce_count, create a second list to distinguish
        # between existing and new instances when returning the entire cohort
        all_instance_ids = [x["InstanceId"] for x in existing_matches] + instance_ids
    if not module.params.get("wait"):
        if existing_matches:
            return dict(
                changed=True,
                changed_ids=instance_ids,
                instance_ids=all_instance_ids,
                spec=instance_spec,
            )
        else:
            return dict(
                changed=True,
                instance_ids=instance_ids,
                spec=instance_spec,
            )
    await_instances(client, module, instance_ids, desired_module_state=desired_module_state)
    instances = find_instances(client, module, ids=instance_ids)

    if existing_matches:
        all_instances = existing_matches + instances
        return dict(
            changed=True,
            changed_ids=instance_ids,
            instance_ids=all_instance_ids,
            instances=[pretty_instance(i) for i in all_instances],
            spec=instance_spec,
        )
    else:
        return dict(
            changed=True,
            instance_ids=instance_ids,
            instances=[pretty_instance(i) for i in instances],
            spec=instance_spec,
        )


def run_instances(client, module: AnsibleAWSModule, **instance_spec: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run EC2 instances with retry logic for InsufficientInstanceCapacity errors.
    
    If the primary instance type fails with InsufficientInstanceCapacity,
    try alternate instance types specified in the module parameters.
    """
    # Get the primary instance type and alternate types
    primary_instance_type = instance_spec.get("InstanceType")
    alternate_instance_types = module.params.get("alternate_instance_types", [])
    
    # List of instance types to try (primary first, then alternates)
    instance_types_to_try = [primary_instance_type] if primary_instance_type else []
    if alternate_instance_types:
        instance_types_to_try.extend(alternate_instance_types)
    last_error = None
    
    for i, instance_type in enumerate(instance_types_to_try):
        # Create a copy of the instance spec with the current instance type to maintain original values
        current_spec = copy.deepcopy(instance_spec)
        current_spec["InstanceType"] = instance_type
        try:
            result = run_ec2_instances(client, **current_spec)
            # If we successfully launched with an alternate instance type, update the module params
            # to reflect the actually used instance type to prevent later modification attempts
            if i > 0:
                module.warn(f"Successfully launched instance with alternate instance type '{instance_type}' "
                           f"after primary instance type '{primary_instance_type}' failed with InsufficientInstanceCapacity")
                # Update the module parameters to reflect the actually used instance type
                module.params["instance_type"] = instance_type
            
            return result
            
        except is_ansible_aws_error_message("Invalid IAM Instance Profile ARN"):
            # IAM instance profile error - likely due to eventual consistency
            # If the instance profile has just been created, it takes some time 
            # to be visible by EC2. Wait 10 seconds and retry with the same instance type
            time.sleep(10)
            try:
                result = run_ec2_instances(client, **current_spec)
                
                # If we successfully launched with an alternate instance type, update the module params
                # to reflect the actually used instance type to prevent later modification attempts
                if i > 0:
                    module.warn(f"Successfully launched instance with alternate instance type '{instance_type}' "
                               f"after primary instance type '{primary_instance_type}' failed with InsufficientInstanceCapacity")
                    # Update the module parameters to reflect the actually used instance type
                    module.params["instance_type"] = instance_type
                
                return result
                
            except is_ansible_aws_error_code("InsufficientInstanceCapacity") as e:
                # InsufficientInstanceCapacity occurred during IAM retry attempt
                # This handles the case where IAM profile propagation succeeded but
                # the instance type still has insufficient capacity
                last_error = e
                if i < len(instance_types_to_try) - 1:
                    # More instance types available, continue to next one
                    continue
                else:
                    # This was the last instance type to try, re-raise the error
                    raise
                
        except is_ansible_aws_error_code("InsufficientInstanceCapacity") as e:
            # InsufficientInstanceCapacity occurred on initial attempt
            # This handles the primary failure scenario for capacity issues
            last_error = e
            if i < len(instance_types_to_try) - 1:
                # More instance types available, continue to next one
                continue
            else:
                # This was the last instance type to try, re-raise the error
                raise
        except Exception as e:
            # For any other error (not IAM or capacity related), re-raise immediately
            # These errors are not retryable and should fail fast
            raise
    
    # If we get here, all instance types failed with InsufficientInstanceCapacity
    raise last_error


def describe_default_subnet(client, module: AnsibleAWSModule, use_availability_zone: bool = True) -> str:
    """
    Read default subnet associated to the AWS account
        Parameters:
            client: AWS API client
            module: The Ansible AWS module
            use_availability_zone: Whether to use availability zone to find the default subnet.
        Returns:
            The default subnet id.
    """
    default_vpc = get_default_vpc(client, module)
    if not default_vpc:
        module.fail_json(
            msg=("No default subnet could be found - you must include a VPC subnet ID (vpc_subnet_id parameter).")
        )
    availability_zone = module.params.get("availability_zone") if use_availability_zone else None
    return get_default_subnet(client, module, default_vpc, availability_zone)["SubnetId"]


def build_network_filters(client, module: AnsibleAWSModule) -> Dict[str, List[str]]:
    """
    Create Network filters for the DescribeInstances API
        Returns:
            Dictionnary of network filters
    """
    filters = {}
    network_interfaces_ids = module.params.get("network_interfaces_ids") or (module.params.get("network") or {}).get(
        "interfaces"
    )
    if module.params.get("vpc_subnet_id"):
        filters["subnet-id"] = [module.params.get("vpc_subnet_id")]
    elif network_interfaces_ids:
        filters["network-interface.network-interface-id"] = [
            eni["id"] if isinstance(eni, dict) else eni for eni in network_interfaces_ids
        ]
    else:
        filters["subnet-id"] = describe_default_subnet(client, module)
    return filters


def build_filters(client, module: AnsibleAWSModule) -> Dict[str, Any]:
    # all states except shutting-down and terminated
    instance_state_names = ["pending", "running", "stopping", "stopped"]
    filters = {}
    instance_ids = module.params.get("instance_ids")
    if isinstance(instance_ids, string_types):
        filters = {"instance-id": [instance_ids], "instance-state-name": instance_state_names}
    elif isinstance(instance_ids, list) and len(instance_ids):
        filters = {"instance-id": instance_ids, "instance-state-name": instance_state_names}
    else:
        if not module.params.get("launch_template"):
            # Network filters
            filters.update(build_network_filters(client, module))
        if module.params.get("name"):
            filters["tag:Name"] = [module.params.get("name")]
        elif module.params.get("tags"):
            name_tag = module.params.get("tags").get("Name", None)
            if name_tag:
                filters["tag:Name"] = [name_tag]

        if module.params.get("image_id"):
            filters["image-id"] = [module.params.get("image_id")]
        elif (module.params.get("image") or {}).get("id"):
            filters["image-id"] = [module.params.get("image", {}).get("id")]

        if filters:
            # add the instance state filter if any filter key was provided
            filters["instance-state-name"] = instance_state_names
    return filters


def main():
    argument_spec = dict(
        state=dict(
            default="present",
            choices=["present", "started", "running", "stopped", "restarted", "rebooted", "terminated", "absent"],
        ),
        wait=dict(default=True, type="bool"),
        wait_timeout=dict(default=600, type="int"),
        count=dict(type="int"),
        exact_count=dict(type="int"),
        image=dict(
            type="dict",
            options=dict(
                id=dict(type="str"),
                ramdisk=dict(type="str"),
                kernel=dict(type="str"),
            ),
        ),
        image_id=dict(type="str"),
        instance_type=dict(type="str"),
        alternate_instance_types=dict(type="list", elements="str"),
        user_data=dict(type="str"),
        aap_callback=dict(
            type="dict",
            aliases=["tower_callback"],
            required_if=[
                (
                    "windows",
                    False,
                    (
                        "tower_address",
                        "job_template_id",
                        "host_config_key",
                    ),
                    False,
                ),
            ],
            options=dict(
                windows=dict(type="bool", default=False),
                set_password=dict(type="str", no_log=True),
                tower_address=dict(type="str"),
                job_template_id=dict(type="str"),
                host_config_key=dict(type="str", no_log=True),
            ),
        ),
        ebs_optimized=dict(type="bool"),
        vpc_subnet_id=dict(type="str", aliases=["subnet_id"]),
        availability_zone=dict(type="str"),
        security_groups=dict(default=[], type="list", elements="str"),
        security_group=dict(type="str"),
        iam_instance_profile=dict(type="str", aliases=["instance_role"]),
        name=dict(type="str"),
        tags=dict(type="dict", aliases=["resource_tags"]),
        purge_tags=dict(type="bool", default=True),
        filters=dict(type="dict", default=None),
        launch_template=dict(type="dict"),
        license_specifications=dict(
            type="list",
            elements="dict",
            options=dict(
                license_configuration_arn=dict(type="str", required=True),
            ),
        ),
        key_name=dict(type="str"),
        cpu_credit_specification=dict(type="str", choices=["standard", "unlimited"]),
        cpu_options=dict(
            type="dict",
            options=dict(
                core_count=dict(type="int", required=True),
                threads_per_core=dict(type="int", choices=[1, 2], required=True),
            ),
        ),
        tenancy=dict(type="str", choices=["dedicated", "default"]),
        placement_group=dict(type="str"),
        placement=dict(
            type="dict",
            options=dict(
                affinity=dict(type="str"),
                availability_zone=dict(type="str"),
                group_name=dict(type="str"),
                host_id=dict(type="str"),
                host_resource_group_arn=dict(type="str"),
                partition_number=dict(type="int"),
                tenancy=dict(type="str", choices=["dedicated", "default", "host"]),
            ),
        ),
        instance_initiated_shutdown_behavior=dict(type="str", choices=["stop", "terminate"]),
        termination_protection=dict(type="bool"),
        hibernation_options=dict(type="bool", default=False),
        detailed_monitoring=dict(type="bool"),
        instance_ids=dict(default=[], type="list", elements="str"),
        network=dict(default=None, type="dict"),
        volumes=dict(default=None, type="list", elements="dict"),
        metadata_options=dict(
            type="dict",
            options=dict(
                http_endpoint=dict(choices=["enabled", "disabled"], default="enabled"),
                http_put_response_hop_limit=dict(type="int", default=1),
                http_tokens=dict(choices=["optional", "required"], default="optional"),
                http_protocol_ipv6=dict(choices=["disabled", "enabled"], default="disabled"),
                instance_metadata_tags=dict(choices=["disabled", "enabled"], default="disabled"),
            ),
        ),
        additional_info=dict(type="str"),
        network_interfaces_ids=dict(
            type="list",
            elements="dict",
            options=dict(
                id=dict(required=True),
                device_index=dict(type="int", default=0),
            ),
        ),
        network_interfaces=dict(
            type="list",
            elements="dict",
            options=dict(
                assign_public_ip=dict(type="bool"),
                private_ip_address=dict(),
                ipv6_addresses=dict(type="list", elements="str"),
                description=dict(),
                private_ip_addresses=dict(
                    type="list",
                    elements="dict",
                    options=dict(private_ip_address=dict(required=True), primary=dict(type="bool")),
                ),
                subnet_id=dict(),
                delete_on_termination=dict(type="bool", default=True),
                device_index=dict(type="int", default=0),
                groups=dict(type="list", elements="str"),
            ),
        ),
        source_dest_check=dict(type="bool"),
    )
    # running/present are synonyms
    # as are terminated/absent
    module = AnsibleAWSModule(
        argument_spec=argument_spec,
        mutually_exclusive=[
            ["security_groups", "security_group"],
            ["availability_zone", "vpc_subnet_id"],
            ["aap_callback", "user_data"],
            ["image_id", "image"],
            ["exact_count", "count"],
            ["exact_count", "instance_ids"],
            ["tenancy", "placement"],
            ["placement_group", "placement"],
            ["network", "network_interfaces"],
            ["network", "network_interfaces_ids"],
            ["security_group", "network_interfaces_ids"],
            ["security_groups", "network_interfaces_ids"],
        ],
        supports_check_mode=True,
    )

    result = dict()

    if module.params.get("network"):
        module.deprecate(
            "The network parameter has been deprecated, please use network_interfaces and/or network_interfaces_ids instead.",
            date="2026-12-01",
            collection_name="amazon.aws",
        )
        if module.params["network"].get("interfaces"):
            if module.params.get("security_group"):
                module.fail_json(msg="Parameter network.interfaces can't be used with security_group")
            if module.params.get("security_groups"):
                module.fail_json(msg="Parameter network.interfaces can't be used with security_groups")
        if (
            module.params["network"].get("source_dest_check") is not None
            and module.params.get("source_dest_check") is not None
        ):
            module.warn(
                "the source_dest_check option has been set therefore network.source_dest_check will be ignored."
            )

    if module.params.get("placement_group"):
        module.deprecate(
            "The placement_group parameter has been deprecated, please use placement.group_name instead.",
            date="2025-12-01",
            collection_name="amazon.aws",
        )

    if module.params.get("tenancy"):
        module.deprecate(
            "The tenancy parameter has been deprecated, please use placement.tenancy instead.",
            date="2025-12-01",
            collection_name="amazon.aws",
        )

    state = module.params.get("state")

    retry_decorator = AWSRetry.jittered_backoff(
        catch_extra_error_codes=[
            "IncorrectState",
            "InsufficientInstanceCapacity",
            "InvalidInstanceID.NotFound",
        ]
    )
    client = module.client("ec2", retry_decorator=retry_decorator)

    filters = module.params.get("filters")
    if filters is None:
        filters = build_filters(client, module)

    try:
        existing_matches = []
        if filters:
            existing_matches = find_instances(client, module, filters=filters)

        if state in ("terminated", "absent"):
            if existing_matches:
                result = ensure_instance_state(client, module, state, filters)
            else:
                result = dict(
                    msg="No matching instances found",
                    changed=False,
                )
        elif module.params.get("exact_count"):
            result = enforce_count(client, module, existing_matches, desired_module_state=state, filters=filters)
        elif existing_matches and not module.params.get("count"):
            for match in existing_matches:
                warn_if_public_ip_assignment_changed(module, match)
                warn_if_cpu_options_changed(module, match)
            result = handle_existing(client, module, existing_matches, state, filters=filters)
        else:
            result = ensure_present(client, module, existing_matches=existing_matches, desired_module_state=state)
    except AnsibleEC2Error as e:
        if e.exception:
            module.fail_json_aws(e.exception, msg=e.message)
        module.fail_json(msg=e.message)

    module.exit_json(**result)


if __name__ == "__main__":
    main()
