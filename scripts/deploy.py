"""
Universal deployment script for any agent in the platform
"""
import subprocess
import sys
import os
import json
from pathlib import Path
from typing import Dict, List

def get_agent_config(agent_name: str) -> Dict:
    """Get configuration for specific agent"""
    configs = {
        "ben-nutritionist": {
            "display_name": "Ben Boulanger Nutrition Expert",
            "port": 8080,
            "env_vars": {
                "OPENAI_API_KEY": True,  # Required
                "PROJECT_ID": False,     # Optional
            },
            "special_files": ["chroma_db", "documents"],
            "docker_tag": "ben-nutrition"
        },
        "fitness-coach": {
            "display_name": "Fitness Coach",
            "port": 8081,
            "env_vars": {
                "OPENAI_API_KEY": True,
            },
            "special_files": [],
            "docker_tag": "fitness-coach"
        },
        "wellness-therapist": {
            "display_name": "Wellness Therapist", 
            "port": 8082,
            "env_vars": {
                "OPENAI_API_KEY": True,
            },
            "special_files": [],
            "docker_tag": "wellness-therapist"
        },
        "gateway": {
            "display_name": "API Gateway",
            "port": 8000,
            "env_vars": {
                "OPENAI_API_KEY": True,
            },
            "special_files": [],
            "docker_tag": "api-gateway"
        }
    }
    
    return configs.get(agent_name, {})

def check_requirements(agent_name: str, config: Dict) -> bool:
    """Check if all requirements are met"""
    print(f"🔍 Checking requirements for {config.get('display_name', agent_name)}...")
    
    # Check if agent directory exists
    agent_path = Path(f"agents/{agent_name}")
    if agent_name != "gateway" and not agent_path.exists():
        print(f"❌ Agent directory not found: {agent_path}")
        return False
    
    # Check environment variables
    missing_vars = []
    for var, required in config.get("env_vars", {}).items():
        if required and not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        return False
    
    print("✅ All requirements met")
    return True

def build_docker_image(agent_name: str, config: Dict) -> bool:
    """Build Docker image for agent"""
    print(f"🔨 Building Docker image for {agent_name}...")
    
    try:
        # Determine build context
        if agent_name == "gateway":
            context = "gateway"
            dockerfile = "gateway/Dockerfile"
        else:
            context = "."  # Build from root to access shared modules
            dockerfile = f"agents/{agent_name}/Dockerfile"
        
        # Create Dockerfile if it doesn't exist
        dockerfile_path = Path(dockerfile)
        if not dockerfile_path.exists():
            create_dockerfile(agent_name, dockerfile_path)
        
        # Build command
        tag = config.get("docker_tag", agent_name)
        cmd = [
            "docker", "build",
            "-f", dockerfile,
            "-t", f"ai-platform/{tag}:latest",
            context
        ]
        
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Docker image built successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Docker build failed: {e.stderr}")
        return False

def create_dockerfile(agent_name: str, dockerfile_path: Path) -> None:
    """Create Dockerfile for agent"""
    dockerfile_path.parent.mkdir(parents=True, exist_ok=True)
    
    if agent_name == "gateway":
        dockerfile_content = """FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy gateway code
COPY gateway/ .
COPY shared/ shared/

# Copy agent modules for imports
COPY agents/ agents/

EXPOSE 8000

CMD ["python", "main.py"]
"""
    else:
        dockerfile_content = f"""FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared modules
COPY shared/ shared/

# Copy agent-specific code
COPY agents/{agent_name}/ .

# Copy special directories if they exist
{"COPY agents/ben-nutritionist/chroma_db/ chroma_db/" if agent_name == "ben-nutritionist" else ""}
{"COPY agents/ben-nutritionist/documents/ documents/" if agent_name == "ben-nutritionist" else ""}

EXPOSE 8080

CMD ["python", "app.py"]
"""
    
    dockerfile_path.write_text(dockerfile_content)
    print(f"📝 Created Dockerfile: {dockerfile_path}")

def run_local(agent_name: str, config: Dict) -> None:
    """Run agent locally"""
    print(f"🚀 Starting {config.get('display_name', agent_name)} locally...")
    
    try:
        if agent_name == "gateway":
            os.chdir("gateway")
            subprocess.run([sys.executable, "main.py"], check=True)
        else:
            os.chdir(f"agents/{agent_name}")
            subprocess.run([sys.executable, "app.py"], check=True)
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start agent: {e}")
    except KeyboardInterrupt:
        print(f"\n🛑 Stopped {config.get('display_name', agent_name)}")

def run_docker(agent_name: str, config: Dict) -> None:
    """Run agent in Docker"""
    print(f"🐳 Running {config.get('display_name', agent_name)} in Docker...")
    
    try:
        tag = config.get("docker_tag", agent_name)
        port = config.get("port", 8080)
        
        # Prepare environment variables
        env_args = []
        for var in config.get("env_vars", {}):
            value = os.getenv(var)
            if value:
                env_args.extend(["-e", f"{var}={value}"])
        
        cmd = [
            "docker", "run",
            "--rm",
            "-p", f"{port}:{port if agent_name != 'gateway' else 8000}",
            *env_args,
            f"ai-platform/{tag}:latest"
        ]
        
        subprocess.run(cmd, check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Docker run failed: {e}")
    except KeyboardInterrupt:
        print(f"\n🛑 Stopped Docker container")

def deploy_gcp(agent_name: str, config: Dict) -> None:
    """Deploy agent to Google Cloud Platform"""
    print(f"☁️ Deploying {config.get('display_name', agent_name)} to GCP...")
    
    try:
        # Use Terraform to deploy
        terraform_dir = Path(f"infrastructure/terraform/agents/{agent_name}")
        if terraform_dir.exists():
            os.chdir(terraform_dir)
            subprocess.run(["terraform", "init"], check=True)
            subprocess.run(["terraform", "apply", "-auto-approve"], check=True)
        else:
            print(f"❌ Terraform configuration not found: {terraform_dir}")
            
    except subprocess.CalledProcessError as e:
        print(f"❌ GCP deployment failed: {e}")

def main():
    if len(sys.argv) < 3:
        print("Usage: python deploy.py <agent_name> <action>")
        print("Agent names: ben-nutritionist, fitness-coach, wellness-therapist, gateway")
        print("Actions: local, docker, build, gcp")
        sys.exit(1)
    
    agent_name = sys.argv[1]
    action = sys.argv[2]
    
    config = get_agent_config(agent_name)
    if not config:
        print(f"❌ Unknown agent: {agent_name}")
        sys.exit(1)
    
    if not check_requirements(agent_name, config):
        sys.exit(1)
    
    if action == "local":
        run_local(agent_name, config)
    elif action == "build":
        build_docker_image(agent_name, config)
    elif action == "docker":
        if build_docker_image(agent_name, config):
            run_docker(agent_name, config)
    elif action == "gcp":
        if build_docker_image(agent_name, config):
            deploy_gcp(agent_name, config)
    else:
        print(f"❌ Unknown action: {action}")
        sys.exit(1)

if __name__ == "__main__":
    main()