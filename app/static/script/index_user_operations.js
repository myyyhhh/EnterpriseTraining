
// 获取DOM元素
const body = document.body;
const userInfo = document.getElementById('userInfo');
// const userSwitchMenu = document.getElementById('userSwitchMenu');
const logoutBtn = document.getElementById('logoutBtn');
const addUserBtn = document.getElementById('addUserBtn');
const logoutModal = document.getElementById('logoutModal');
const logoutModalBackdrop = document.getElementById('logoutModalBackdrop');
const addUserModal = document.getElementById('addUserModal');
const addUserModalBackdrop = document.getElementById('addUserModalBackdrop');
const closeLogoutModalBtn = document.getElementById('closeLogoutModal');
const closeAddUserModalBtn = document.getElementById('closeAddUserModal');
const cancelLogoutBtn = document.getElementById('cancelLogoutBtn');
const cancelAddUserBtn = document.getElementById('cancelAddUserBtn');
const confirmLogoutBtn = document.getElementById('confirmLogoutBtn');
const addUserForm = document.getElementById('addUserForm');


    userInfo.addEventListener('click', function(e) {
        e.stopPropagation();
        userSwitchMenu.classList.toggle('active');
    });
document.addEventListener('click', function () {
    userSwitchMenu.classList.remove('active');
});

// userSwitchMenu.addEventListener('click', function (e) {
//     e.stopPropagation();
// });

// 打开退出登录确认对话框
logoutBtn.addEventListener('click', function () {
    logoutModal.style.display = 'block';
    logoutModalBackdrop.style.display = 'block';
    body.classList.add('modal-active');
});

// // 打开添加用户对话框
// addUserBtn.addEventListener('click', function () {
//     addUserModal.style.display = 'block';
//     addUserModalBackdrop.style.display = 'block';
//     body.classList.add('modal-active');
// });

// 关闭退出登录对话框
function closeLogoutModal() {
    logoutModal.style.display = 'none';
    logoutModalBackdrop.style.display = 'none';
    body.classList.remove('modal-active');
}

// // 关闭添加用户对话框
// function closeAddUserModal() {
//     addUserModal.style.display = 'none';
//     addUserModalBackdrop.style.display = 'none';
//     body.classList.remove('modal-active');
// }

// 事件监听
closeLogoutModalBtn.addEventListener('click', closeLogoutModal);
cancelLogoutBtn.addEventListener('click', closeLogoutModal);
logoutModalBackdrop.addEventListener('click', closeLogoutModal);

// closeAddUserModalBtn.addEventListener('click', closeAddUserModal);
// cancelAddUserBtn.addEventListener('click', closeAddUserModal);
// addUserModalBackdrop.addEventListener('click', closeAddUserModal);

// 阻止点击模态框内容时关闭
logoutModal.addEventListener('click', function (e) {
    e.stopPropagation();
});

// addUserModal.addEventListener('click', function (e) {
//     e.stopPropagation();
// });

// 退出登录确认
confirmLogoutBtn.addEventListener('click', function () {
    console.log('logout success');
    logout();

    closeLogoutModal();
});

// 添加用户表单提交
addUserForm.addEventListener('submit', function (e) {
    e.preventDefault();
    const username = document.getElementById('newUsername').value;
    const password = document.getElementById('newPassword').value;

    addUser(username, password);
    
    closeAddUserModal();
    this.reset();
});

// 按ESC键关闭所有模态框
document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
        closeLogoutModal();
        closeAddUserModal();
    }
});


function logout() {
    fetch('/logout', {
        method: 'POST',
        credentials: 'include'
    })
    .then(response => {
        // 检查响应状态
        if (response.redirected) {
            // 如果后端返回重定向，跟随重定向到登录页面
            window.location.href = response.url;
        } else {
            // 如果没有重定向，可能需要手动处理
            console.log('Logout response:', response);
            // 这里可以添加备用逻辑，例如显示消息并手动跳转到登录页
            showAlert('退出登录成功', 'success');
            setTimeout(() => {
                window.location.href = '/login';
            }, 1000);
        }
    })
    .catch(error => {
        console.error('退出登录失败:', error);
        showAlert('退出登录失败，请重试', 'error');
    });
}

