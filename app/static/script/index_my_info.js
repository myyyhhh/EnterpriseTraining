// 存储原始用户数据，用于取消编辑时恢复
let originalUserData = null;

// DOM加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    // 初始化原始数据
    initOriginalData();
    
    // 绑定按钮事件
    document.getElementById('edit-btn').addEventListener('click', enterEditMode);
    document.getElementById('save-btn').addEventListener('click', saveChanges);
    document.getElementById('cancel-btn').addEventListener('click', cancelEdit);
});

// 初始化原始用户数据
function initOriginalData() {
    originalUserData = {
        user_account_info: {
            username: document.getElementById('username').value
        },
        user_based_info: {
            real_name: document.getElementById('real_name').value,
            gender: document.getElementById('gender').value,
            birthday: document.getElementById('birthday').value,
            height: document.getElementById('height').value || null,
            weight: document.getElementById('weight').value || null
        },
        user_habit_info: {
            daily_water: document.getElementById('daily_water').value || null,
            sleep_duration: document.getElementById('sleep_duration').value || null,
            exercise_amount: document.getElementById('exercise_amount').value || null,
            vegetable_fruit_intake: document.getElementById('vegetable_fruit_intake').value || null,
            protein_intake: document.getElementById('protein_intake').value || null,
            meat_vegetable_ratio: document.getElementById('meat_vegetable_ratio').value,
            dietary_restrictions: document.getElementById('dietary_restrictions').value,
            cooking_method: document.getElementById('cooking_method').value
        },
        user_psychology: {
            physical_reaction_index: document.getElementById('physical_reaction_index').value || null,
            sleep_cognition_bias: document.getElementById('sleep_cognition_bias').value || null,
            exercise_stress_value: document.getElementById('exercise_stress_value').value || null,
            // diet_emotion_dependence: document.getElementById('diet_emotion_dependence').value || null,
            emotion_stress_index: document.getElementById('emotion_stress_index').value || null
        }
    };

}

// 进入编辑模式
function enterEditMode() {
    // 启用所有输入框
    document.querySelectorAll('.form-control').forEach(input => {
        input.disabled = false;
        input.style.color = 'black';  // 设置文字颜色为黑色
    });
    
    // 切换按钮显示状态
    document.getElementById('edit-btn').style.display = 'none';
    document.getElementById('save-btn').style.display = 'inline-block';
    document.getElementById('cancel-btn').style.display = 'inline-block';
    
    // 清空消息提示
    showMessage('', '');
}

// 取消编辑
function cancelEdit() {
    // 恢复原始数据
    // document.getElementById('username').value = originalUserData.user_account_info.username;
    // document.getElementById('password').value = ''; // 密码不保留原始值，避免安全问题
    
    // document.getElementById('real_name').value = originalUserData.user_based_info.real_name;
    // document.getElementById('gender').value = originalUserData.user_based_info.gender;
    // document.getElementById('birthday').value = originalUserData.user_based_info.birthday;
    // document.getElementById('height').value = originalUserData.user_based_info.height || '';
    // document.getElementById('weight').value = originalUserData.user_based_info.weight || '';
    
    // document.getElementById('daily_water').value = originalUserData.user_habit_info.daily_water || '';
    // document.getElementById('sleep_duration').value = originalUserData.user_habit_info.sleep_duration || '';
    // document.getElementById('exercise_amount').value = originalUserData.user_habit_info.exercise_amount || '';
    // document.getElementById('vegetable_fruit_intake').value = originalUserData.user_habit_info.vegetable_fruit_intake || '';
    // document.getElementById('protein_intake').value = originalUserData.user_habit_info.protein_intake || '';
    // document.getElementById('meat_vegetable_ratio').value = originalUserData.user_habit_info.meat_vegetable_ratio;
    // document.getElementById('dietary_restrictions').value = originalUserData.user_habit_info.dietary_restrictions;
    // document.getElementById('cooking_method').value = originalUserData.user_habit_info.cooking_method;
    
    // document.getElementById('physical_reaction_index').value = originalUserData.user_psychology.physical_reaction_index || '';
    // document.getElementById('sleep_cognition_bias').value = originalUserData.user_psychology.sleep_cognition_bias || '';
    // document.getElementById('exercise_stress_value').value = originalUserData.user_psychology.exercise_stress_value || '';
    // document.getElementById('diet_emotion_dependence').value = originalUserData.user_psychology.diet_emotion_dependence || '';
    // document.getElementById('emotion_stress_index').value = originalUserData.user_psychology.emotion_stress_index || '';
    
    // 禁用所有输入框
    document.querySelectorAll('.form-control').forEach(input => {
        input.disabled = true;
    });
    
    // 切换按钮显示状态
    document.getElementById('edit-btn').style.display = 'inline-block';
    document.getElementById('save-btn').style.display = 'none';
    document.getElementById('cancel-btn').style.display = 'none';
    
    // 清空消息提示
    showMessage('', '');
}

