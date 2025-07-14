# OmniBot - AI-Powered Omni-Channel Chatbot Platform

🤖 **OmniBot** adalah platform chatbot AI yang menghubungkan WhatsApp, Telegram, LINE, dan Instagram dengan berbagai penyedia AI dalam satu dashboard yang terpadu.

## 🚀 Fitur Utama

### 🌐 Multi-Platform Support
- **WhatsApp** - Integrasi dengan WhatsApp Business API
- **Telegram** - Bot Telegram dengan webhook
- **LINE** - LINE Messaging API
- **Instagram** - Instagram Business Messaging

### 🤖 AI Provider Integration
- **Gemini** (Default)
- **OpenAI GPT** (GPT-4, GPT-3.5, dll)
- **Claude** (Anthropic)
- **DeepSeek**
- **Qwen**
- **Kimi**

### 💰 Pricing Plans
- **Free**: 100 pesan/bulan, 1 bot
- **Basic**: 1,000 pesan/bulan, 5 bot ($19/bulan)
- **Premium**: 5,000 pesan/bulan, unlimited bot ($49/bulan)

### 🔧 Fitur Lainnya
- Auto-reply untuk semua platform
- Multi-account support
- Webhook management
- Chat history & analytics
- Custom AI system messages
- Real-time messaging interface

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: React.js dengan Tailwind CSS
- **Database**: MongoDB
- **Authentication**: JWT
- **AI Integration**: emergentintegrations library
- **Payment**: Xendit (Indonesia)

## 📋 Requirements

- Python 3.8+
- Node.js 14+
- MongoDB
- Yarn package manager

## 🚀 Installation & Setup

### 1. Clone Repository
```bash
git clone <repository-url>
cd omnibot
```

### 2. Backend Setup
```bash
cd backend
pip install -r requirements.txt
```

### 3. Frontend Setup
```bash
cd frontend
yarn install
```

### 4. Environment Variables

#### Backend (.env)
```
MONGO_URL=mongodb://localhost:27017
DB_NAME=omnibot_db
SECRET_KEY=your-secret-key-here
```

#### Frontend (.env)
```
REACT_APP_BACKEND_URL=http://localhost:8001
```

### 5. Running the Application

#### Development Mode
```bash
# Backend
cd backend
uvicorn server:app --reload --host 0.0.0.0 --port 8001

# Frontend
cd frontend
yarn start
```

#### Production Mode (with supervisor)
```bash
sudo supervisorctl restart all
```

## 📱 Platform Setup Guide

