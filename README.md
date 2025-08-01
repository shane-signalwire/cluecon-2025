# Max Electric Payment Demo

A demonstration application showcasing **secure voice-based payment processing** using SignalWire's AI Agent technology and Call Widget. This app simulates a fictional electric company (Max Electric) where customers can call to pay outstanding balances through a safe and secure voice interface.

## 🎯 **What This Demo Does**

This application demonstrates:

- **Voice-First Payment Processing**: Customers make calls using SignalWire's Call Widget to handle payment transactions
- **AI-Powered Customer Service**: An intelligent agent processes payment requests using natural language
- **Secure DTMF Input**: Customers can input sensitive payment information via keypad tones
- **Real-Time Customer Data**: Integration with customer database for balance lookups and payment processing
- **Modern Web Interface**: Clean, responsive dashboard with SignalWire-themed design

### **Demo Scenario**
1. Customer visits the Max Electric dashboard and sees their outstanding balance
2. Customer clicks "Call Support for Payment" to initiate a voice call
3. AI Agent greets the customer and offers payment assistance
4. Customer provides payment information via voice or DTMF keypad
5. Agent processes the payment and confirms the transaction

## 🏗️ **Application Architecture**

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Web Frontend  │    │   Flask Backend  │    │ SignalWire AI   │
│                 │    │                  │    │     Agent       │
│  • Dashboard    │◄──►│  • Customer API  │◄──►│                 │
│  • Call Widget  │    │  • Agent Routes  │    │ • Payment Funcs │
│  • DTMF Support │    │  • SWML Webhooks │    │ • Balance Lookup│
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │                        │
         │              ┌─────────▼─────────┐              │
         │              │   SQLite Database │              │
         │              │                   │              │
         └──────────────► • Customer Data   │◄─────────────┘
                        │ • Payment History │
                        └───────────────────┘
```

## 📋 **Prerequisites**

- **Python 3.8+**
- **Docker** (optional but recommended)
- **SignalWire Account** with:
  - Space URL (e.g., `yourspace.signalwire.com`)
  - Project ID
  - API Token
  - Call Widget Token and Destination
- **Ngrok Account** (for local development tunneling)

## 🚀 **Quick Start**

> **⚠️ Prerequisites**: Make sure you have your SignalWire credentials ready and create a `.env` file from the provided `env.sample` template before starting.

### **Option 1: Docker with Make Commands (Recommended)**

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd pay-demo-cc25
   ```

2. **Configure environment variables:**
   ```bash
   # Copy the sample environment file
   cp env.sample .env
   
   # Edit .env with your SignalWire credentials and configuration
   vim .env  # or nano .env, or use your preferred editor
   ```

3. **Build and run with Make commands:**
   ```bash
   # Quick setup with advanced agent (recommended)
   make advanced
   
   # Or use simple agent for testing
   make simple
   
   # Or traditional setup (defaults to advanced agent)
   make setup
   ```

4. **Access the application:**
   - Web Interface: `http://localhost:8080`
   - Use `make logs` to view application logs
   - The startup script will display your ngrok tunnel URL

### **Option 2: Local Python Environment**

1. **Install dependencies:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   ```bash
   # Copy the sample environment file
   cp env.sample .env
   
   # Edit .env with your SignalWire credentials
   vim .env
   ```

3. **Run the application:**
   ```bash
   chmod +x start_services.sh
   ./start_services.sh
   ```

## ⚙️ **Configuration**

### **Environment Variables (`.env` file)**

**⚠️ Important**: You must create a `.env` file based on the provided `env.sample` template.

1. **Copy the sample file:**
   ```bash
   cp env.sample .env
   ```

2. **Edit `.env` with your actual credentials:**
   ```bash
   # SignalWire Configuration (Required)
   SIGNALWIRE_SPACE=your-space-name
   SW_PROJECT_ID=your-project-id-here
   SW_REST_API_TOKEN=your-rest-api-token-here

   # SignalWire Call Widget (Required)
   DISPLAY_NAME=<swml-resource-display-name>
   SIGNALWIRE_CALL_TOKEN=your-call-widget-token-here
   SIGNALWIRE_CALL_DESTINATION=<call-widget-destination-address>

   # AI Agent Configuration (Optional)
   POST_PROMPT_URL=<your-post-prompt-url>

   # Ngrok Configuration (Required)
   NGROK_TOKEN=your-ngrok-token-here
   ```

### **Agent Demo Selection**

The application now supports two different AI agent implementations, selected at build time:

- **Advanced Agent** (`atom_agent-advanced.py`): Full-featured payment agent with PIN validation, DataMap tools, and comprehensive payment processing
- **Simple Agent** (`atom_agent-simple.py`): Basic agent with simplified payment flow for testing

