
// // 管家意见相关功能
// document.addEventListener('DOMContentLoaded', function () {
//     // 获取DOM元素
//     const generateBtn = document.getElementById('generate-advice-btn');
//     const adviceContent = document.getElementById('adviceContent');
//     const loadingIndicator = document.getElementById('loadingIndicator');
//     const adviceMessage = document.getElementById('adviceMessage');

//     // 按钮点击事件
//     generateBtn.addEventListener('click', async function () {
//         try {
//             // 显示加载状态
//             loadingIndicator.style.display = 'block';
//             generateBtn.disabled = true;
//             adviceMessage.style.display = 'none';

//             // 向FastAPI后端发送请求
//             console.log('Sending request to generate advice...');

//             const response = await fetch('/generate-advice', {
//                 method: 'POST',
//                 headers: {
//                     'Content-Type': 'application/json',
//                     // 如果需要身份验证，可以添加token
//                     // 'Authorization': `Bearer ${getToken()}`
//                 },
//                 // 可以发送当前用户信息等数据
//                 body: JSON.stringify({
//                     user_name: document.getElementById('userName').textContent.trim(),
//                     request_time: new Date().toISOString()
//                 })
//             });

//             const result = await response.json();

//             // 隐藏加载状态
//             loadingIndicator.style.display = 'none';
//             generateBtn.disabled = false;

//             console.log('Received advice:', result);

//             if (response.ok) {
//                 // 显示成功消息和生成的意见
//                 adviceContent.innerHTML = `<div class="advice-card">
//                     <h3>最新管家意见</h3>
//                     <p>${result.advice}</p>
//                     <div class="advice-meta">
//                         <small>生成时间: ${new Date(result.timestamp).toLocaleString()}</small>
//                     </div>
//                 </div>`;

//                 showMessage('管家意见生成成功', 'success');
//             } else {
//                 // 显示错误消息
//                 showMessage(`生成失败: ${result.error || '未知错误'}`, 'error');
//             }
//         } catch (error) {
//             // 处理网络错误
//             loadingIndicator.style.display = 'none';
//             generateBtn.disabled = false;
//             showMessage(`网络错误: ${error.message}`, 'error');
//         }
//     });

//     // 显示消息提示
//     function showMessage(text, type) {
//         adviceMessage.textContent = text;
//         adviceMessage.style.display = 'block';
//         adviceMessage.className = 'advice-message';

//         if (type === 'success') {
//             adviceMessage.classList.add('alert-success');
//         } else if (type === 'error') {
//             adviceMessage.classList.add('alert-danger');
//         }

//         // 3秒后自动隐藏消息
//         setTimeout(() => {
//             adviceMessage.style.display = 'none';
//         }, 3000);
//     }
// });





document.addEventListener('DOMContentLoaded', function () {
    // 获取DOM元素
    const generateBtn = document.getElementById('generate-advice-btn');
    const adviceContent = document.getElementById('adviceContent');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const adviceMessage = document.getElementById('adviceMessage');

    // 按钮点击事件
    generateBtn.addEventListener('click', async function () {
        try {
            // 显示加载状态
            loadingIndicator.style.display = 'block';
            generateBtn.disabled = true;
            adviceMessage.style.display = 'none';

            // 向FastAPI后端发送请求
            console.log('Sending request to generate advice...');

            const response = await fetch('/generate-advice', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_name: document.getElementById('userName').textContent.trim(),
                    request_time: new Date().toISOString()
                })
            });

            const result = await response.json();

            // 隐藏加载状态
            loadingIndicator.style.display = 'none';
            generateBtn.disabled = false;

            console.log('Received advice:', result);

            if (response.ok && result.status === 'success') {
                // 处理建议列表（支持不定长度）
                renderAdviceList(result.advices);
                showMessage('管家意见生成成功', 'success');
            } else {
                // 显示错误消息（兼容后端可能返回的不同错误格式）
                const errorMsg = result.error || '生成失败，请稍后重试';
                showMessage(`生成失败: ${errorMsg}`, 'error');
                // 清空内容区域
                adviceContent.innerHTML = '<p class="empty-state">暂无管家意见，请点击生成按钮重试</p>';
            }
        } catch (error) {
            // 处理网络错误
            loadingIndicator.style.display = 'none';
            generateBtn.disabled = false;
            showMessage(`网络错误: ${error.message}`, 'error');
            adviceContent.innerHTML = '<p class="empty-state">网络连接失败，请检查网络后重试</p>';
        }
    });

    // 渲染建议列表（核心优化部分）
    function renderAdviceList(advices) {
        // 处理空列表情况
        if (!advices || advices.length === 0) {
            adviceContent.innerHTML = `
                <div class="advice-card">
                    <h3>管家意见</h3>
                    <p class="empty-advice">暂无针对您的建议数据，请完善个人信息后重试</p>
                </div>
            `;
            return;
        }

        // 构建建议列表HTML
        let adviceHtml = `
            <div class="advice-card">
                <h3>最新管家意见</h3>
                <div class="advice-list">
        `;

        // 遍历建议数组（支持任意长度）
        advices.forEach((advice, index) => {
            // 移除建议文本中的换行符并格式化
            const formattedAdvice = advice.replace(/\n/g, '<br>');
            
            // 为每条建议添加序号和样式
            adviceHtml += `
                <div class="advice-item">
                    <div class="advice-text">${formattedAdvice}</div>
                </div>
            `;
        });

        // 添加生成时间
        const generateTime = new Date().toLocaleString();
        adviceHtml += `
                </div>
                <div class="advice-meta">
                    <small>生成时间: ${generateTime}</small>
                </div>
                <div>
                </div>
            </div>
        `;

        // 渲染到页面
        adviceContent.innerHTML = adviceHtml;
    }

    // 显示消息提示
    function showMessage(text, type) {
        adviceMessage.textContent = text;
        adviceMessage.style.display = 'block';
        adviceMessage.className = 'advice-message';

        if (type === 'success') {
            adviceMessage.classList.add('alert-success');
        } else if (type === 'error') {
            adviceMessage.classList.add('alert-danger');
        }

        // 3秒后自动隐藏消息
        setTimeout(() => {
            adviceMessage.style.display = 'none';
        }, 3000);
    }
});