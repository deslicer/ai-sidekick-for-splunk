# Workshop API Key Management Guide

This guide helps workshop presenters manage Google AI Studio API keys for participants efficiently and safely.

## ✅ Bulk API Key Creation Available!

**Great news!** You CAN create Google AI Studio API keys programmatically using the Google Cloud CLI (`gcloud`). This guide provides both automated bulk creation tools and manual management options for workshop presenters.

## 🎯 Complete Workshop Management System

The Python workshop manager provides **8 comprehensive actions** for complete workshop lifecycle management:

### **🔧 Action 1: `check-gcloud` - Environment Validation**
```bash
cd scripts/lab
python workshop-api-key-manager.py --action check-gcloud
```
**What it does:**
- Verifies Google Cloud CLI installation and version
- Checks authentication status and active account
- Validates project configuration
- Tests permissions for API key operations

**Example Output:**
```
✅ Google Cloud CLI is ready!
   📋 Project: my-workshop-project
   👤 Account: presenter@company.com
   💡 Ready to create API keys in project my-workshop-project
```

### **🚀 Action 2: `init` - Workshop Initialization**
```bash
python workshop-api-key-manager.py --action init
```
**What it does:**
- Creates workshop configuration file (`workshop-config.json`)
- Sets up default budget limits ($5 per participant, $250 total cap)
- Configures workshop metadata (name, date, duration)
- Establishes baseline settings for all operations

**Example Output:**
```
🚀 Initializing workshop configuration...
✅ Created config file: workshop-config.json
📊 Workshop: AI Sidekick for Splunk Workshop
👥 Max participants: 50
💰 Budget per participant: $5.0
💳 Total budget cap: $250.0
```

### **📝 Action 3: `template` - Participant Management Setup**
```bash
python workshop-api-key-manager.py --action template --participants 25
```
**What it does:**
- Generates CSV template for participant registration
- Pre-populates with placeholder data for easy editing
- Creates structured format for collecting participant info

**Example Output:**
```
📝 Created participant template: workshop-participants-template-25.csv
📋 Next steps:
   1. Fill in participant names and emails
   2. Have each participant create their Google AI Studio API key
   3. Collect API keys and add them to the CSV file
   4. Run: python workshop-api-key-manager.py --action validate
```

### **🔑 Action 4: `create-keys` - Bulk API Key Creation (Recommended)**
```bash
python workshop-api-key-manager.py --action create-keys --participants 25 --prefix workshop-key
```
**What it does:**
- Bulk creates API keys with automatic naming (`workshop-key-1-timestamp`)
- Automatically restricts keys to Gemini API (`generativelanguage.googleapis.com`)
- Handles errors gracefully with retry logic
- Exports to CSV with proper formatting (`workshop_api_keys.csv`)

**Example Output:**
```
🚀 Creating 25 API keys...
   📋 Project: my-workshop-project
   🏷️  Prefix: workshop-key

📊 Results:
   ✅ Successfully created: 25
   ❌ Failed: 0
   🔒 Restricted to Gemini API: 25
   📄 Keys saved to: workshop_api_keys.csv
```

### **✅ Action 5: `validate` - API Key Validation & Testing**
```bash
python workshop-api-key-manager.py --action validate
```
**What it does:**
- Validates each participant's API key against Google AI Studio
- Tests functionality with actual API calls to Gemini
- Checks API restrictions are properly applied
- Updates participant status (validated, invalid, functional)

**Example Output:**
```
🔍 Loading participants and validating API keys...
👥 Found 25 participants

📊 Validation Results:
✅ Valid API keys: 23
❌ Invalid API keys: 2
🔧 Functional API keys: 23

❌ Invalid API Keys:
   - John Doe (john@email.com): API key validation failed
   - Jane Smith (jane@email.com): Network error during validation
```

### **📊 Action 6: `report` - Comprehensive Analytics**
```bash
python workshop-api-key-manager.py --action report
```
**What it does:**
- Budget analysis - tracks spending per participant and total
- Usage statistics - requests made, activity patterns
- Status breakdown - participant engagement levels
- Budget utilization - percentage of budget used
- AI-generated recommendations for workshop optimization

**Example Output:**
```
📊 Generating workshop report...
📄 Report saved to: workshop-report-20250820-105500.json

📊 Workshop Summary:
   👥 Total participants: 25
   🔑 API key status: {'validated': 23, 'invalid': 2}
   💰 Budget used: $45.50 / $250.0
   📈 Budget utilization: 18.2%

💡 Recommendations:
   ✅ Budget usage is healthy. Participants can continue normal usage.
   🔧 2 participants have invalid API keys that need replacement.
```

