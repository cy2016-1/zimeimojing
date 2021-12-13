const { BrowserWindow, net, ipcMain } = require("electron");
const ws = require("nodejs-websocket");

const html_root = "http://127.0.0.1:8088";
var view_index = html_root + "/desktop/black.html";

var control = {
    mainWindow: "", // webview 窗件
    IsDisplayScreen: true,

    //导航
    navigat: function (nav_json) {
        //创建窗口
        var create_win = function () {
            var childWin = new BrowserWindow({
                parent: control.mainWindow,
                modal: true,
                show: false,
                frame: false,
                transparent: true,
            });
            childWin.once("ready-to-show", () => {
                childWin.show();
            });
            return childWin;
        };

        var close_win = function () {
            if (!control.childWin.isDestroyed()) {
                control.childWin.close();
            }
            control.childWin = "";
        };

        try {
            if (typeof nav_json == "object") {
                // event ：'open' 弹出窗口
                var rx = /^https?:\/\//i;
                var url = nav_json.url;
                if (!rx.test(url)) url = html_root +'/'+ url;
                url = url.replace(/\\/g, "/");

                if (nav_json.event == "open") {
                    if (!control.IsDisplayScreen) return;
                    if (typeof this.childWin != "object") {
                        this.childWin = create_win();
                    } else if (this.childWin.isDestroyed()) {
                        this.childWin = create_win();
                    }

                    if (nav_json.size) {
                        var w = nav_json.size.width;
                        var h = nav_json.size.height;
                        this.childWin.setSize(w, h);
                        this.childWin.center();
                    }
                    var currentURL = this.childWin.webContents.getURL();
                    if (currentURL != url) this.childWin.loadURL(url);

                    if (nav_json.timer) {
                        if (typeof nav_json.timer == "number") {
                            setTimeout(function () {
                                close_win();
                            }, nav_json.timer * 1000);
                        }
                    }
                }
                // event : 'self' 当前窗口
                if (nav_json.event == "self") {
                    control.mainWindow.loadURL(url);
                }
                // event : 'index' 定义首页
                if (nav_json.event == "index") {
                    view_index = url;
                    control.mainWindow.loadURL(view_index);
                }
                // event : 'close' 关闭弹出窗口
                if (nav_json.event == "close") {
                    if (typeof this.childWin == "object") {
                        close_win();
                    } else {
                        control.mainWindow.loadURL(view_index);
                    }
                }
                // event : 'hideScreen' 隐藏屏幕
                if (nav_json.event == "hideScreen") {
                    control.mainWindow.hide();
                    control.IsDisplayScreen = false;
                }
            }
        } catch (err) {
            console.log("[JS]:err:" + err);
        }
    },

    //接收前端消息并转发到Python
    relay_to_python: function (client_sock) {
        ipcMain.on("toPython", (event, arg) => {
            if (typeof arg == "string") {
                try {
                    arg = JSON.parse(arg);
                } catch (e) {
                    arg = { MsgType: "Text", Receiver: "ControlCenter", Data: arg };
                }
            }
            arg = JSON.stringify(arg);
            client_sock.sendText(arg);
        });
    },

    // 向前端注入通讯接口
    inset_to_python: function () {
        var inc_js = `if(typeof(ZM)=='undefined')window.ZM={};if(typeof(ZM.send)!='function'){ZM.send=function(data){require('electron').ipcRenderer.send('toPython',data);}}`;
        json_str = {type: 'addElement',eletype: 'jscode',data: inc_js};
        control.mainWindow.webContents.send("public", json_str);
    },

    //内部通信服务端
    start_websocket: function () {
        console.log("[JS]:开始建立屏幕通讯连接...");
        var _this = this;
        var server = ws.createServer((conn) => {
            conn.on("text", (str) => {
                // console.log(str);
                var json_str = JSON.parse(str); //字符串转json
                if (json_str.type == "nav") {
                    //如果是导航消息，直接在这里处理
                    control.navigat(json_str);
                } else if (json_str.type == "exejs") {
                    var exec_js = `try{`+ json_str.data +`}catch(err){console.log("[Python]:" + err);}`;
                    control.mainWindow.webContents.executeJavaScript(exec_js);
                } else {
                    control.mainWindow.webContents.send("public", json_str);
                }
            });
            conn.on("close", (code, reason) => {
                console.log("[JS]:关闭连接");
            });
            conn.on("error", (code, reason) => {
                console.log("[JS]:异常关闭");
            });
        }).listen(8103);
        server.on("connection", (client_sock) => {
            console.log("[JS]:有服务端接入");
            _this.relay_to_python(client_sock);
        });
    },

    // 加载插件内的HTML、CSS、JS类代码
    load_plugin_html: function (objtype) {
        var plugin_hook = html_root + "/api/plugin_hook.py?get=" + objtype;
        const request = net.request(plugin_hook);
        request.on("response", (response) => {
            response.on("data", (chunk) => {
                json_str = {type: 'addElement', eletype: objtype, data: chunk.toString("utf8")};
                control.mainWindow.webContents.send("public", json_str);
            });
            response.on("end", () => { });
        });
        request.end();
    },

    Init: function (mainWindow) {
        this.mainWindow = mainWindow;

        //开启通讯服务
        this.start_websocket();

        this.mainWindow.loadURL(view_index);

        this.mainWindow.webContents.on("did-finish-load", function () {
            let thisurl = control.mainWindow.webContents.getURL();
            if (thisurl.substr(-19, 19) == "/desktop/black.html") return;
            control.load_plugin_html("html");
            control.load_plugin_html("css");
            control.load_plugin_html("js");
            control.inset_to_python();
        });

        this.mainWindow.on("resize", function () {
            let thisurl = control.mainWindow.webContents.getURL();
            if (thisurl.substr(-19, 19) == "/desktop/black.html") return;
            control.mainWindow.loadURL(view_index);
        });
    },
};

module.exports = control;
