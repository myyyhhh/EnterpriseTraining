//---------------对话功能-------------------

const chatHistory = document.getElementById('chatHistory');
const inputBox = document.querySelector('.the-communication-input input');
const sendBtn = document.querySelector('.the-communication-input button');

// 滚动到聊天区域底部
function scrollToBottom() {
    chatHistory.scrollTop = chatHistory.scrollHeight;
}

// 获取DOM元素
// 添加加载中的指示器
function addLoadingIndicator() {
    const div = document.createElement('div');
    div.className = 'message message-other loading-indicator';
    div.id = 'ai-loading'; // 添加ID以便后续移除
    div.innerHTML = `
        <div class="message-header">
            <div class="message-sender">健康管家</div>
            <div class="message-time">正在输入...</div>
        </div>
        <div class="message-content">
            <div class="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
    `;
    chatHistory.appendChild(div);
    scrollToBottom();
}

// 移除加载指示器
function removeLoadingIndicator() {
    const loadingIndicator = document.getElementById('ai-loading');
    if (loadingIndicator) {
        loadingIndicator.remove();
    }
}

// // 发送消息函数
// async function sendMessage() {
//     const message = inputBox.value.trim();
//     if (!message) return; // 空消息不发送

//     // 1. 清空输入框
//     inputBox.value = '';

//     try {
//         // 2. 发送POST请求到后端
//         const response = await fetch('/send-message', {
//             method: 'POST',
//             headers: {
//                 'Content-Type': 'application/x-www-form-urlencoded',
//             },
//             body: new URLSearchParams({ message: message })
//         });

//         const data = await response.json();
//         if (data.status === 'success') {
//             // 3. 动态添加用户消息到界面
//             addMessageToDOM(data.user_message);
//             // 4. 动态添加AI回复到界面
//             addMessageToDOM(data.ai_message);
//         }
//     } catch (error) {
//         console.error('发送失败：', error);
//         addMessageToDOM({
//             sender: 'system',
//             message: '消息发送失败，请重试',
//             time: '刚刚'
//         });
//     }
// }
// 发送消息函数 - 修改后
async function sendMessage() {

    console.log('发送消息');

    const message = inputBox.value.trim();
    if (!message) return; // 空消息不发送

    // 1. 清空输入框
    inputBox.value = '';

    try {
        // 2. 立即添加用户消息到界面
        const now = new Date();
        const timeString = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}`;

        const userMsg = {
            sender: 'human',
            message: message,
            time: timeString
        };

        console.log(userMsg);

        addMessageToDOM(userMsg);

        // 3. 添加AI加载指示器
        addLoadingIndicator();

        // 4. 发送POST请求到后端
        const response = await fetch('/send-message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams({ message: message })
        });

        const data = await response.json();
        if (data.status === 'success') {
            // 5. 移除加载指示器
            removeLoadingIndicator();

            // 6. 动态添加AI回复到界面
            addMessageToDOM(data.ai_message);
        }
    } catch (error) {
        console.error('发送失败：', error);

        // 移除加载指示器并显示错误信息
        removeLoadingIndicator();
        addMessageToDOM({
            sender: 'system',
            message: '消息发送失败，请重试',
            time: '刚刚'
        });
    }
}

// 动态添加消息到聊天界面
function addMessageToDOM(msg) {
    const div = document.createElement('div');
    // 根据sender设置样式（匹配前端模板的判断）
    if (msg.sender === 'human') {
        div.className = 'message message-self';
        div.innerHTML = `
            <div class="message-header">
                <div class="message-sender">我</div>
                <div class="message-time">${msg.time}</div>
            </div>
            <div class="message-content">${msg.message}</div>
        `;
    } else if (msg.sender === 'ai') {
        div.className = 'message message-other';
        div.innerHTML = `
            <div class="message-header">
                <div class="message-sender">健康管家</div>
                <div class="message-time">${msg.time}</div>
            </div>
            <div class="message-content">${msg.message}</div>
        `;
    } else { // system
        div.className = 'message message-system';
        div.innerHTML = `<div class="message-content">${msg.message}</div>`;
    }
    chatHistory.appendChild(div);
    // 滚动到底部
    chatHistory.scrollTop = chatHistory.scrollHeight;
}

// // 绑定发送事件（按钮点击/回车）
// sendBtn.addEventListener('click', sendMessage);
// inputBox.addEventListener('keypress', (e) => {
//     if (e.key === 'Enter') sendMessage();
// });

// 清空聊天记录
function clearChat() {
    if (confirm('确定要清空当前聊天记录吗？')) {
        const chatHistory = document.getElementById('chatHistory');
        // 保留系统消息
        const systemMessage = chatHistory.querySelector('.message-system');
        chatHistory.innerHTML = '';
        if (systemMessage) {
            chatHistory.appendChild(systemMessage);
        }

        // 发送清空请求到后端
        fetch('/clear-chat', { method: 'POST' })
            .catch(error => console.error('清空聊天记录错误:', error));
    }
}

// 事件监听
document.addEventListener('DOMContentLoaded', () => {
    // 滚动到底部
    scrollToBottom();

    // 发送按钮点击事件
    document.getElementById('sendButton').addEventListener('click', sendMessage);

    // 输入框回车事件
    document.getElementById('messageInput').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
    inputBox.focus();
});
// 清空聊天按钮
// document.getElementById('clearChatBtn').addEventListener('click', clearChat);

// 输入框自动聚焦
document.getElementById('messageInput').focus();