### **🔍 Action 7: `monitor` - Real-Time Workshop Monitoring**
```bash
python workshop-api-key-manager.py --action monitor
```
**What it does:**
- Live dashboard updating every 30 seconds
- Real-time budget tracking - see spending as it happens
- Activity monitoring - track participant engagement
- Alert system - warns when approaching limits
- Auto-refresh display for continuous monitoring

**Example Output:**
```
🎯 Workshop Monitor - 2025-08-20 10:55:30
📊 25 participants | $67.25 used | 1,245 requests

⚠️  Alerts:
   ⚠️  Budget usage is at 80%+ of cap. Consider monitoring closely.
   🔧 2 participants have invalid API keys that need replacement.
```

### **🧹 Action 8: `cleanup` - Post-Workshop Security**
```bash
python workshop-api-key-manager.py --action cleanup --prefix workshop-key
```
**What it does:**
- Bulk deletes all workshop API keys matching the pattern
- Safety validation before deletion
- Comprehensive reporting of cleanup results
- Error handling for failed deletions

**Example Output:**
```
🧹 Cleaning up workshop API keys with prefix 'workshop-key'...
✅ Cleanup completed:
   🗑️  Deleted: 25 keys
   📊 Total found: 25 keys
```

## 🎯 **Complete Workshop Workflow**

### **Pre-Workshop (1-2 weeks before)**
```bash
cd scripts/lab

# Option A: Bulk Creation (Recommended)
python workshop-api-key-manager.py --action check-gcloud
python workshop-api-key-manager.py --action create-keys --participants 25
./setup-local-llm-backup.sh

# Option B: Manual Collection
python workshop-api-key-manager.py --action init
python workshop-api-key-manager.py --action template --participants 25
# Send guide to participants, collect keys manually
```

### **Pre-Workshop (2-3 days before)**
```bash
# Validate all keys work
python workshop-api-key-manager.py --action validate

# Generate pre-workshop report
python workshop-api-key-manager.py --action report
```

### **During Workshop**
```bash
# Real-time monitoring dashboard
python workshop-api-key-manager.py --action monitor

# Emergency backup
./switch-to-local-llm.sh
```

### **Post-Workshop**
```bash
# Final report
python workshop-api-key-manager.py --action report

# Security cleanup
python workshop-api-key-manager.py --action cleanup --prefix workshop-key
# OR use interactive script
./cleanup-workshop-keys.sh --pattern workshop-key
```

## 🔧 **Alternative Tools**

### **Bash Script Alternative (Simple Use Cases)**
```bash
# For quick, lightweight key creation only
./bulk-create-api-keys.sh
```
**Use when:** You only need basic key creation without management features

### **Standalone Cleanup Scripts**
```bash
# Interactive cleanup with confirmation prompts
./cleanup-workshop-keys.sh --pattern workshop-key
./cleanup-workshop-keys.ps1 -Pattern workshop-key  # PowerShell version
```
**Use when:** You want interactive confirmation before deleting keys

### **Direct gcloud Commands (Advanced Users)**
```bash
# Manual key creation
gcloud alpha services api-keys create --display-name="my-key" --api-target="service=generativelanguage.googleapis.com"

# Manual cleanup
gcloud alpha services api-keys list --filter='displayName~workshop-key' --format='value(name)' | xargs -I {} gcloud alpha services api-keys delete {} --quiet
```
**Use when:** You need custom gcloud operations or integration with other scripts

## 📋 Participant API Key Creation Guide

**Send this to your workshop participants:**

---

### How to Create Your Google AI Studio API Key

**⏰ Please complete this BEFORE the workshop**

