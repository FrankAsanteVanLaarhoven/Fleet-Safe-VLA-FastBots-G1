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
