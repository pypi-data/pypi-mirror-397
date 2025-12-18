#!/bin/bash
#
# Eeveon CI/CD Monitor Script
# Continuously monitors GitHub repository for new commits
#

set -e

# Get project name from argument
PROJECT_NAME="$1"

if [ -z "$PROJECT_NAME" ]; then
    echo "Usage: $0 <project-name>"
    exit 1
fi

# Base directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
CONFIG_FILE="$BASE_DIR/config/pipeline.json"
LOG_DIR="$BASE_DIR/logs"
DEPLOY_SCRIPT="$SCRIPT_DIR/deploy.sh"

# Ensure log directory exists
mkdir -p "$LOG_DIR"

# Log function
log() {
    local level="$1"
    shift
    local message="$@"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local log_file="$LOG_DIR/deploy-$(date '+%Y-%m-%d').log"
    
    echo "[$timestamp] [$level] [$PROJECT_NAME] $message" | tee -a "$log_file"
}

# Check if jq is installed
if ! command -v jq &> /dev/null; then
    log "ERROR" "jq is not installed. Please install it: sudo apt install jq"
    exit 1
fi

# Load project configuration
if [ ! -f "$CONFIG_FILE" ]; then
    log "ERROR" "Configuration file not found: $CONFIG_FILE"
    exit 1
fi

# Extract project configuration
REPO_URL=$(jq -r ".\"$PROJECT_NAME\".repo_url" "$CONFIG_FILE")
BRANCH=$(jq -r ".\"$PROJECT_NAME\".branch" "$CONFIG_FILE")
POLL_INTERVAL=$(jq -r ".\"$PROJECT_NAME\".poll_interval" "$CONFIG_FILE")
DEPLOYMENT_DIR=$(jq -r ".\"$PROJECT_NAME\".deployment_dir" "$CONFIG_FILE")
LAST_COMMIT=$(jq -r ".\"$PROJECT_NAME\".last_commit // empty" "$CONFIG_FILE")

if [ "$REPO_URL" == "null" ]; then
    log "ERROR" "Project '$PROJECT_NAME' not found in configuration"
    exit 1
fi

log "INFO" "Starting monitor for project: $PROJECT_NAME"
log "INFO" "Repository: $REPO_URL"
log "INFO" "Branch: $BRANCH"
log "INFO" "Poll interval: ${POLL_INTERVAL}s"

# Clone repository if it doesn't exist
REPO_DIR="$DEPLOYMENT_DIR/repo"
if [ ! -d "$REPO_DIR/.git" ]; then
    log "INFO" "Cloning repository..."
    git clone --branch "$BRANCH" "$REPO_URL" "$REPO_DIR"
    
    if [ $? -eq 0 ]; then
        log "SUCCESS" "Repository cloned successfully"
        # Get initial commit
        cd "$REPO_DIR"
        CURRENT_COMMIT=$(git rev-parse HEAD)
        
        # Update config with initial commit
        jq ".\"$PROJECT_NAME\".last_commit = \"$CURRENT_COMMIT\"" "$CONFIG_FILE" > "$CONFIG_FILE.tmp"
        mv "$CONFIG_FILE.tmp" "$CONFIG_FILE"
        
        log "INFO" "Initial commit: $CURRENT_COMMIT"
    else
        log "ERROR" "Failed to clone repository"
        exit 1
    fi
fi

# Main monitoring loop
log "INFO" "Monitoring started. Checking every ${POLL_INTERVAL} seconds..."

while true; do
    cd "$REPO_DIR"
    
    # Fetch latest changes
    git fetch origin "$BRANCH" &> /dev/null
    
    if [ $? -ne 0 ]; then
        log "WARNING" "Failed to fetch from remote"
        sleep "$POLL_INTERVAL"
        continue
    fi
    
    # Get remote commit hash
    REMOTE_COMMIT=$(git rev-parse "origin/$BRANCH")
    
    # Get current local commit
    LOCAL_COMMIT=$(git rev-parse HEAD)
    
    # Check if there are new commits
    if [ "$REMOTE_COMMIT" != "$LOCAL_COMMIT" ]; then
        log "INFO" "New commit detected!"
        log "INFO" "Local:  $LOCAL_COMMIT"
        log "INFO" "Remote: $REMOTE_COMMIT"
        
        # Get commit message
        COMMIT_MSG=$(git log -1 --pretty=format:"%s" "$REMOTE_COMMIT")
        log "INFO" "Commit message: $COMMIT_MSG"
        
        # Trigger deployment
        log "INFO" "Triggering deployment..."
        
        if bash "$DEPLOY_SCRIPT" "$PROJECT_NAME"; then
            log "SUCCESS" "Deployment completed successfully"
            
            # Update last commit in config
            jq ".\"$PROJECT_NAME\".last_commit = \"$REMOTE_COMMIT\"" "$CONFIG_FILE" > "$CONFIG_FILE.tmp"
            mv "$CONFIG_FILE.tmp" "$CONFIG_FILE"
        else
            log "ERROR" "Deployment failed"
        fi
    else
        log "INFO" "No new commits (current: ${LOCAL_COMMIT:0:7})"
    fi
    
    # Wait for next poll
    sleep "$POLL_INTERVAL"
done
