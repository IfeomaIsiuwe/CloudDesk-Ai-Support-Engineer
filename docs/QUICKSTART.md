# 🚀 CloudDesk Quick Start Guide

## Installation (2 minutes)

### Mac/Linux:
```bash
cd CloudDesk
chmod +x setup.sh
./setup.sh
```

### Windows:
```bash
cd CloudDesk
setup.bat
```

## Configuration (2 minutes)

1. Copy environment template:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your API keys:
   ```
   HF_TOKEN=your_huggingface_token
   PINECONE_API_KEY=your_pinecone_key
   ```

## Running Applications

### Main AI Assistant (Port 8501)
```bash
streamlit run streamlit_app.py
```
➜ Visit: http://localhost:8501

### Admin Dashboard (Port 8502)
```bash
streamlit run dashboards/admin_dashboard.py
```
➜ Visit: http://localhost:8502

### Analytics Dashboard (Port 8503)
```bash
streamlit run dashboards/analytics_dashboard.py
```
➜ Visit: http://localhost:8503

### REST API Server (Port 5000)
```bash
python -m flask --app api.routes run
```
➜ API Docs: http://localhost:5000/api/health

## 📊 What Each Component Does

| Component | Purpose | Port |
|-----------|---------|------|
| **Main App** | User-facing AI support assistant | 8501 |
| **Admin Dashboard** | Manage system, escalations, users | 8502 |
| **Analytics Dashboard** | View metrics, trends, insights | 8503 |
| **REST API** | Programmatic access to features | 5000 |

## 🎯 Main Features

### 1. AI Support Assistant (streamlit_app.py)
- 💬 Ask CloudDesk questions
- 🔍 Get RAG-powered responses
- ⭐ Rate responses with feedback
- 📊 View response confidence
- 🚨 Auto-escalation to Tier 2
- 💾 Query caching
- 📚 Learn from previous support

### 2. Admin Dashboard
**Overview Page:**
- System health metrics
- Query stats (resolved, escalated)
- Response times
- User activity

**Escalation Management:**
- View open escalation tickets
- Assign to Tier 2 agents
- Track resolution times

**Knowledge Base:**
- Learned responses (from Tier 2)
- Reuse statistics
- Learning effectiveness

**User Management:**
- Manage user accounts
- Assign roles
- View user history

**Audit & Compliance:**
- All system actions logged
- Compliance reports
- Data export

### 3. Analytics Dashboard
**Query Performance:**
- Success rates
- Confidence trends
- Response time analysis

**Search Analytics:**
- Top searched queries
- Knowledge gaps
- Trending categories

**Feedback Analysis:**
- Rating distribution
- Helpful vs unhelpful
- Categories needing improvement

**Knowledge Insights:**
- Learned responses usage
- Coverage by category
- Learning opportunities

## 📈 Key Metrics You'll See

```
Total Queries:           Number of all user queries
Success Rate:            % of queries resolved without escalation
Escalation Rate:         % requiring Tier 2 support
Avg Confidence:          How certain the AI is (0-100%)
Response Time:           How fast responses are generated
User Rating:             Average star rating (1-5)
```

## 🔗 API Examples

### Get Summary Metrics
```bash
curl -H "X-API-Key: YOUR_KEY" \
  http://localhost:5000/api/metrics/summary?days=30
```

### Submit Feedback
```bash
curl -X POST -H "X-API-Key: YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query_id":"123","response_id":"456","rating":5,"helpful":true}' \
  http://localhost:5000/api/feedback
```

### Get Escalation Queue
```bash
curl -H "X-API-Key: YOUR_KEY" \
  http://localhost:5000/api/escalations?limit=20
```

## 🐛 Troubleshooting

### Database Error
```python
from database import DatabaseManager
db = DatabaseManager()  # Reinitialize
```

### API Key Not Working
- Generate new key in User Management
- Make sure X-API-Key header is set
- Check key is active (not deactivated)

### Cache Issues
```python
from features.cache_manager import CacheManager
cache_manager = CacheManager(db)
cache_manager.clear_expired_cache()
```

### No Escalations Appearing
- Check escalation confidence threshold (default: 60%)
- Verify Tier 2 users are created
- Check audit logs for escalation records

## 📚 Documentation

- **Full System Docs:** `SYSTEM_DOCUMENTATION.md`
- **API Documentation:** Check `/api/health` endpoint
- **Database Schema:** See `database/models.py`

## 🔐 Security Tips

1. **API Keys:** Store securely, never commit to git
2. **Passwords:** Use strong passwords for admin accounts
3. **Audit Logs:** Regularly review in admin dashboard
4. **Backup:** Backup `clouddesk.db` regularly
5. **Environment:** Use `.env` file, don't hardcode secrets

## ⚡ Performance Tips

1. **Enable Caching:** Set `CACHE_ENABLED=True` in .env
2. **Adjust TTL:** Increase `CACHE_TTL_SECONDS` for more caching
3. **Database Cleanup:** Periodically clear old audit logs
4. **Monitor API:** Use admin dashboard to track performance

## 🎓 Learning Path

**New Users:**
1. Start with main AI assistant
2. Submit feedback on responses
3. View analytics dashboard
4. Explore admin dashboard

**Integration:**
1. Generate API key in user settings
2. Use REST API for programmatic access
3. Integrate with your systems
4. Monitor via dashboards

**Advanced:**
1. Customize escalation rules
2. Manage knowledge base
3. Configure notifications
4. Export compliance reports

## 🆘 Getting Help

1. Check **SYSTEM_DOCUMENTATION.md** for detailed docs
2. Review **API endpoints** at http://localhost:5000/api/health
3. Check **Admin Dashboard** for system status
4. Review **Audit Logs** for error details

## ✅ Success Checklist

- [ ] Installation completed without errors
- [ ] `.env` file configured with API keys
- [ ] Main app runs at http://localhost:8501
- [ ] Can ask a question and get response
- [ ] Can submit feedback
- [ ] Admin dashboard loads
- [ ] Analytics dashboard shows data
- [ ] REST API responds to requests

## 🚀 You're Ready!

Your CloudDesk AI Support System is now running! 

**Next Steps:**
1. Try asking a support question
2. Explore the dashboards
3. Configure your Tier 2 support team
4. Integrate with your systems via API
5. Monitor performance metrics

---

**Need help?** Check SYSTEM_DOCUMENTATION.md for comprehensive guides.

**Questions?** Review the feature module documentation in the `features/` directory.

**Ready to deploy?** See SYSTEM_DOCUMENTATION.md for production deployment instructions.
