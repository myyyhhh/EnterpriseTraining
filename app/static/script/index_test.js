
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
        // 获取结果容器并清空
        const resultBody = document.getElementById('test-result-body');
        resultBody.innerHTML = '';

        // 创建维度结果区域
        const dimensionContainer = document.createElement('div');
        dimensionContainer.className = 'result-dimensions-container';

        // 遍历每个维度结果并创建卡片
        results.forEach(result => {
            const dimensionCard = document.createElement('div');
            dimensionCard.className = 'dimension-result-card';

            // 根据分数确定卡片颜色
            let scoreClass = '';
            if (result.score >= 26) {
                scoreClass = 'score-high';
            } else if (result.score >= 16) {
                scoreClass = 'score-medium';
            } else {
                scoreClass = 'score-low';
            }

            // 构建卡片内容
            dimensionCard.innerHTML = `
            <div class="card-header ${scoreClass}">
                <h3 class="dimension-title">${result.dimension}</h3>
                <div class="dimension-score">得分: ${result.score}</div>
            </div>
            <div class="card-content">
                <div class="assessment-section">
                    <h4 class="section-title">评估</h4>
                    <p class="section-content">${result.assessment}</p>
                </div>
                <div class="suggestion-section">
                    <h4 class="section-title">建议</h4>
                    <p class="section-content">${result.suggestion}</p>
                </div>
            </div>
        `;

            dimensionContainer.appendChild(dimensionCard);
        });

        // 创建综合评估区域
        const overallAssessment = document.createElement('div');
        overallAssessment.className = 'overall-assessment-container';
        overallAssessment.innerHTML = `
        <h3 class="overall-title">综合评估</h3>
        <div class="overall-content">基于您的测试结果，我们发现您在多个维度上表现出了不同的心理特征。这些结果可以帮助您更好地了解自己，并采取适当的措施来提升心理健康水平。</div>
    `;

    //     // 创建专业建议区域
    //     const professionalSuggestion = document.createElement('div');
    //     professionalSuggestion.className = 'suggestion-container';
    //     professionalSuggestion.innerHTML = `
    //     <h3 class="suggestion-title">
    //         <i class="fas fa-lightbulb"></i> 专业建议
    //     </h3>
    //     <div class="suggestion-content">根据您的测试结果，我们建议您保持积极的生活态度，定期进行自我反思，并考虑与专业心理咨询师进行进一步的交流，以获得更个性化的指导和支持。</div>
    // `;

        // 添加所有区域到结果容器
        resultBody.appendChild(dimensionContainer);
        resultBody.appendChild(overallAssessment);
        // resultBody.appendChild(professionalSuggestion);

        // 创建并添加重新测试按钮
        const restartBtnContainer = document.createElement('div');
        restartBtnContainer.className = 'restart-button-container';

        const restartBtn = document.createElement('button');
        restartBtn.className = 'restart-button';
        restartBtn.innerHTML = '<i class="fas fa-redo"></i> 重新测试';

        restartBtn.addEventListener('click', function () {
            // 重置测试状态
            document.getElementById('test-result').style.display = 'none';
            document.getElementById('testContainer').style.display = 'block';
            document.getElementById('psychology-test-form').reset();

            // 清除所有选项的选中状态
            document.querySelectorAll('.option-item.selected').forEach(option => {
                option.classList.remove('selected');
            });

            // 重置进度条
            document.getElementById('progress-text').textContent = '0%';
            document.getElementById('progress-fill').style.width = '0%';
            progressContainer.style.display = 'block';
            // 滚动到测试开始位置
            document.querySelector('.progress-container').scrollIntoView({ behavior: 'smooth' });
        });

        restartBtnContainer.appendChild(restartBtn);
        resultBody.appendChild(restartBtnContainer);

        // 显示测试结果，隐藏测试内容
        document.getElementById('test-result').style.display = 'block';
        document.getElementById('testContainer').style.display = 'none';
        progressContainer.style.display = 'none';

        // 滚动到结果区域
        document.getElementById('test-result').scrollIntoView({ behavior: 'smooth' });
    }
});