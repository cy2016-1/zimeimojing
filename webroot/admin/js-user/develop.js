$.extend({
    // 加载开发者基本信息
    ajax_develop: function (fn) {
        var urlapi = '../../py/develop_user.py?op=getaccount&r=' + Math.random()
        $.ajax({
            type: "GET",
            url: urlapi,
            dataType: 'json',
            success: function (msg) {
                if (msg.code == '0000') {
                    var data = $.parseJSON(msg.data);
                    if (typeof (fn) == 'function') fn(data);
                } else {
                    if (typeof (fn) == 'function') fn({});
                }
            }
        });
    },

    // 加载开发者详细信息
    ajax_developInfo: function (userid, fn) {
        var urlapi = '../../py/develop_user.py?op=getaccountinfo&userid='+userid+'&r=' + Math.random();
        $.ajax({
            type: "GET",
            url: urlapi,
            dataType: 'json',
            success: function (msg) {
                if (msg.code == '0000') {
                    if (typeof (fn) == 'function') fn(msg.data);
                } else {
                    if (typeof (fn) == 'function') fn({});
                }
            }
        });
    },

    // 加载开发者已发布的插件列表
    ajax_developPlugin: function (userid, fn) {
        var urlapi = '../../py/develop_user.py?op=getaccplugin&userid='+userid+'&r=' + Math.random();
        $.ajax({
            type: "GET",
            url: urlapi,
            dataType: 'json',
            success: function (msg) {
                if (msg.code == '0000') {
                    if (typeof (fn) == 'function') fn(msg.data);
                } else {
                    if (typeof (fn) == 'function') fn({});
                }
            }
        });
    },

    // 退出登录
    logout_develop: function (fn) {
        var urlapi = '../../py/develop_user.py?op=exitaccount&r=' + Math.random()
        $.ajax({
            type: "GET",
            url: urlapi,
            dataType: 'json',
            success: function (msg) {
                if (msg.code == '0000') {
                    if (typeof (fn) == 'function') fn(msg);
                } else {
                    if (typeof (fn) == 'function') fn({});
                }
            }
        });
    },

    // 登录开发者
    login_develop: function (fn) {
        var host = window.location.host + '@admin@pages@login@authredirect.html';
        host = host.replace(/@@/g, '@');

        var winobj = $.openWindow('http://hapi.16302.com/user/wxlogin/host/' + host, 500, 500, { title: '微信登录' });
        window.localStorage.setItem('x-admin-oauth-code', '');
        var logtimer = setInterval(function () {
            var oauthcode = localStorage.getItem('x-admin-oauth-code');

            if (oauthcode == null) { clearInterval(logtimer); return false }
            if (oauthcode) {
                var theRequest = {};
                var strs = oauthcode.split('&');
                for (let i = 0; i < strs.length; i++) {
                    var item = strs[i].split('=');
                    theRequest[item[0]] = decodeURI(item[1]);
                }
                if (typeof (fn) == 'function') fn(theRequest);
                clearInterval(logtimer);
                return false
            }
            if (winobj.closed) { clearInterval(logtimer); return false }
        }, 500);
    }
});