// 保存修改
async function saveChanges() {
    try {
        // 收集表单数据
        const userData = {
            user_account_info: {
                username: document.getElementById('username').value.trim(),
                password: document.getElementById('password').value.trim() || null
            },
            user_based_info: {
                real_name: document.getElementById('real_name').value.trim() || null,
                gender: (
                    document.getElementById('gender').value === '男' ? 1 : 
                    document.getElementById('gender').value === '女' ? 2 :
                    0 
                ),
                birthday: document.getElementById('birthday').value || null,
                height: document.getElementById('height').value ? parseFloat(document.getElementById('height').value) : null,
                weight: document.getElementById('weight').value ? parseFloat(document.getElementById('weight').value) : null
            },
            user_habit_info: {
                daily_water: document.getElementById('daily_water').value ? parseInt(document.getElementById('daily_water').value) : null,
                sleep_duration: document.getElementById('sleep_duration').value ? parseFloat(document.getElementById('sleep_duration').value) : null,
                exercise_amount: document.getElementById('exercise_amount').value.trim()|| null,

                vegetable_fruit_intake: document.getElementById('vegetable_fruit_intake').value.trim()|| null,
                protein_intake: document.getElementById('protein_intake').value.trim()|| null,
                
                meat_vegetable_ratio: document.getElementById('meat_vegetable_ratio').value.trim() || null,
                dietary_restrictions: document.getElementById('dietary_restrictions').value.trim() || null,
                cooking_method: document.getElementById('cooking_method').value.trim() || null
            },
            user_psychology: {
                physical_reaction_index: document.getElementById('physical_reaction_index').value.trim() || null,
                sleep_cognition_bias: document.getElementById('sleep_cognition_bias').value.trim() || null,
                exercise_stress_value: document.getElementById('exercise_stress_value').value.trim() || null,

                emotion_stress_index: document.getElementById('emotion_stress_index').value.trim() || null
            }
        };

        console.log('修改后的用户数据:', userData);
        // 发送更新请求
        const response = await fetch('/update-user-info', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(userData)
        });

        const result = await response.json();

        console.log('更新结果:', result);

        if (response.ok) {
            // 显示成功消息
            showMessage('信息更新成功！', 'success');
            
            // 退出编辑模式
            cancelEdit();
            
            // 更新原始数据缓存
            initOriginalData();
                updateUserResponse(result)
            // 清空密码输入框（安全考虑）
            document.getElementById('password').value = '';
        } else {
            // 显示错误消息
            showMessage(result.detail || '更新失败，请重试', 'error');
        }
    } catch (error) {
        console.error('更新失败:', error);
        showMessage('网络错误，更新失败', 'error');
    }
}

// 显示消息提示
function showMessage(text, type) {
    const alertEl = document.getElementById('message-alert');
    if (!text) {
        alertEl.style.display = 'none';
        return;
    }
    
    // 设置消息内容和样式
    alertEl.textContent = text;
    alertEl.className = 'alert';
    alertEl.classList.add(type === 'success' ? 'alert-success' : 'alert-danger');
    alertEl.style.display = 'block';
    
    // 3秒后自动隐藏
    setTimeout(() => {
        alertEl.style.display = 'none';
    }, 3000);
}

function updateUserResponse(result) {
    const userInfo = result.user_info;
    const userAccountInfo = userInfo.user_account_info;
    const userBasedInfo = userInfo.user_based_info;
    const userHabitInfo = userInfo.user_habit_info;
    const userPsychologyInfo = userInfo.user_psychology;

    // 修改账户信息
    document.getElementById('username').value = userAccountInfo.username;

    // 修改基本信息
    document.getElementById('real_name').value = userBasedInfo.real_name;
    if (userBasedInfo.gender === 1) {
        document.getElementById('gender').value = '男';
    } else if (userBasedInfo.gender === 2) {
        document.getElementById('gender').value = '女';
    } else {
        document.getElementById('gender').value = '其他';
    }


    document.getElementById('birthday').value = userBasedInfo.birthday;
    document.getElementById('height').value = userBasedInfo.height;
    document.getElementById('weight').value = userBasedInfo.weight;

    // 修改习惯信息
    document.getElementById('cooking_method').value = userHabitInfo.cooking_method; 
    document.getElementById('daily_water').value = userHabitInfo.daily_water;
     document.getElementById('dietary_restrictions').value = userHabitInfo.dietary_restrictions;
    document.getElementById('exercise_amount').value = userHabitInfo.exercise_amount;
        document.getElementById('meat_vegetable_ratio').value = userHabitInfo.meat_vegetable_ratio;
    document.getElementById('sleep_duration').value = userHabitInfo.sleep_duration;

    document.getElementById('vegetable_fruit_intake').value = userHabitInfo.vegetable_fruit_intake;
    document.getElementById('protein_intake').value = userHabitInfo.protein_intake;

    // 修改心理信息
    document.getElementById('physical_reaction_index').value = userPsychologyInfo.physical_reaction_index;
    document.getElementById('sleep_cognition_bias').value = userPsychologyInfo.sleep_cognition_bias;
    document.getElementById('exercise_stress_value').value = userPsychologyInfo.exercise_stress_value;
    document.getElementById('emotion_stress_index').value = userPsychologyInfo.emotion_stress_index;
   

}