import ipaddress

# Your CIDR blocks
vpc_cidr = "10.192.0.0/16"  # VPC
subnet_cidrs = [
    "10.192.10.0/24",  # Public subnet 1a
    "10.192.11.0/24",  # Public subnet 1b
    "10.192.20.0/24",  # Private subnet 1a
    "10.192.21.0/24"   # Private subnet 1b
]

# Convert to network objects
vpc_network = ipaddress.ip_network(vpc_cidr)
subnet_networks = [ipaddress.ip_network(cidr) for cidr in subnet_cidrs]

# Check if all subnets are within VPC CIDR
print(f"Checking if all subnets are within VPC CIDR {vpc_cidr}:")
for i, subnet in enumerate(subnet_networks):
    if subnet.subnet_of(vpc_network):
        print(f"✓ {subnet_cidrs[i]} is properly contained in the VPC")
    else:
        print(f"❌ ERROR: {subnet_cidrs[i]} is NOT contained in the VPC")

# Check for overlaps between subnets
print("\nChecking for problematic overlaps between subnets:")
has_subnet_overlaps = False
for i, subnet1 in enumerate(subnet_networks):
    for j, subnet2 in enumerate(subnet_networks[i+1:], i+1):
        if subnet1.overlaps(subnet2):
            print(f"❌ PROBLEM: {subnet_cidrs[i]} overlaps with {subnet_cidrs[j]}")
            has_subnet_overlaps = True

if not has_subnet_overlaps:
    print("✓ No subnet overlaps found - your subnet configuration is correct")