document.addEventListener("DOMContentLoaded", () => {
  const chatBtn = document.getElementById("chat-btn");
  const chatBox = document.getElementById("chat-box");
  const closeBtn = document.getElementById("close-chat");
  const chatMessages = document.getElementById("chat-messages");
  const msgInput = document.getElementById("msg-input");
  const sendBtn = document.getElementById("send-btn");

  if (!chatBtn || !chatBox || !closeBtn || !chatMessages || !msgInput || !sendBtn) {
    console.error("❌ Không tìm thấy các phần tử chatbot.");
    return;
  }

  // Mở/đóng chat box
  chatBtn.addEventListener("click", () => {
    chatBox.style.display = "flex";
    msgInput.focus();
  });

  closeBtn.addEventListener("click", () => {
    chatBox.style.display = "none";
  });

  // Lịch sử chat
  let history = [];

  // Hàm hiển thị tin nhắn
  function addMessage(role, text) {
    const div = document.createElement("div");
    div.className = "msg " + role;
    div.textContent = text;
    chatMessages.appendChild(div);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    return div; // trả về div để update nếu cần
  }

  // Gửi tin nhắn
  async function sendMessage() {
    const text = msgInput.value.trim();
    if (!text) return;

    // Hiển thị tin nhắn user
    addMessage("user", text);
    msgInput.value = "";
    msgInput.disabled = true;
    sendBtn.disabled = true;

    // Thêm "typing..." tạm thời
    const typingDiv = addMessage("bot", "🤖 ...");

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text, history })
      });

      if (!res.ok) throw new Error("Server error " + res.status);

      const data = await res.json();
      const reply = data.reply || "🤖 Không có phản hồi từ server.";

      // Thay "typing..." bằng phản hồi thật
      typingDiv.textContent = reply;

      // Cập nhật lịch sử chat
      history.push({ role: "user", content: text });
      history.push({ role: "assistant", content: reply });

    } catch (err) {
      console.error("❌ Lỗi API:", err);
      typingDiv.textContent = "⚠️ Lỗi server. Vui lòng thử lại.";
    } finally {
      msgInput.disabled = false;
      sendBtn.disabled = false;
      msgInput.focus();
    }
  }

  // Sự kiện gửi tin nhắn
  sendBtn.addEventListener("click", sendMessage);
  msgInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") sendMessage();
  });
});