function addUser(username, password) {
    // 前端验证
    if (!username || !password) {
        showAlert('用户名和密码不能为空', 'error');
        return;
    }
    
    fetch('/add-user', {
        method: 'POST',
        credentials: 'include',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: new URLSearchParams({
            'new_username': username,
            'new_password': password
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            showAlert(`用户 ${username} 添加成功`, 'success');
            // 刷新用户列表
            loadUserList();
        } else {
            showAlert(data.message || '添加用户失败', 'error');
        }
    })
    .catch(error => {
        console.error('添加用户失败:', error);
        showAlert('添加用户失败，请重试', 'error');
    });
}

// 切换用户（调用后端接口）
function switchUser(targetUsername) {
    fetch('/switch-user', {
        method: 'POST',
        credentials: 'include',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: new URLSearchParams({
            'target_user': targetUsername  // 与后端Form参数对应
        })
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(data => {
                throw new Error(data.detail || '切换用户失败');
            });
        }
        return response.json();
    })
    .then(data => {
        if (data.status === 'success') {
            showAlert(`已成功切换到用户：${data.username}`, 'success');
            // 刷新页面加载新用户数据
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        }
    })
    .catch(error => {
        console.error('切换用户失败:', error);
        showAlert(error.message, 'error');
    });
}



// // 获取DOM元素
// const body = document.body;
// const userInfo = document.getElementById('userInfo');
// const userSwitchMenu = document.getElementById('userSwitchMenu');
// const logoutBtn = document.getElementById('logoutBtn');
// const addUserBtn = document.getElementById('addUserBtn');
// const logoutModal = document.getElementById('logoutModal');
// const logoutModalBackdrop = document.getElementById('logoutModalBackdrop');
// const addUserModal = document.getElementById('addUserModal');
// const addUserModalBackdrop = document.getElementById('addUserModalBackdrop');
// const closeLogoutModalBtn = document.getElementById('closeLogoutModal');
// const closeAddUserModalBtn = document.getElementById('closeAddUserModal');
// const cancelLogoutBtn = document.getElementById('cancelLogoutBtn');
// const cancelAddUserBtn = document.getElementById('cancelAddUserBtn');
// const confirmLogoutBtn = document.getElementById('confirmLogoutBtn');
// const addUserForm = document.getElementById('addUserForm');

// // 修复：确保userInfo和userSwitchMenu被正确引用
// if (!userInfo || !userSwitchMenu) {
//     console.error('无法找到userInfo或userSwitchMenu元素');
// } else {
//     // 点击用户信息区域切换菜单
//     userInfo.addEventListener('click', function(e) {
//         e.stopPropagation();
//         userSwitchMenu.classList.toggle('active');
//     });

//     // 点击页面其他区域关闭菜单
//     document.addEventListener('click', function() {
//         userSwitchMenu.classList.remove('active');
//     });

//     // 阻止菜单点击事件冒泡
//     userSwitchMenu.addEventListener('click', function(e) {
//         e.stopPropagation();
//     });
// }

// // 打开退出登录确认对话框
// logoutBtn.addEventListener('click', function() {
//     logoutModal.style.display = 'block';
//     logoutModalBackdrop.style.display = 'block';
//     body.classList.add('modal-active');
// });

// // 打开添加用户对话框
// addUserBtn.addEventListener('click', function() {
//     addUserModal.style.display = 'block';
//     addUserModalBackdrop.style.display = 'block';
//     body.classList.add('modal-active');
// });

// // 关闭退出登录对话框
// function closeLogoutModal() {
//     logoutModal.style.display = 'none';
//     logoutModalBackdrop.style.display = 'none';
//     body.classList.remove('modal-active');
// }

// // 关闭添加用户对话框
// function closeAddUserModal() {
//     addUserModal.style.display = 'none';
//     addUserModalBackdrop.style.display = 'none';
//     body.classList.remove('modal-active');
// }

// // 事件监听
// closeLogoutModalBtn.addEventListener('click', closeLogoutModal);
// cancelLogoutBtn.addEventListener('click', closeLogoutModal);
// logoutModalBackdrop.addEventListener('click', closeLogoutModal);

// closeAddUserModalBtn.addEventListener('click', closeAddUserModal);
// cancelAddUserBtn.addEventListener('click', closeAddUserModal);
// addUserModalBackdrop.addEventListener('click', closeAddUserModal);

// // 阻止点击模态框内容时关闭
// logoutModal.addEventListener('click', function(e) {
//     e.stopPropagation();
// });

// addUserModal.addEventListener('click', function(e) {
//     e.stopPropagation();
// });

// // 退出登录确认
// confirmLogoutBtn.addEventListener('click', function() {
//     logout();
//     closeLogoutModal();
// });

