<template>
  <div>
    <transition name="fade">
      <div v-if="isOpen" class="chatbot-container">
        <div class="chatbot-header">
          🎓 Chatbot Tuyển Sinh
          <button class="chatbot-close" @click="isOpen = false" title="Thu nhỏ">×</button>
        </div>
        <div class="chatbot-messages" ref="messages">
          <div v-for="(msg, idx) in messages" :key="idx" :class="['chatbot-msg', msg.role]">
            <span v-if="msg.role === 'user'">🧑‍💻</span>
            <span v-else>🤖</span>
            <span class="chatbot-text">{{ msg.text }}</span>
          </div>
        </div>
        <form class="chatbot-input-row" @submit.prevent="send">
          <input v-model="input" type="text" placeholder="Nhập câu hỏi..." class="chatbot-input" autocomplete="off" />
          <button type="submit" :disabled="loading || !input.trim()" class="chatbot-send">Gửi</button>
        </form>
      </div>
    </transition>
    <transition name="pop">
      <button v-if="!isOpen" class="chatbot-fab" @click="isOpen = true" title="Mở Chatbot">
        <svg width="28" height="28" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="12" fill="#1976d2"/><path d="M7 17v-2a4 4 0 0 1 4-4h2a4 4 0 0 1 4 4v2" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><circle cx="9" cy="10" r="1" fill="#fff"/><circle cx="15" cy="10" r="1" fill="#fff"/></svg>
      </button>
    </transition>
  </div>
</template>

<script>
export default {
  name: 'Chatbot',
  data() {
    return {
      input: '',
      messages: [
        { role: 'bot', text: 'Xin chào! Bạn muốn hỏi gì về tuyển sinh?' }
      ],
      loading: false,
      isOpen: false
    }
  },
  methods: {
    async send() {
      const question = this.input.trim()
      if (!question) return
      this.messages.push({ role: 'user', text: question })
      this.input = ''
      this.loading = true
      this.scrollToBottom()
      try {
        const res = await fetch('http://localhost:5005/api/chatbot/ask', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ question })
        })
        const data = await res.json()
        this.messages.push({ role: 'bot', text: data.answer })
      } catch (e) {
        this.messages.push({ role: 'bot', text: 'Lỗi kết nối server!' })
      }
      this.loading = false
      this.scrollToBottom()
    },
    scrollToBottom() {
      this.$nextTick(() => {
        const el = this.$refs.messages
        if (el) el.scrollTop = el.scrollHeight
      })
    },
    receiveAnswer(answer) {
      this.messages.push({ role: 'bot', text: answer })
      this.loading = false
      this.scrollToBottom()
    }
  }
}
</script>

<style scoped>
.chatbot-container {
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  max-width: 400px;
  min-width: 280px;
  background: #fff;
  box-shadow: 0 2px 12px rgba(0,0,0,0.07);
  display: flex;
  flex-direction: column;
  height: 500px;
  position: relative;
  z-index: 10000;
}
.chatbot-header {
  background: #1976d2;
  color: #fff;
  padding: 1rem;
  font-weight: bold;
  border-top-left-radius: 12px;
  border-top-right-radius: 12px;
  text-align: center;
  position: relative;
}
.chatbot-close {
  position: absolute;
  right: 12px;
  top: 10px;
  background: transparent;
  border: none;
  color: #fff;
  font-size: 1.5rem;
  cursor: pointer;
  line-height: 1;
}
.chatbot-messages {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  background: #f9f9f9;
}
.chatbot-msg {
  margin-bottom: 0.75rem;
  display: flex;
  align-items: flex-start;
}
.chatbot-msg.user {
  justify-content: flex-end;
}
.chatbot-msg.bot {
  justify-content: flex-start;
}
.chatbot-text {
  background: #e3f2fd;
  border-radius: 8px;
  padding: 0.5rem 0.75rem;
  margin-left: 0.5rem;
  max-width: 70%;
  word-break: break-word;
  font-size: 1rem;
}
.chatbot-msg.user .chatbot-text {
  background: #c8e6c9;
  margin-left: 0;
  margin-right: 0.5rem;
}
.chatbot-input-row {
  display: flex;
  border-top: 1px solid #e0e0e0;
  padding: 0.5rem;
  background: #fff;
}
.chatbot-input {
  flex: 1;
  border: none;
  outline: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-size: 1rem;
  background: #f5f5f5;
  margin-right: 0.5rem;
}
.chatbot-send {
  background: #1976d2;
  color: #fff;
  border: none;
  border-radius: 6px;
  padding: 0.5rem 1.2rem;
  font-size: 1rem;
  cursor: pointer;
  transition: background 0.2s;
}
.chatbot-send:disabled {
  background: #bdbdbd;
  cursor: not-allowed;
}
.chatbot-fab {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: #1976d2;
  color: #fff;
  border: none;
  box-shadow: 0 2px 8px rgba(0,0,0,0.18);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  cursor: pointer;
  position: fixed;
  bottom: 32px;
  right: 32px;
  z-index: 9999;
  transition: box-shadow 0.2s;
}
.chatbot-fab:hover {
  box-shadow: 0 4px 16px rgba(25,118,210,0.25);
}
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.2s;
}
.fade-enter, .fade-leave-to {
  opacity: 0;
}
.pop-enter-active, .pop-leave-active {
  transition: transform 0.2s, opacity 0.2s;
}
.pop-enter, .pop-leave-to {
  transform: scale(0.7);
  opacity: 0;
}
</style> 