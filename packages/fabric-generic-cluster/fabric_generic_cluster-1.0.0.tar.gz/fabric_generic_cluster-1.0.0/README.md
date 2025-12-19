# FABRIC Slice Management Framework

A comprehensive, type-safe Python framework for managing FABRIC testbed slices with support for complex network topologies, DPU interfaces, multi-OS configurations, and various hardware components.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Pydantic V2](https://img.shields.io/badge/pydantic-v2-orange.svg)](https://docs.pydantic.dev/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## 🌟 Features

### Core Capabilities
- ✅ **Type-Safe Data Models** - Pydantic-based topology definitions with automatic validation
- ✅ **DPU Interface Support** - Full support for DPU network interfaces alongside traditional NICs
- ✅ **Multi-OS Support** - Automatic detection and configuration for Rocky Linux, Ubuntu, and Debian
- ✅ **Hardware Components** - Full support for GPUs, FPGAs, DPUs, NVMe, and custom NICs
- ✅ **Network Management** - L2/L3 network configuration with IPv4/IPv6 support
- ✅ **SSH Automation** - Passwordless SSH setup across all nodes
- ✅ **Visualization** - Multiple output formats (text, ASCII, graphs, tables)
- ✅ **Backward Compatible** - Works with existing dict-based code
- ✅ **Modular Design** - Separated concerns for better maintainability

### Hardware Support
- **GPUs** - NVIDIA RTX series, Tesla T4, A30, A40
- **FPGAs** - Xilinx Alveo U280, U50, U250
- **DPUs** - ConnectX-7 100G/400G Data Processing Units with network interfaces
- **NVMe** - Intel P4510, P4610 NVMe storage
- **NICs** - Basic, ConnectX-5, ConnectX-6, SharedNICs, SmartNICs
- **Persistent Storage** - Volume management

## 📋 Table of Contents

- [Installation](#installation)
- [Directory Structure](#directory-structure)
- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [Usage Examples](#usage-examples)
- [YAML Topology Format](#yaml-topology-format)
- [API Reference](#api-reference)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

## 🚀 Installation

### Prerequisites

- Python 3.9 or higher
- Access to FABRIC JupyterHub or local FABRIC environment
- `fabrictestbed-extensions` (usually pre-installed in FABRIC JupyterHub)

### Install Dependencies

```bash
# Clone the repository
git clone https://github.com/yourusername/fabric-slice-management.git
cd fabric-slice-management

# Install required packages
pip install -r requirements.txt
```

### Environment Setup

For a guided setup, use the environment setup notebook:

```bash
jupyter notebook notebooks/notebook-aux-setup-environment.ipynb
```

Or install directly:

```bash
pip install -r requirements.txt
```

## 📁 Directory Structure

```
.
├── docs/                           # Documentation
│   ├── AUXILIARY_NOTEBOOKS.md
│   ├── l3_network_workflow.md
│   ├── yaml_migration_guide.md
│   └── YAML_QUICK_REFERENCE.md
│
├── examples/                       # Example deployment scripts
│   └── complete-deployment-example.py
│
├── model/                          # Topology YAML files
│   ├── _slice_topology.yaml
│   └── _slice_topology_*.yaml
│
├── notebooks/                      # Jupyter notebooks
│   ├── notebook-aux-*.ipynb
│   └── notebook-create-slice-*.ipynb
│
├── scripts/                        # Utility scripts
│   ├── reorganize_repository.sh
│   └── setup_repo.sh
│
├── test/                          # Test files
│   ├── test_migration.py
│   ├── test_fpga_support.py
│   └── test_dpu_support.py
│
├── slice_deployment.py            # Core modules (root)
├── slice_network_config.py
├── slice_ssh_setup.py
├── slice_topology_viewer.py
├── slice_utils_builder_compat.py
├── slice_utils_models.py
├── tool_topology_summary_generator.py
│
├── README.md
└── requirements.txt
```

## 🎯 Quick Start

### Option 1: Full Deployment Script

Deploy everything with one command:

```bash
python examples/complete-deployment-example.py \
    --yaml model/_slice_topology.yaml \
    --slice-name my-test-slice
```

This will:
1. Load and validate topology
2. Deploy slice to FABRIC
3. Configure L3 networks (if any)
4. Configure all interfaces (DPU + NIC)
5. Setup passwordless SSH
6. Test connectivity

### Option 2: Step-by-Step in Python/Notebook

#### Step 1: Load and Validate Topology

```python
from slice_utils_models import load_topology_from_yaml_file
import slice_deployment as sd

# Load topology (with automatic validation)
topology = load_topology_from_yaml_file("model/_slice_topology.yaml")

print(f"Loaded {len(topology.site_topology_nodes.nodes)} nodes")
print(f"Loaded {len(topology.site_topology_networks.networks)} networks")
```

#### Step 2: Deploy to FABRIC

```python
# Generate unique slice name
slice_name = sd.check_or_generate_unique_slice_name("my-slice")

# Deploy slice (creates nodes, NICs, DPUs, GPUs, FPGAs, etc.)
slice = sd.deploy_topology_to_fabric(topology, slice_name)

# Wait for slice to become active
slice.wait(timeout=600, interval=30, progress=True)
```

#### Step 3: Configure L3 Networks (if applicable)

If your topology includes IPv4/IPv6/IPv4Ext/IPv6Ext networks:

```python
# Configure L3 networks (assigns IPs from orchestrator)
sd.configure_l3_networks(slice, topology)
```

#### Step 4: Configure Network Interfaces

This configures **both NIC and DPU interfaces**:

```python
import slice_network_config as snc

# Configure all interfaces (auto-detects OS: Rocky/Ubuntu/Debian)
snc.configure_node_interfaces(slice, topology)

# Verify configuration
snc.verify_node_interfaces(slice, topology)
```

#### Step 5: Setup SSH Access

```python
import slice_ssh_setup as ssh

# Complete SSH setup (keys, distribution, config)
ssh.setup_passwordless_ssh(slice)

# Verify SSH connectivity
ssh_results = ssh.verify_ssh_access(
    slice, topology, "node-1", "network_1"
)
```

#### Step 6: Test Connectivity

```python
# Ping test
results = snc.ping_network_from_node(
    slice, topology, "node-1", "network_1", count=3
)

if all(results.values()):
    print("✅ All connectivity tests passed!")
```

### Option 3: Using Notebooks

```python
# In a Jupyter notebook (from notebooks/ directory)
import sys
sys.path.insert(0, '..')  # Add parent directory to path

from slice_utils_models import load_topology_from_yaml_file
import slice_deployment as sd

# Load topology
topology = load_topology_from_yaml_file("../model/_slice_topology.yaml")

# Deploy slice
slice = sd.deploy_topology_to_fabric(topology, "my-slice")
```

## 🗂️ Architecture

### Core Modules (Root Level)

- **`slice_utils_models.py`** - Pydantic models for type-safe topology definitions
- **`slice_deployment.py`** - Slice creation, network binding, and deployment
- **`slice_network_config.py`** - Network interface configuration (supports all Linux distros)
- **`slice_ssh_setup.py`** - SSH key management and passwordless access
- **`slice_topology_viewer.py`** - Topology visualization and summary tools
- **`slice_utils_builder_compat.py`** - Backward compatibility layer
- **`tool_topology_summary_generator.py`** - CLI tool for generating YAML summaries

### Design Principles

1. **Separation of Concerns** - Each module has a single, well-defined responsibility
2. **Type Safety** - Pydantic models provide runtime validation and IDE support
3. **Flexibility** - Works with both new models and legacy dict formats
4. **Extensibility** - Easy to add new hardware types or features
5. **Documentation** - Comprehensive docstrings and examples

### Network Configuration Flow

The framework handles both **L2 (manual)** and **L3 (orchestrator-managed)** networks:

**L2 Networks** (L2Bridge, L2PTP, L2STS):
1. IP addresses defined in YAML topology
2. `configure_node_interfaces()` applies these IPs to interfaces
3. Works on both NIC and DPU interfaces

**L3 Networks** (IPv4, IPv6, IPv4Ext, IPv6Ext):
1. `configure_l3_networks()` gets IPs from orchestrator
2. Assigns IPs to interfaces via FABRIC API
3. `configure_node_interfaces()` makes configuration persistent
4. For external networks, enables public routing

## 📚 Usage Examples

### Example 1: Access Topology Data (Type-Safe)

```python
# Get specific node
node = topology.get_node_by_hostname("lc-1")

print(f"Node: {node.hostname}")
print(f"Site: {node.site}")
print(f"CPU: {node.capacity.cpu} cores")
print(f"RAM: {node.capacity.ram} GB")

# Check hardware
if node.pci.fpga:
    print(f"FPGAs: {len(node.pci.fpga)}")
    for fpga in node.pci.fpga.values():
        print(f"  - {fpga.name}: {fpga.model}")

if node.pci.dpu:
    print(f"DPUs: {len(node.pci.dpu)}")
    for dpu in node.pci.dpu.values():
        print(f"  - {dpu.name}: {dpu.model}")
        print(f"    Interfaces: {len(dpu.interfaces)}")
```

### Example 2: Query Networks and Interfaces

```python
# Get nodes on a specific network
nodes_on_net1 = topology.get_nodes_on_network("network_1")

print(f"Nodes on network_1:")
for node in nodes_on_net1:
    # This returns interfaces from BOTH NICs and DPUs
    interfaces = node.get_interfaces_for_network("network_1")
    for device_name, iface in interfaces:
        ip = iface.get_ipv4_address()
        device_type = "DPU" if device_name.startswith("dpu") else "NIC"
        print(f"  - {node.hostname} ({device_type} {device_name}): {ip}")
```

### Example 3: Visualization

```python
import slice_topology_viewer as viewer

# Print detailed summary
viewer.print_topology_summary(topology)

# Print compact table
viewer.print_compact_summary(topology)

# Generate ASCII diagram
viewer.print_ascii_topology(topology)

# Draw graph
viewer.draw_topology_graph(
    topology, 
    figsize=(14, 10),
    show_ip=True, 
    save_path="topology.png"
)
```

### Example 4: Generate YAML Summary

```python
# Inject summary header into YAML file
viewer.inject_summary_into_yaml_file("model/_slice_topology.yaml", topology)

# Or use command line
!python tool_topology_summary_generator.py model/_slice_topology.yaml
```

### Example 5: OpenStack Role Queries

```python
# Find control nodes
control_nodes = [
    node for node in topology.site_topology_nodes.iter_nodes()
    if node.specific.openstack.is_control()
]

print(f"Control nodes: {[n.hostname for n in control_nodes]}")

# Find compute nodes
compute_nodes = [
    node for node in topology.site_topology_nodes.iter_nodes()
    if node.specific.openstack.is_compute()
]

print(f"Compute nodes: {[n.hostname for n in compute_nodes]}")
```

### Example 6: Working with DPU Interfaces

```python
# Get all interfaces (includes both NIC and DPU)
all_interfaces = node.get_all_interfaces()

print(f"Total interfaces: {len(all_interfaces)}")

for device_name, iface_name, iface in all_interfaces:
    device_type = "DPU" if device_name.startswith("dpu") else "NIC"
    print(f"{device_type} {device_name}.{iface_name}:")
    print(f"  Binding: {iface.binding}")
    print(f"  IPv4: {iface.get_ipv4_address()}")
```

## 📄 YAML Topology Format

### Complete Node Example with DPU

```yaml
site_topology_nodes:
  nodes:
    node1:
      name: lc-1
      hostname: lc-1
      site: PSC
      
      capacity:
        cpu: 4
        ram: 32
        disk: 100
        os: default_rocky_9
      
      persistent_storage:
        volume:
          volume1:
            name: FABRIC_Staff_1T
            size: 1000
      
      pci:
        dpu:
          dpu1:
            name: dpu1
            model: NIC_ConnectX_7_100
            interfaces:
              iface1:
                device: eth1
                connection: conn-eth1
                binding: net_local_1
                ipv4:
                  address: 192.168.201.200/24
                  gateway: 192.168.201.1
                  dns: 8.8.8.8
                ipv6:
                  address: ''
                  gateway: ''
                  dns: ''
        
        fpga:
          fpga1:
            name: fpga1
            model: FPGA_Xilinx_U280
        
        gpu:
          gpu1:
            name: rtx6000
            model: GPU_RTX6000
        
        nvme:
          nvme1:
            name: nvme1
            model: NVME_P4510
        
        network:
          nic1:
            name: nic1
            model: NIC_Basic
            interfaces:
              iface1:
                device: eth2
                connection: conn-eth2
                binding: net_local_1
                ipv4:
                  address: 192.168.201.211/24
                  gateway: 192.168.201.1
                  dns: 8.8.8.8
                ipv6:
                  address: ''
                  gateway: ''
                  dns: ''
      
      specific:
        openstack:
          control: 'true'
          network: 'true'
          compute: 'false'
          storage: 'true'

site_topology_networks:
  networks:
    net1:
      name: net_local_1
      type: L2Bridge
      subnet:
        ipv4:
          address: 192.168.201.0/24
          gateway: 192.168.201.1
        ipv6:
          address: ''
          gateway: ''
```

### Supported Network Types

**L2 Networks** (Manual IP Configuration):
- `L2Bridge` - Ethernet bridge network
- `L2PTP` - Point-to-point Ethernet
- `L2STS` - Stitched network to external facilities

**L3 Networks** (Orchestrator-Managed):
- `IPv4` - Private IPv4 network (IPs auto-assigned)
- `IPv6` - Private IPv6 network (IPs auto-assigned)
- `IPv4Ext` - Public IPv4 network with internet access
- `IPv6Ext` - Public IPv6 network with internet access

### Supported Operating Systems

- `default_rocky_9` - Rocky Linux 9
- `default_ubuntu_24` - Ubuntu 24.04
- `default_ubuntu_22` - Ubuntu 22.04
- `default_debian_11` - Debian 11
- `default_debian_12` - Debian 12

### Supported Hardware Models

**DPUs:**
- `NIC_ConnectX_7_100` - ConnectX-7 100G DPU
- `NIC_ConnectX_7_400` - ConnectX-7 400G DPU

**NICs:**
- `NIC_Basic` - Basic NIC
- `NIC_ConnectX_5` - ConnectX-5 SmartNIC
- `NIC_ConnectX_6` - ConnectX-6 SmartNIC

**GPUs:**
- `GPU_RTX6000` - NVIDIA RTX 6000
- `GPU_Tesla_T4` - NVIDIA Tesla T4
- `GPU_A30` - NVIDIA A30
- `GPU_A40` - NVIDIA A40

**FPGAs:**
- `FPGA_Xilinx_U280` - Xilinx Alveo U280
- `FPGA_Xilinx_U50` - Xilinx Alveo U50
- `FPGA_Xilinx_U250` - Xilinx Alveo U250

**NVMe:**
- `NVME_P4510` - Intel P4510
- `NVME_P4610` - Intel P4610

## 🔧 API Reference

### slice_utils_models

```python
# Load topology
topology = load_topology_from_yaml_file(path)
topology = load_topology_from_dict(data)

# Access data
node = topology.get_node_by_hostname(hostname)
network = topology.get_network_by_name(name)
nodes = topology.get_nodes_on_network(network_name)

# Node interface methods
all_interfaces = node.get_all_interfaces()  # Returns NIC + DPU interfaces
network_interfaces = node.get_interfaces_for_network(network_name)
```

### slice_deployment

```python
# Deployment
slice = deploy_topology_to_fabric(topology, slice_name, use_timestamp=False)
configure_l3_networks(slice, topology)  # For L3 networks only

# Management
slice = get_slice(slice_name)
delete_slice(slice_name)

# Utilities
check_slices()
show_config()
unique_name = check_or_generate_unique_slice_name(base_name)
```

### slice_network_config

```python
# Configuration
configure_node_interfaces(slice, topology)  # Configures NICs + DPUs
verify_node_interfaces(slice, topology)
update_hosts_file_on_nodes(slice, topology)

# Testing
results = ping_network_from_node(slice, topology, source_hostname, network_name, use_ipv6=False, count=3)
```

### slice_ssh_setup

```python
# SSH Setup
setup_passwordless_ssh(slice)
results = verify_ssh_access(slice, topology, source_hostname, network_name, use_ipv6=False)

# Individual operations
generate_ssh_keys_on_nodes(slice)
public_keys = collect_public_keys(slice)
distribute_ssh_keys(slice, public_keys)
disable_strict_host_key_checking(slice)
remove_ssh_keys(slice, remove_entire_ssh_dir=False)
```

### slice_topology_viewer

```python
# Summaries
print_topology_summary(topology)
print_compact_summary(topology)
print_ascii_topology(topology)
print_network_details(topology, network_name)

# Visualization
draw_topology_graph(topology, figsize=(14, 10), show_ip=True, save_path=None)

# YAML Generation
inject_summary_into_yaml_file(yaml_path, topology, include_ascii=True, backup=True)
summary = generate_yaml_summary(topology, include_ascii=True)

# Export
export_topology_to_json(topology, output_path)
export_topology_to_dot(topology, output_path)
```

## 🧪 Testing

### Run Test Suite

```bash
# Test all components
python test/test_migration.py
python test/test_fpga_support.py
python test/test_dpu_support.py
python test/test_summary_generator.py
```

### Manual Testing

```python
from slice_utils_models import load_topology_from_yaml_file

# Test loading
topology = load_topology_from_yaml_file("model/_slice_topology.yaml")
assert len(topology.site_topology_nodes.nodes) > 0

# Test DPU support
node = list(topology.site_topology_nodes.nodes.values())[0]
all_ifaces = node.get_all_interfaces()
print(f"Total interfaces (NIC + DPU): {len(all_ifaces)}")

# Test validation
assert node.hostname
assert node.capacity.cpu > 0

print("✅ All manual tests passed!")
```

## 🛠️ Troubleshooting

### Issue: Import Error in Notebooks

```python
ModuleNotFoundError: No module named 'slice_utils_models'
```

**Solution:** Add to the top of your notebook:
```python
import sys
sys.path.insert(0, '..')  # Add parent directory to path
```

### Issue: YAML File Not Found

```python
FileNotFoundError: _slice_topology.yaml
```

**Solution:** Update the path based on your location:
```python
# If in root directory
topology = load_topology_from_yaml_file("model/_slice_topology.yaml")

# If in notebooks/, test/, or examples/
topology = load_topology_from_yaml_file("../model/_slice_topology.yaml")
```

### Issue: NetworkManager Not Found on Debian

The framework auto-detects and supports:
- NetworkManager (Rocky Linux)
- netplan (Ubuntu 18.04+)
- systemd-networkd (Debian 11+)
- /etc/network/interfaces (old Debian/Ubuntu)

If you get errors, check the OS:

```python
node = slice.get_node("hostname")
stdout, _ = node.execute("cat /etc/os-release")
print(stdout)
```

### Issue: DPU Interfaces Not Configured

**Check if DPUs are in topology:**
```python
node = topology.site_topology_nodes.nodes['node1']
print(f"DPUs: {node.pci.dpu}")

# Verify interfaces
for dpu_name, dpu in node.pci.dpu.items():
    print(f"{dpu_name}: {len(dpu.interfaces)} interfaces")
```

**Verify all interfaces are found:**
```python
all_ifaces = node.get_all_interfaces()
print(f"Total: {len(all_ifaces)}")  # Should include NIC + DPU

for device_name, iface_name, iface in all_ifaces:
    device_type = "DPU" if device_name.startswith("dpu") else "NIC"
    print(f"{device_type} {device_name}.{iface_name} → {iface.binding}")
```

## 📖 Documentation

- [YAML Quick Reference](docs/YAML_QUICK_REFERENCE.md)
- [YAML Migration Guide](docs/yaml_migration_guide.md)
- [L3 Network Workflow](docs/l3_network_workflow.md)
- [Notebook Updates Guide](docs/notebook_updates_guide.md)
- [Auxiliary Notebooks](docs/AUXILIARY_NOTEBOOKS.md)

## 🤝 Contributing

Contributions are welcome! When adding new features:

1. Update the appropriate core module in the root directory
2. Add tests to the `test/` directory
3. Update documentation in `docs/`
4. Add example YAML to `model/` if needed
5. Update this README if adding new capabilities

### Development Setup

```bash
# Clone repository
git clone https://github.com/yourusername/fabric-slice-management.git
cd fabric-slice-management

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run tests
python test/test_migration.py
```

## 📊 Performance

- **Validation Speed**: ~10ms for typical topology (3-10 nodes)
- **Deployment Time**: Depends on FABRIC (typically 5-10 minutes)
- **Network Config**: ~30 seconds per node
- **SSH Setup**: ~1-2 minutes for 3-node cluster

## 🗺️ Roadmap

- [x] Type-safe Pydantic models
- [x] DPU interface support
- [x] Multi-distro support (Rocky/Ubuntu/Debian)
- [x] L2/L3 network configuration
- [x] Automated SSH setup
- [ ] Web-based topology editor
- [ ] Ansible playbook integration
- [ ] Monitoring and metrics collection
- [ ] Multi-site topology support
- [ ] REST API endpoint

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built for the [FABRIC Testbed](https://fabric-testbed.net/)
- Uses [Pydantic](https://docs.pydantic.dev/) for data validation
- Network visualization with [NetworkX](https://networkx.org/) and [Matplotlib](https://matplotlib.org/)

## 📞 Support

- 📧 Email: support@fabric-testbed.net
- 💬 Slack: [FABRIC Workspace](https://fabric-testbed.slack.com)
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/fabric-slice-management/issues)

---

**Made with ❤️ for the FABRIC Community**