// // 添加用户表单提交
// addUserForm.addEventListener('submit', function(e) {
//     e.preventDefault();
//     const username = document.getElementById('newUsername').value;
//     const password = document.getElementById('newPassword').value;

//     addUser(username, password);
//     closeAddUserModal();
//     this.reset();
// });

// // 按ESC键关闭所有模态框
// document.addEventListener('keydown', function(e) {
//     if (e.key === 'Escape') {
//         closeLogoutModal();
//         closeAddUserModal();
//     }
// });

// // 加载用户列表
// function loadUserList() {
//     fetch('/api/users', {
//         method: 'GET',
//         credentials: 'include'
//     })
//     .then(response => response.json())
//     .then(users => {
//         const userListContainer = document.getElementById('userListContainer');
//         userListContainer.innerHTML = '';
        
//         users.forEach(user => {
//             const userItem = document.createElement('div');
//             userItem.className = 'menu-item';
//             userItem.innerHTML = `<i class="fas fa-user mr-2"></i> ${user.user_account_info.username}`;
//             userItem.addEventListener('click', function() {
//                 switchUser(user.user_account_info.username);
//             });
//             userListContainer.appendChild(userItem);
//         });
//     })
//     .catch(error => {
//         console.error('加载用户列表失败:', error);
//         showAlert('获取用户列表失败，请刷新页面', 'error');
//     });
// }

// // 退出登录功能
// function logout() {
//     fetch('/logout', {
//         method: 'POST',
//         credentials: 'include'
//     })
//     .then(response => {
//         if (response.redirected) {
//             window.location.href = response.url;
//         } else {
//             console.log('Logout response:', response);
//             showAlert('退出登录成功', 'success');
//             setTimeout(() => {
//                 window.location.href = '/login';
//             }, 1000);
//         }
//     })
//     .catch(error => {
//         console.error('退出登录失败:', error);
//         showAlert('退出登录失败，请重试', 'error');
//     });
// }

// // 添加用户功能
// function addUser(username, password) {
//     if (!username || !password) {
//         showAlert('用户名和密码不能为空', 'error');
//         return;
//     }
    
//     fetch('/add-user', {
//         method: 'POST',
//         credentials: 'include',
//         headers: {
//             'Content-Type': 'application/x-www-form-urlencoded'
//         },
//         body: new URLSearchParams({
//             'new_username': username,
//             'new_password': password
//         })
//     })
//     .then(response => response.json())
//     .then(data => {
//         if (data.status === 'success') {
//             showAlert(`用户 ${username} 添加成功`, 'success');
//             loadUserList();
//         } else {
//             showAlert(data.message || '添加用户失败', 'error');
//         }
//     })
//     .catch(error => {
//         console.error('添加用户失败:', error);
//         showAlert('添加用户失败，请重试', 'error');
//     });
// }

// // 切换用户（调用后端接口）
// function switchUser(targetUsername) {
//     fetch('/switch-user', {
//         method: 'POST',
//         credentials: 'include',
//         headers: {
//             'Content-Type': 'application/x-www-form-urlencoded'
//         },
//         body: new URLSearchParams({
//             'target_user': targetUsername
//         })
//     })
//     .then(response => {
//         if (!response.ok) {
//             return response.json().then(data => {
//                 throw new Error(data.detail || '切换用户失败');
//             });
//         }
//         return response.json();
//     })
//     .then(data => {
//         if (data.status === 'success') {
//             showAlert(`已成功切换到用户：${data.username}`, 'success');
//             setTimeout(() => {
//                 window.location.reload();
//             }, 1000);
//         }
//     })
//     .catch(error => {
//         console.error('切换用户失败:', error);
//         showAlert(error.message, 'error');
//     });
// }

// // 通用提示函数
// function showAlert(message, type = 'info') {
//     // 创建提示元素（如果不存在）
//     let alertElement = document.getElementById('global-alert');
//     if (!alertElement) {
//         alertElement = document.createElement('div');
//         alertElement.id = 'global-alert';
//         alertElement.className = 'alert';
//         document.body.appendChild(alertElement);
//     }

//     // 设置样式和内容
//     alertElement.textContent = message;
//     alertElement.className = 'alert';
//     alertElement.classList.add(type === 'error' ? 'alert-error' : 'alert-success');
//     alertElement.style.display = 'block';

//     // 3秒后自动隐藏
//     setTimeout(() => {
//         alertElement.style.display = 'none';
//     }, 3000);
// }