### WhatsApp Business API
1. Daftar di [WhatsApp Business Platform](https://business.whatsapp.com/)
2. Buat aplikasi baru
3. Generate access token
4. Setup webhook URL: `https://yourdomain.com/api/webhooks/whatsapp/{bot_id}`

### Telegram Bot
1. Chat dengan [@BotFather](https://t.me/BotFather)
2. Buat bot baru dengan `/newbot`
3. Salin bot token
4. Setup webhook: `https://yourdomain.com/api/webhooks/telegram/{bot_id}`

### LINE Messaging API
1. Buat akun di [LINE Developers](https://developers.line.biz/)
2. Buat provider dan channel baru
3. Dapatkan Channel Access Token
4. Setup webhook: `https://yourdomain.com/api/webhooks/line/{bot_id}`

### Instagram Business Messaging
1. Setup Instagram Business Account
2. Buat Facebook App
3. Konfigurasi Instagram Basic Display
4. Setup webhook: `https://yourdomain.com/api/webhooks/instagram/{bot_id}`

## 🔑 API Key Setup

### AI Provider API Keys

#### Gemini (Default)
- URL: [Google AI Studio](https://aistudio.google.com/app/apikey)
- Default key sudah disediakan

#### OpenAI
- URL: [OpenAI Platform](https://platform.openai.com/api-keys)
- Model: gpt-4, gpt-3.5-turbo, dll

#### Claude (Anthropic)
- URL: [Anthropic Console](https://console.anthropic.com/)
- Model: claude-3-sonnet, claude-3-haiku, dll

#### DeepSeek
- URL: [DeepSeek Platform](https://platform.deepseek.com/)
- Model: deepseek-chat, deepseek-coder

#### Qwen
- URL: [Qwen Platform](https://dashscope.aliyun.com/)
- Model: qwen-turbo, qwen-max

#### Kimi
- URL: [Moonshot AI](https://platform.moonshot.cn/)
- Model: moonshot-v1-8k, moonshot-v1-32k

## 👥 User Roles

### 1. User (Default)
- Membuat dan mengelola bot
- Menggunakan chat interface
- Mengatur AI provider pribadi
- Melihat analytics bot

### 2. Superadmin
- Semua fitur user
- Mengatur Xendit payment settings
- Melihat semua user dan bot
- Manage system settings

## 🔐 Authentication

### Register
```bash
POST /api/auth/register
{
  "email": "user@example.com",
  "password": "password123",
  "full_name": "John Doe"
}
```

### Login
```bash
POST /api/auth/login
{
  "email": "user@example.com",
  "password": "password123"
}
```

### Default Superadmin
Untuk membuat superadmin pertama, update database secara manual:
```javascript
db.users.updateOne(
  {email: "admin@example.com"},
  {$set: {role: "superadmin"}}
)
```

## 📊 API Endpoints

### Authentication
- `POST /api/auth/register` - Register user baru
- `POST /api/auth/login` - Login user
- `GET /api/auth/me` - Get user profile

### Bot Management
- `GET /api/bots` - Get semua bot user
- `POST /api/bots` - Buat bot baru
- `GET /api/bots/{bot_id}` - Get detail bot
- `PUT /api/bots/{bot_id}` - Update bot
- `DELETE /api/bots/{bot_id}` - Delete bot

### Chat Interface
- `POST /api/chat/send` - Send message ke AI
- `GET /api/chat/history/{bot_id}` - Get chat history

### Webhooks
- `POST /api/webhooks/whatsapp/{bot_id}` - WhatsApp webhook
- `POST /api/webhooks/telegram/{bot_id}` - Telegram webhook
- `POST /api/webhooks/line/{bot_id}` - LINE webhook
- `POST /api/webhooks/instagram/{bot_id}` - Instagram webhook

### AI Settings
- `GET /api/ai/models` - Get available AI models
- `POST /api/ai/settings` - Update AI settings

### Admin (Superadmin only)
- `POST /api/admin/xendit/settings` - Update Xendit settings
- `GET /api/admin/xendit/settings` - Get Xendit settings

## 🔧 Configuration

### AI Models Available

#### OpenAI
- gpt-4.1, gpt-4.1-mini, gpt-4o, o1, o1-mini, o3, o3-mini

#### Anthropic
- claude-sonnet-4-20250514, claude-opus-4-20250514, claude-3-5-sonnet-20241022

#### Gemini
- gemini-2.0-flash, gemini-1.5-pro, gemini-1.5-flash

#### DeepSeek
- deepseek-chat, deepseek-coder

#### Qwen
- qwen-turbo, qwen-max

#### Kimi
- moonshot-v1-8k, moonshot-v1-32k, moonshot-v1-128k

## 🚀 Deployment

### 1. Setup MongoDB
```bash
# MongoDB connection string
MONGO_URL=mongodb://localhost:27017
```

### 2. Setup SSL Certificate
Untuk webhook, pastikan domain memiliki SSL certificate yang valid.

### 3. Configure Nginx (Optional)
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location /api/ {
        proxy_pass http://localhost:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 4. Process Management
```bash
# Start all services
sudo supervisorctl start all

# Check status
sudo supervisorctl status

# Restart services
sudo supervisorctl restart all
```

## 🐛 Troubleshooting

### Common Issues

1. **MongoDB Connection Error**
   - Pastikan MongoDB running
   - Check connection string di .env

2. **Webhook Not Receiving**
   - Pastikan domain accessible dari internet
   - Check SSL certificate
   - Verify webhook URL format

3. **AI Provider Error**
   - Verify API key
   - Check model name
   - Ensure sufficient quota

4. **Frontend Not Loading**
   - Check REACT_APP_BACKEND_URL
   - Verify backend server running
   - Check CORS settings

### Logs
```bash
# Backend logs
tail -f /var/log/supervisor/backend.*.log

# Frontend logs
tail -f /var/log/supervisor/frontend.*.log
```

## 🤝 Contributing

1. Fork repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create pull request

## 📄 License

MIT License - see LICENSE file for details

## 📞 Support

Untuk support dan pertanyaan:
- Email: support@omnibot.com
- Documentation: https://docs.omnibot.com
- GitHub Issues: https://github.com/yourusername/omnibot/issues

## 🔄 Updates

### v1.0.0 (Current)
- Multi-platform chatbot support
- AI provider integration
- Webhook management
- User authentication
- Basic analytics

### Coming Soon
- Advanced analytics dashboard
- Message scheduling
- Custom AI training
- Team collaboration features
- Mobile app

---

**Made with ❤️ by OmniBot Team**