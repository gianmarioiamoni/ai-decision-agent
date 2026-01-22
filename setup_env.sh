#!/bin/bash
# setup_env.sh - Load environment variables correctly (no newlines)

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🔧 Loading environment variables...${NC}"

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Please create it from env.example${NC}"
    exit 1
fi

# Export each variable, stripping newlines
while IFS='=' read -r key value; do
    # Skip comments and empty lines
    [[ "$key" =~ ^#.*$ ]] && continue
    [[ -z "$key" ]] && continue
    
    # Remove quotes and newlines
    value=$(echo "$value" | sed 's/^["'\'']//;s/["'\'']$//' | tr -d '\n\r')
    
    # Export variable
    export "$key=$value"
    
    echo -e "${GREEN}✅ Loaded: $key${NC}"
done < .env

echo -e "${GREEN}✅ Environment variables loaded successfully!${NC}"
echo -e "${YELLOW}💡 You can now run: python app/ui/rag_test_advanced.py or ./run_app.sh${NC}"

