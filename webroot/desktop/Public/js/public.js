/**
 * 全局JS，网络状态，显示提示文字
 **/
const require = parent.window.require;
const { ipcRenderer } = require('electron');

var html = '<div class="top_status" id="statusbar"><span class="iconfont" id="network"></span></div><div id="tishiText"></div>';
$(function() {
    if (!$('#statusbar').length) { $('.main-body').append(html); }

    var network = $('#network'); // 网络状态

    //==================麦的状态动画=========================
    var mic_state = {
        Init: function() {
            var michtml = `<canvas id="canvas" style="display:block;position: absolute;"></canvas><svg t="1561126448931" style="position: absolute;top:24px;left:24px;width:32px;height:32px" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="5437" xmlns:xlink="http://www.w3.org/1999/xlink"><defs></defs><path d="M698.624 501.376a170.112 170.112 0 0 1-170.112 170.112h-58.496a170.112 170.112 0 0 1-170.112-170.112V250.048a170.048 170.048 0 0 1 170.112-170.112h58.496a170.112 170.112 0 0 1 170.112 170.112v251.328z" fill="#979FCB" p-id="5438"></path><path d="M725.76 410.624v104.512c0 104.448-87.68 189.12-195.904 189.12H462.464c-108.224 0-195.968-84.672-195.968-189.12V410.624h-31.808v123.904c0 118.912 99.904 215.296 223.04 215.296h76.736c123.264 0 223.104-96.384 223.104-215.296V410.624h-31.808z" fill="#394B97" p-id="5439"></path><path d="M453.184 719.104h92.16v162.944h-92.16z" fill="#394B97" p-id="5440"></path><path d="M734.656 944v-12.224c0-40.896-38.976-74.048-87.232-74.048h-296.32c-48.128 0-87.232 33.216-87.232 74.048v12.224h470.784z" fill="#394B97" p-id="5441"></path><path d="M520.896 225.088h174.464v41.152H520.896zM298.944 225.088h174.464v41.152H298.944zM520.896 297.536h174.464v41.152H520.896zM298.944 297.536h174.464v41.152H298.944zM520.896 375.68h174.464v41.216H520.896zM298.944 375.68h174.464v41.216H298.944zM520.896 448.256h174.464v41.088H520.896zM298.944 448.256h174.464v41.088H298.944z" fill="#5161A4" p-id="5442"></path></svg>`;
            var divobj = document.createElement("div");
            divobj.setAttribute("style", "position: fixed;bottom:85px;left:47%;display: none;");
            divobj.setAttribute("id", "micro");
            divobj.innerHTML = michtml;
            document.body.appendChild(divobj);

            this.canvas = document.getElementById('canvas');
            this.ctx = canvas.getContext('2d');
            this.canvas.width = 80;
            this.canvas.height = 80;
            this.radius = 15;
            this.timer = 0;
            this.is_up_do = '';
            return this;
        },
        drawCircle: function() {
            this.ctx.beginPath();
            this.ctx.arc(40, 40, this.radius, 0, Math.PI * 2); //划弧
            this.ctx.closePath();
            this.ctx.lineWidth = 3;
            this.ctx.strokeStyle = 'rgba(38, 147, 255,1)';
            this.ctx.stroke();

            this.radius += 0.5;
            if (this.radius > 30) {
                this.radius = 0;
            }
        },
        render: function() {
            var prev = this.ctx.globalCompositeOperation;
            this.ctx.globalCompositeOperation = 'destination-in';
            this.ctx.globalAlpha = 0.80;
            this.ctx.fillRect(0, 0, canvas.width, canvas.height);
            this.ctx.globalCompositeOperation = prev;
            this.drawCircle();
        },
        up_staut: function() {
            var timer2 = setInterval(function() {
                mic_state.render()
                if (mic_state.radius == 0) { window.clearInterval(timer2); }
            }, 20);
        },
        do_staut: function() {
            this.radius = 15
            this.render()
        },
        main: function(st) {
            var newst = parseInt(st)
            if (newst == 0) {
                if (this.is_up_do != newst) this.do_staut()
            } else {
                if (this.is_up_do != newst || this.radius == 0) this.up_staut()
            }
            this.is_up_do = newst
        }
    };
    //====================END==========================

    var micstate = mic_state.Init();

    //接收主进程消息
    var timer1 = 0
    ipcRenderer.on('public', function(event, json) {
        //麦的状态
        if (json.type == 'mic') {
            var data = json.data;
            if (data == 'start') { $('#micro').show(); }
            if (data == 'stop') { $('#micro').hide(); }
            if (data == '1' || data == '0') {
                micstate.main(data);
            }
        }

        //设备状态
        if (json.type == 'dev') {
            var data = json.data
            if (data.netstatus == 1) {
                network.html('&#xe6ae;');
            } else {
                network.html('&#xe726;');
            }
        }

        //语音消息提示
        if (json.type == 'text') {
            var json_obj = json.data;

            var msg = json_obj.msg;
            var timer = json_obj.timer * 1000;

            if (json_obj.init == 1) $('#tishiText').empty();

            var ts_arr = $('#tishiText div');

            if (ts_arr.length >2) {
                if (ts_arr.length >= 4) ts_arr.first().remove();
                $('#tishiText div').eq(0).css({ 'opacity': '0.2' });
                $('#tishiText div').eq(1).css({ 'opacity': '0.4' });
            }

            var duihua = '<div class="' + json_obj.obj + '">' + msg + '</div>';

            $('#tishiText').append(duihua);

            window.clearTimeout(timer1);
            timer1 = setTimeout(function() { $('#tishiText').empty(); }, 30000);
        }

        // 向页面添加元素
        if (json.type == 'addElement'){
            if (!json.data) return;
            var data = json.data;
            if ( json.eletype == 'html' ){
                var file_list = data.split(',');
                for (x in file_list) {
                    $.get(file_list[x],function(html){
                        if (html){
                            var divobj = document.createElement("div");
                            divobj.innerHTML = html;
                            document.body.appendChild(divobj);
                        }
                    });
                }
            }
            if ( json.eletype == 'js' ){
                var file_list = data.split(',');
                for (x in file_list) {
                    var fileref = document.createElement("script");
                    fileref.setAttribute("type","text/javascript");
                    fileref.setAttribute("src", file_list[x]);
                    document.getElementsByTagName("head")[0].appendChild(fileref);
                }
            }
            if ( json.eletype == 'css' ){
                var file_list = data.split(',');
                for (x in file_list) {
                    $.get(file_list[x],function(css){
                        if (css){
                            var cssScript = document.createElement('style');
                            cssScript.type = 'text/css';
                            cssScript.innerHTML = css;
                            document.getElementsByTagName("head")[0].appendChild(cssScript);
                        }
                    });
                }
            }
            if ( json.eletype == 'jscode' ){
                var newScript = document.createElement('script');
                newScript.type = 'text/javascript';
                newScript.innerHTML = data;
                document.body.appendChild(newScript);
            }
        }
    });
});