**To choose your agent implementation:**

```bash
# Build and run with advanced agent (recommended)
make advanced

# Build and run with simple agent (for testing)
make simple

# Development mode with advanced agent
make dev-advanced

# Development mode with simple agent  
make dev-simple
```

The chosen agent file is copied as `atom_agent.py` during the Docker build process, eliminating any runtime configuration needed.

### **SignalWire Setup**

1. **Create a SignalWire Space** at [signalwire.com](https://signalwire.com)

2. **Get your credentials** from the API section:
   - Space URL
   - Project ID  
   - API Token

3. **Create a Call Widget token:**
   - Go to Call Fabric → Addresses
   - Create an address for your agent endpoint
   - Generate a guest token for the Call Widget

4. **Configure the destination:**
   - Set `SIGNALWIRE_CALL_DESTINATION` to your agent endpoint
   - Format: `https://your-ngrok-url.ngrok-free.app/agent`

### **Ngrok Setup**

1. **Sign up** at [ngrok.com](https://ngrok.com)
2. **Get your auth token** from the dashboard
3. **Add to environment:** `NGROK_TOKEN=your-token`

The application automatically:
- Starts ngrok tunnel on port 8080
- Updates SignalWire webhooks with the new URL
- Configures the AI agent endpoint

## 📁 **Project Structure**

```
pay-demo-cc25/
├── app.py                      # Main Flask application
├── atom_agent-advanced.py      # Full-featured AI agent with PIN validation
├── atom_agent-simple.py        # Simplified AI agent for testing
├── resource.py                 # SWML webhook management utilities
├── customer.db                 # SQLite database (auto-created)
├── requirements.txt            # Python dependencies
├── env.sample                  # Environment template (copy to .env)
├── .env                        # Your environment configuration (create from env.sample)
├── start_services.sh           # Application startup script
├── Dockerfile                  # Docker container configuration (with build args)
├── Makefile                    # Docker management commands with agent selection
├── templates/                  # HTML templates
│   ├── base.html              # Base template with SignalWire styling
│   ├── dashboard.html         # Customer dashboard with call widget
│   ├── index.html             # Landing page
│   └── ...
└── static/                     # Static assets
    ├── css/
    │   └── style.css          # SignalWire-themed styles
    ├── js/
    │   └── main.js            # Frontend JavaScript
    └── images/
    
Note: During Docker build, either atom_agent-advanced.py or atom_agent-simple.py 
is copied as atom_agent.py based on the selected build target.
```

## 🔧 **Key Components**

### **1. Flask Backend (`app.py`)**
- **Customer Dashboard**: Displays account balance and payment options
- **Call Widget Integration**: Serves SignalWire call tokens and destinations
- **Agent Endpoint**: Handles incoming calls and routes to AI agent
- **Database Management**: Customer data and payment history

### **2. AI Agent (`atom_agent.py`)**
- **Payment Processing**: SWAIG functions for handling payments
- **Customer Lookup**: Retrieves customer balances and information
- **Natural Language**: Processes voice commands and responses
- **DTMF Support**: Handles keypad input for sensitive data
- **Build-time Selection**: Copied from either `atom_agent-advanced.py` or `atom_agent-simple.py` during Docker build

### **3. Call Widget (`templates/dashboard.html`)**
- **c2c-widget Implementation**: Brian Kwest's proven approach
- **DTMF Functionality**: Keypad support for payment input
- **Event Handling**: Call state management and modal interactions
- **Error Prevention**: Robust error handling and state management

### **4. SWML Webhooks (`resource.py`)**
- **Dynamic Configuration**: Updates webhook URLs automatically
- **Ngrok Integration**: Handles tunnel URL changes
- **Resource Management**: Creates and updates SignalWire resources

## 🎮 **Usage**

### **Customer Experience**

1. **Visit Dashboard**: Navigate to `http://localhost:8080/dashboard`
2. **View Balance**: See outstanding balance for Max Electric account
3. **Initiate Payment**: Click "Call Support for Payment"
4. **Voice Interaction**: Speak with AI agent about payment options
5. **Provide Payment Info**: Use voice or keypad (DTMF) for sensitive data
6. **Confirm Payment**: Agent processes and confirms transaction

### **DTMF Keypad Support**

During an active call, customers can use their phone keypad:
- **Numbers 0-9**: Input payment amounts, account numbers
- **# and ***: Navigation and confirmation
- **Automatic Detection**: System recognizes DTMF input automatically

### **Testing the Demo**

1. **Start the application**
2. **Make a test call** from the dashboard
3. **Interact with the AI agent**:
   - Ask about account balance
   - Request to make a payment  
   - Provide test payment information
4. **Use DTMF keypad** to input sensitive data
5. **Confirm payment** and observe the result

## 🐳 **Docker Management with Make Commands**

The included `Makefile` provides convenient Docker commands for easy application management:

### **Essential Commands**

```bash
# Quick start with agent selection
make advanced      # Build and run with advanced agent (recommended)
make simple        # Build and run with simple agent (for testing)
make setup         # Traditional setup (defaults to advanced agent)

# Individual commands
make build         # Build the Docker image (defaults to advanced agent)
make build-advanced # Build with advanced agent
make build-simple  # Build with simple agent
make run           # Build and run the container
make run-only      # Run container (assumes image exists)
make stop          # Stop and remove the container
make restart       # Stop and restart the container
```

### **Development Commands**

```bash
# Development with hot-reload and agent selection
make dev-advanced  # Development mode with advanced agent
make dev-simple    # Development mode with simple agent
make dev           # Traditional dev mode (defaults to advanced agent)

# View application output
make logs          # Follow container logs
make status        # Show container status

# Access container
make shell         # Open bash shell inside container
```

### **Maintenance Commands**

```bash
# Cleanup
make clean         # Stop container and remove image
make clean-all     # Deep clean Docker resources
make rebuild       # Clean and rebuild from scratch

# Build options
make build-no-cache # Build without Docker cache

# Utilities
make check-env     # Verify .env file exists and show variables
make open          # Open application in default browser
make help          # Show all available commands
```

### **Typical Workflow**

```bash
# Initial setup
cp env.sample .env
# Edit .env with your credentials
make advanced      # Start with advanced agent (recommended)

# Or for testing/development
make simple        # Start with simple agent

# During development
make dev-advanced  # Development with advanced agent
# or
make dev-simple    # Development with simple agent
make logs          # Monitor logs in another terminal

# When done
make stop          # Stop the application
```

## 🔒 **Security Considerations**

- **Environment Variables**: All sensitive credentials stored in `env` file
- **HTTPS/WSS**: SignalWire requires secure connections for production
- **Token Management**: Call Widget tokens have limited scope and expiration
- **DTMF Privacy**: Keypad input is transmitted securely via SignalWire
- **Input Validation**: All customer inputs are validated and sanitized

## 🛠️ **Development**

### **Local Development**

1. **Hot Reloading**: Use `make dev` for automatic code reloading
2. **Debugging**: Set `DEBUG=True` in environment for verbose logging
3. **Database Reset**: Delete `customer.db` to reset customer data
4. **Log Monitoring**: Use `make logs` to watch application output

### **Adding New Features**

1. **New SWAIG Functions**: Add to `atom_agent.py`
2. **Frontend Changes**: Modify templates in `templates/`
3. **Database Updates**: Extend models in `app.py`
4. **Styling**: Update `static/css/style.css`

### **Troubleshooting**

**Common Issues:**

- **Missing .env file**: Make sure you've copied `env.sample` to `.env` and configured it
- **Wrong Agent Version**: Use `make advanced` for full features or `make simple` for basic testing
- **Call Widget Not Working**: Check `SIGNALWIRE_CALL_TOKEN` and destination URL
- **Agent Not Responding**: Verify ngrok tunnel and webhook configuration  
- **DTMF Not Working**: Ensure call is active and event listeners are attached
- **Database Errors**: Check SQLite file permissions and path

**Debug Steps:**

1. Check environment file exists: `make check-env`
2. Check application logs: `make logs`
3. Verify environment variables are loaded: `make status`
4. Test ngrok tunnel: Visit displayed URL
5. Check SignalWire webhook status in dashboard
6. Monitor browser console for JavaScript errors
7. Try rebuilding with specific agent: `make clean && make advanced` or `make clean && make simple`

## 📚 **API Reference**

### **Agent Endpoints**

- `POST /agent` - Main AI agent webhook endpoint
- `GET /dashboard` - Customer dashboard page
- `POST /swaig` - SWAIG function handler

### **SWAIG Functions**

- `get_customer_balance(phone_number)` - Retrieve customer balance
- `get_payment(amount, payment_method)` - Process payment transaction

## 🤝 **Contributing**

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature-name`
3. **Make changes** and test thoroughly
4. **Submit a pull request** with description

## 📄 **License**

This project is provided as a demonstration and learning tool. Please review SignalWire's terms of service for production usage.

## 🆘 **Support**

- **SignalWire Documentation**: [developer.signalwire.com](https://developer.signalwire.com)
- **Community Discord**: [signalwire.community](https://signalwire.community)
- **GitHub Issues**: For bug reports and feature requests

---

**Built with ❤️ using SignalWire's powerful communication platform** 