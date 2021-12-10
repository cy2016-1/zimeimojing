(function($){

    /**
     * 取URL地址参数
     * 用法：
     * var name = $.getUrlParam('name');
     */
    $.getUrlParam = function(name) {
        var reg = new RegExp("(^|&)" + name + "=([^&]*)(&|$)");
        var r = window.location.search.substr(1).match(reg);
        if (r != null) return unescape(r[2]); return null;
    }

    /**
     * 弹出窗口函数
     * @param {网址} url
     * @param {宽度} w
     * @param {高度} h
     * @param {其他设置参数} setup = {}
     */
    $.openWindow = function( url, w, h, setup) {
        var iWidth = w || 500;
        var iHeight = h || 300;
        var setup = setup || {};
        var menubar = setup.menubar || 'no';
        var title = setup.title || '弹出窗口';
        var iTop = (window.screen.availHeight - 30 - iHeight) / 2;
        var iLeft = (window.screen.availWidth - 10 - iWidth) / 2;
        return window.open(url, title, "width="+w+",height="+h+",top="+iTop+",left="+iLeft+",toolbar=no,menubar="+menubar+",scrollbars=no,resizable=no,location=no,status=no,alwaysRaised=yes,depended=yes");
    }
})(jQuery);