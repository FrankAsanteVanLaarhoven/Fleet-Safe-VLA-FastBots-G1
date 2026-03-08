#!/bin/bash
set -e

# Constants
REGION="us-central1"
ZONE="us-central1-a"
VM_NAME="isaac-l4-dev"
MACHINE_TYPE="g2-standard-4"
IMAGE_FAMILY="ubuntu-2204-lts"
IMAGE_PROJECT="ubuntu-os-cloud"
DISK_SIZE="200GB"
DISK_TYPE="pd-balanced"
ACCELERATOR="count=1,type=nvidia-l4"
ACCOUNT="frankleroyvan@gmail.com"

echo "=========================================="
echo "    Isaac Sim GCP L4 Auto-Provisioner    "
echo "=========================================="

# 1. Check Authentication
ACTIVE_ACCOUNT=$(gcloud config get-value account 2>/dev/null)
if [[ "$ACTIVE_ACCOUNT" != "$ACCOUNT" ]]; then
    echo "Current account is $ACTIVE_ACCOUNT."
    echo "Authenticating as $ACCOUNT... (A browser window will open)"
    gcloud auth login $ACCOUNT --no-launch-browser || gcloud auth login $ACCOUNT
    gcloud config set account $ACCOUNT
else
    echo "Already authenticated as $ACCOUNT."
fi

# Try to find the user's project ID for "My First Project"
PROJECT_ID=$(gcloud projects list --filter="name:'My First Project'" --format="value(projectId)" || echo "")
if [[ -z "$PROJECT_ID" ]]; then
    # Fallback to current configured project
    PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
fi

if [[ -z "$PROJECT_ID" ]]; then
    echo "ERROR: Could not determine Project ID. Please set it manually using 'gcloud config set project [PROJECT_ID]'"
    exit 1
fi

echo "Setting active project to: $PROJECT_ID"
gcloud config set project $PROJECT_ID

echo "Enabling Compute Engine API..."
gcloud services enable compute.googleapis.com

# 2. Check GPU Quota (NVIDIA L4 in us-central1)
echo "Checking L4 GPU Quota in $REGION..."
L4_QUOTA=$(gcloud compute regions describe $REGION --format="json" | jq -r '.quotas[] | select(.metric=="NVIDIA_L4_GPUS") | .limit' 2>/dev/null || echo "0.0")
if [[ "$L4_QUOTA" == "0.0" ]] || [[ -z "$L4_QUOTA" ]]; then
    echo "WARNING: NVIDIA_L4_GPUS quota in $REGION appears to be 0 or null."
    echo "Please ensure you have requested an L4 quota increase in the GCP Console under IAM & Admin -> Quotas."
    echo "The script will attempt to proceed, but VM creation may fail if quota is not approved."
else
    echo "L4 GPU Quota limits: $L4_QUOTA"
fi

# 3. Create Firewall Rules (if not existing)
echo "Ensuring firewall rules allow HTTP/HTTPS..."
gcloud compute firewall-rules create allow-http-https-isaac \
    --direction=INGRESS \
    --priority=1000 \
    --network=default \
    --action=ALLOW \
    --rules=tcp:80,tcp:443 \
    --source-ranges=0.0.0.0/0 \
    --target-tags=http-server,https-server || echo "Firewall rule already exists."

# 4. Provision the VM
echo "Creating VM: $VM_NAME in $ZONE..."
gcloud compute instances create $VM_NAME \
    --project=$PROJECT_ID \
    --zone=$ZONE \
    --machine-type=$MACHINE_TYPE \
    --accelerator=$ACCELERATOR \
    --maintenance-policy=TERMINATE \
    --image-family=$IMAGE_FAMILY \
    --image-project=$IMAGE_PROJECT \
    --boot-disk-size=$DISK_SIZE \
    --boot-disk-type=$DISK_TYPE \
    --tags=http-server,https-server \
    --scopes=https://www.googleapis.com/auth/cloud-platform || echo "VM might already exist. Proceeding to setup."

# 5. Wait for SSH to be ready
echo "Waiting for VM SSH to become available (sleeping for 30s)..."
sleep 30
echo "Attempting to establish SSH keys and ensure connectivity..."
gcloud compute ssh $VM_NAME --zone=$ZONE --project=$PROJECT_ID --command="echo 'SSH is ready!'" || sleep 15 && gcloud compute ssh $VM_NAME --zone=$ZONE --project=$PROJECT_ID --command="echo 'SSH is ready!'"

# 6. Prepare the SSH Payload
cat << 'EOF' > install_isaac_deps.sh
#!/bin/bash
set -e
export DEBIAN_FRONTEND=noninteractive

echo "Running VM setup inside $HOSTNAME..."
sudo apt update && sudo apt upgrade -y

# Check if NVIDIA driver is installed
if ! command -v nvidia-smi &> /dev/null; then
    echo "Installing NVIDIA drivers..."
    sudo apt install -y linux-headers-$(uname -r)
    sudo apt install -y nvidia-driver-535
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Installing Docker..."
    sudo apt-get update
    sudo apt-get install -y ca-certificates curl gnupg
    sudo install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor --yes -o /etc/apt/keyrings/docker.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt-get update
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io
    sudo usermod -aG docker $USER
fi

# Install NVIDIA Container Toolkit
if ! dpkg -l | grep -q nvidia-container-toolkit; then
    echo "Installing NVIDIA Container Toolkit..."
    distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
    curl -s -L https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor --yes -o /usr/share/keyrings/nvidia-container-toolkit.gpg
    curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | \
      sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit.gpg] https://#g' | \
      sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
    sudo apt-get update
    sudo apt-get install -y nvidia-container-toolkit
    sudo nvidia-ctk runtime configure --runtime=docker
    sudo systemctl restart docker
fi

echo "Creating Isaac Sim workspace..."
mkdir -p /home/$USER/isaac-sim

echo "Creating Isaac Sim launch script..."
cat << 'LAUNCH' > /home/$USER/launch_isaac_sim.sh
#!/bin/bash
docker pull nvcr.io/nvidia/isaac-sim:4.2.0
docker run --name isaac-sim --entrypoint bash -it --rm --gpus all \
  --network host \
  -v ~/isaac-sim:/isaac-sim \
  nvcr.io/nvidia/isaac-sim:4.2.0
LAUNCH
chmod +x /home/$USER/launch_isaac_sim.sh

echo "Done! Initializing reboot to load new nvidia kernels. Run ~/launch_isaac_sim.sh after reboot."
EOF

# 7. Execute Payload via gcloud scp and ssh
echo "Copying setup payload to $VM_NAME..."
gcloud compute scp install_isaac_deps.sh $VM_NAME:~/install_isaac_deps.sh --zone=$ZONE --project=$PROJECT_ID

echo "Executing setup payload on $VM_NAME via SSH..."
gcloud compute ssh $VM_NAME --zone=$ZONE --project=$PROJECT_ID --command="chmod +x ~/install_isaac_deps.sh && ~/install_isaac_deps.sh" || echo "Execution completed or rebooted."

echo "=========================================="
echo "    Isaac Sim Setup Complete!             "
echo "=========================================="
echo "To ssh into the instance, run:"
echo "gcloud compute ssh $VM_NAME --zone=$ZONE --project=$PROJECT_ID"
echo "Note: The VM may be rebooting due to driver install, wait 2 mins before SSHing."