1. **Visit Google AI Studio**
   - Go to [https://aistudio.google.com/](https://aistudio.google.com/)
   - Sign in with your Google account

2. **Create API Key**
   - Click "Get API Key" in the top navigation
   - Click "Create API Key in new project" (recommended)
   - Or select an existing project if you prefer

3. **Copy Your API Key**
   - Copy the generated API key (starts with `AIza...`)
   - **Keep this secure** - don't share it publicly

4. **Test Your Key (Optional)**
   - Visit the [AI Studio playground](https://aistudio.google.com/app/prompts/new_chat)
   - Try asking a simple question to verify it works

5. **Submit to Workshop Organizers**
   - Provide your API key through the secure method shared by organizers
   - Include your name and email as registered

**💡 Pro Tips:**
- Free tier includes generous limits perfect for workshops
- No billing setup required for basic usage
- Keep your API key private and secure

---

## 🔍 Google Cloud Limitations & Considerations

### API Key Creation Capabilities

1. **✅ Programmatic Creation Available**
   - Google Cloud CLI (`gcloud`) supports bulk API key creation
   - Can create up to 300 API keys per project
   - Automatic restriction to specific APIs (e.g., Gemini)
   - Perfect for workshop scenarios

2. **Rate Limits (Per Project)**
   - **Free Tier**: 5 requests/minute, 100 requests/day per project
   - **Paid Tier**: Higher limits, varies by model
   - Limits are **per project**, not per API key

3. **Quota Sharing**
   - All API keys from the same project share quotas
   - For bulk creation: all workshop keys share the same project quotas
   - Consider this when planning workshop exercises

### Workshop Scaling Considerations

#### Small Workshops (≤20 participants)
- ✅ **Recommended approach**
- Each participant creates their own project/API key
- No quota conflicts
- Easy to manage

#### Medium Workshops (21-50 participants)
- ⚠️ **Manageable with planning**
- Monitor usage carefully
- Consider staggered exercises
- Have backup plans for quota limits

#### Large Workshops (50+ participants)
- 🚨 **Requires special planning**
- Consider multiple workshop sessions
- Use local LLM alternatives as backup
- Request quota increases in advance

### Budget Management

#### Free Tier Benefits
- **No billing required** for basic usage
- **Generous limits** for workshop activities
- **Perfect for learning** and experimentation

#### Paid Tier Considerations
- **Only needed for heavy usage**
- **Billing per project** (participant responsibility)
- **Workshop organizer not liable** for participant costs

## 🛠️ Advanced Workshop Management

### Pre-Workshop Checklist

- [ ] Initialize workshop configuration
- [ ] Create participant template
- [ ] Send API key creation guide to participants
- [ ] Collect participant information and API keys
- [ ] Validate all API keys 2-3 days before workshop
- [ ] Prepare backup plans for invalid keys
- [ ] Test workshop exercises with sample API keys

### During Workshop Checklist

- [ ] Start monitoring mode
- [ ] Have backup API keys ready
- [ ] Monitor budget usage
- [ ] Help participants with API key issues
- [ ] Generate mid-workshop reports if needed

### Post-Workshop Checklist

- [ ] Generate final report
- [ ] Archive participant data securely
- [ ] Document lessons learned
- [ ] Clean up temporary files

## 🔧 Troubleshooting Common Issues

### Invalid API Keys
**Problem**: Participant API key doesn't work
**Solutions**:
1. Verify key was copied correctly (no extra spaces)
2. Check if key is from Google AI Studio (not Google Cloud)
3. Have participant regenerate key
4. Use backup key if available

### Rate Limit Exceeded
**Problem**: "Quota exceeded" errors during workshop
**Solutions**:
1. Stagger exercises across participants
2. Use local LLM as backup
3. Switch to different exercises temporarily
4. Have participants create new projects

### Budget Concerns
**Problem**: Worried about unexpected costs
**Solutions**:
1. Free tier is sufficient for most workshops
2. Participants control their own billing
3. Monitor usage with provided tools
4. Set clear expectations about usage

## 📊 Usage Monitoring

### Real-Time Monitoring
```bash
python workshop-api-key-manager.py --action monitor
```

Shows:
- Active participants
- Budget usage
- Request counts
- Alerts and recommendations

### Report Generation
```bash
python workshop-api-key-manager.py --action report
```

Generates:
- Participant summary
- Budget analysis
- Usage statistics
- Recommendations

## 🔐 Security Best Practices

### For Workshop Organizers
- Store participant API keys securely
- Use encrypted communication for key collection
- Delete keys after workshop completion
- Don't commit keys to version control

### For Participants
- Keep API keys private
- Don't share keys with others
- Regenerate keys after workshop if concerned
- Monitor usage in Google AI Studio

## 🚀 Alternative Solutions

### For Large Workshops
1. **Multiple Sessions**: Split into smaller groups
2. **Local LLMs**: Use Ollama as backup/primary
3. **Shared Projects**: Organizer provides pre-created keys (higher management overhead)
4. **Hybrid Approach**: Mix of Google AI Studio and local LLMs

### Backup Plans
1. **Ollama Setup**: Local LLM installation guide
2. **OpenAI Alternative**: If participants have OpenAI keys
3. **Demo Mode**: Presenter-driven demonstrations
4. **Offline Exercises**: Non-LLM workshop activities

## 📞 Support During Workshop

### Quick Fixes
```bash
# Validate single participant
grep "participant@email.com" workshop-participants.csv

# Check workshop status
python workshop-api-key-manager.py --action report

# Monitor in real-time
python workshop-api-key-manager.py --action monitor
```

### Emergency Procedures
1. **Invalid Key**: Help participant recreate
2. **Quota Exceeded**: Switch to backup exercises
3. **Budget Alert**: Review usage and adjust
4. **Technical Issues**: Fall back to demo mode

---

This approach provides comprehensive management while working within Google's limitations. The key is preparation, monitoring, and having backup plans ready.
