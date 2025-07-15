
document.addEventListener('DOMContentLoaded', function () {

    const startBtn = document.getElementById('start-test-btn');
    const testIntro = document.getElementById('testIntro');
    const testContainer = document.getElementById('testContainer');
    const psychologyTestForm = document.getElementById('psychology-test-form');
    const progressContainer = document.getElementById('progress-container');

    // 开始测试按钮功能
    startBtn.addEventListener('click', function () {
        // 隐藏欢迎界面，显示测试内容
        testIntro.style.display = 'none';
        testContainer.style.display = 'block';
        progressContainer.style.display = 'block';

        // 滚动到测试开始位置
        testContainer.scrollIntoView({ behavior: 'smooth' });
    });

    // 选项选择功能
    const optionItems = document.querySelectorAll('.option-item');

    optionItems.forEach(item => {
        item.addEventListener('click', function () {
            // 清除同题目下的其他选中状态
            const questionCard = this.closest('.question-card');
            questionCard.querySelectorAll('.option-item').forEach(opt => {
                opt.classList.remove('selected');
            });

            // 设置当前选项为选中
            this.classList.add('selected');

            // 更新进度
            updateProgress();
        });
    });

    // 更新进度条
    function updateProgress() {
        const totalQuestions = document.querySelectorAll('.question-card').length;
        const answeredQuestions = document.querySelectorAll('.option-item.selected').length;
        const progress = Math.round((answeredQuestions / totalQuestions) * 100);

        document.getElementById('progress-text').textContent = `${progress}%`;
        document.getElementById('progress-fill').style.width = `${progress}%`;
    }

    // // 表单提交处理
    const testForm = document.getElementById('psychology-test-form');

    testForm.addEventListener('submit', function (e) {
        e.preventDefault();

        const answers = {};
        let allAnswered = true;

        document.querySelectorAll('.question-card').forEach(question => {
            const selectedOption = question.querySelector('.option-item.selected');
            if (selectedOption) {
                // 1. 获取题目ID（如1,2,3...）
                const questionId = question.dataset.questionId;
                // 2. 获取所属维度（如"情绪压力指标"）
                const dimension = question.closest('.dimension-card').dataset.dimension;
                // 3. 获取分数
                const score = parseInt(selectedOption.dataset.score);

                // 4. 生成唯一键：维度+题目ID（避免重复）
                const uniqueKey = `${dimension}-${questionId}`;

                // 按后端要求的格式存储
                answers[uniqueKey] = {
                    dimension: dimension,
                    score: score
                };
            } else {
                allAnswered = false;
                // 高亮未回答的问题（需配合CSS）
                question.classList.add('unanswered');
                setTimeout(() => question.classList.remove('unanswered'), 3000);
            }
        });

        // console.log('修正后的答案:', answers);

        if (!allAnswered) {
            // 滚动到第一个未回答的问题
            const firstUnanswered = document.querySelector('.question-card.unanswered');
            if (firstUnanswered) {
                firstUnanswered.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
            return;
        }

        // 发送数据到后端
        submitTestAnswers(answers);
    });

    // 提交答案到后端
    async function submitTestAnswers(answers) {
        try {
            const response = await fetch('/submit-test', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    answers: answers
                })
            });

            const result = await response.json();

            console.log(result)

            if (result.status === "success") {
                // 显示测试结果
                displayTestResults(result.results);
            } else {
                alert('提交失败: ' + result.message);
            }
        } catch (error) {
            console.error('提交测试时出错:', error);
            alert('提交测试时发生错误，请重试');
        }
    }

    // 显示测试结果
    function displayTestResults(results) {
        const dimensionResults = document.getElementById('dimension-results');
        dimensionResults.innerHTML = ''; // 清空现有内容

        results.forEach(result => {
            const dimensionCard = document.createElement('div');
            dimensionCard.className = 'dimension-card';

            // 设置卡片样式和颜色
            let scoreClass = '';
            if (result.score >= 26) {
                scoreClass = 'bg-success text-white';
            } else if (result.score >= 16) {
                scoreClass = 'bg-warning text-dark';
            } else {
                scoreClass = 'bg-danger text-white';
            }

            dimensionCard.innerHTML = `
            <div class="content-card">
                <div class="card-header ${scoreClass}">
                    <h5 class="card-title">
                        ${result.dimension}
                    </h5>
                    <div class="score-badge">得分: ${result.score}</div>
                </div>
                <div class="user-card">
                    <p><strong>评估:</strong> ${result.assessment}</p>
                    <p><strong>建议:</strong> ${result.suggestion}</p>
                </div>
            </div>
        `;

            dimensionResults.appendChild(dimensionCard);
            dimensionCard.style.display = 'flex';
            dimensionCard.style.flexDirection = 'column';
        });
        // 显示测试结果
        document.getElementById('test-result').style.display = 'block';
        // 滚动到结果区域
        document.getElementById('test-result').scrollIntoView({ behavior: 'smooth' });
        // 隐藏测试内容
        progressContainer.style.display = 'none';
        testContainer.style.display = 'none';
        // 加入重新测试按钮
        // const restartBtn = document.createElement('button');
        // restartBtn.className = 'btn btn-primary';
        // restartBtn.textContent = '重新测试';
        // testContainer.appendChild(restartBtn);
        // 创建并添加重新测试按钮
        const restartBtnContainer = document.createElement('div');
        restartBtnContainer.className = 'restart-btn-container mt-4 text-center';

        const restartBtn = document.createElement('button');
        restartBtn.className = 'btn btn-primary';
        restartBtn.innerHTML = '<i class="fas fa-redo"></i> 重新测试';

        // 重新测试按钮点击事件
        restartBtn.addEventListener('click', function () {
            // 重置测试状态
            document.getElementById('test-result').style.display = 'none'; // 隐藏结果
            document.getElementById('testContainer').style.display = 'block'; // 显示测试内容
            document.getElementById('psychology-test-form').reset(); // 重置表单

            // 清除所有选项的选中状态
            document.querySelectorAll('.option-item.selected').forEach(option => {
                option.classList.remove('selected');
            });

            // 重置进度条
            document.getElementById('progress-text').textContent = '0%';
            document.getElementById('progress-fill').style.width = '0%';

            // 滚动到测试开始位置
            document.querySelector('.progress-container').scrollIntoView({ behavior: 'smooth' });
        });

        restartBtnContainer.appendChild(restartBtn);
        document.querySelector('.result-dimensions').after(restartBtnContainer); // 将按钮添加到建议区域下方
    }
});