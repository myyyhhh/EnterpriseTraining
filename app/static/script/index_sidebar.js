//==========DOM元素=================

const toggleBtn = document.getElementById('toggleBtn'); // 折叠按钮
const sidebar = document.getElementById('sidebar');     //侧边栏  
const userInfo = document.getElementById('userInfo');    //用户信息区域
const userSwitchMenu = document.getElementById('userSwitchMenu');    //用户切换菜单
const switchItems = document.querySelectorAll('.switch-user-item');  //用户切换菜单项
const appContainer = document.getElementById('app-container');
//===========主界面===========================

// ------------折叠功能--------------

toggleBtn.addEventListener('click', function () {
    sidebar.classList.toggle('collapsed');
});

// -------------用户菜单---------------

// 用户切换功能（绑定到用户信息区域）
userInfo.addEventListener('click', function (e) {
    // console.log(e);
    e.stopPropagation();
    userSwitchMenu.classList.toggle('active');
});


//点击页面其他区域关闭菜单
document.addEventListener('click', function () {
    userSwitchMenu.classList.remove('active');
});

//阻止菜单点击事件冒泡
userSwitchMenu.addEventListener('click', function (e) {
    e.stopPropagation();
});


// 菜单项点击事件
switchItems.forEach(item => {
    item.addEventListener('click', function () {
        const userName = this.textContent.trim();
        if (userName === "添加用户" || userName === "账户设置" || userName === "退出登录") {
            alert(`正在执行: ${userName}`);
        } else {
            document.querySelector('.user-name').textContent = userName;
            if (userName === "李华") {
                document.querySelector('.user-role').textContent = "系统管理员";
            } else if (userName === "王芳") {
                document.querySelector('.user-role').textContent = "普通会员";
            } else {
                document.querySelector('.user-role').textContent = "高级会员";
            }
            alert(`已切换到用户: ${userName}`);
        }
        userSwitchMenu.classList.remove('active');
    });
});

//--------------导航功能--------------

// 导航项点击事件
// 获取DOM元素
const navItems = document.querySelectorAll('.nav-item');
const contentPages = document.querySelectorAll('.content-page');

// 导航切换功能
function switchView(viewName) {
    // 更新导航项状态
    navItems.forEach(item => {
        if (item.getAttribute('data-view') === viewName) {
            item.classList.add('active');
        } else {
            item.classList.remove('active');
        }
    });

    // 更新内容页面
    contentPages.forEach(page => {
        if (page.getAttribute('data-view') === viewName) {
            page.classList.add('active');
        } else {
            page.classList.remove('active');
        }
    });
}

// 为每个导航项添加点击事件
navItems.forEach(item => {
    item.addEventListener('click', function () {
        const viewName = this.getAttribute('data-view');
        switchView(viewName);
    });
});

