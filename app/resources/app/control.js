const process = require('child_process');
const request = require("request");
const ws = require("nodejs-websocket");
pythonapi = require('./pythonapi');
var set_wifi  = require('./set_wifi');
var my_mqtt   = require('./my_mqtt');

var control = {
	mainWindow: '',		// webview 窗件
	is_start: false,	// 首次连接服务器是否成功
	is_net_ok: false,	// 网络是否连通
	net_timer: 0,		// 网络探测定时器

	start_websocket: function(){
		console.log("开始建立连接...")

		var server = ws.createServer(function(conn){
		    conn.on("text", function (str) {
		        //console.log(str)
		        //var json = {'m':str}
		        control.mainWindow.webContents.send('public',JSON.parse(str) );
		    })
		    conn.on("close", function (code, reason) {
		        console.log("关闭连接")
		    });
		    conn.on("error", function (code, reason) {
		        console.log("异常关闭")
		    });
		}).listen(8103)

		console.log("WebSocket建立完毕")
	},

	//检测网络
	tect_net: function(){
		var url = config.httpapi + '/raspberry/index.html';		// 测试网络是否通
		var status = {'netstatus':0};
		try{
			var this_url = control.mainWindow.getURL();
			var re = /\/html\/index\.html/;
			request({url: url, timeout: 1500}, function(error, response, body) {
			    if (!error && response.statusCode == 200){
				    status.netstatus = 1
				    control.is_net_ok = true;
				    if ( !re.test(this_url) ){
					    control.mainWindow.loadURL("file:///"+__dirname+"/html/index.html");
				    }
				    //发送网络状态到前端
			    	control.mainWindow.webContents.send('public',status);
			    }else{
				    status.netstatus = 0
				    control.is_net_ok = false;
				    //检测是否为新设备
				    var isnew = pythonapi.run('isnewdev');
				    if (isnew !=''){
					    var json = JSON.parse(isnew.toString());
						if (json.code=='0000'){
					    	//if (json.data==1){
						    	//新设备
						    	clearInterval(control.net_timer);
						    	set_wifi.init(control.mainWindow);		//开始配网
					    	//}
					    }
			    	}
			    }
			});
		}catch(err){
			control.mainWindow.webContents.send('public',status);
		}

		//进行设备上线连接服务器
		if (control.is_net_ok && !control.is_start){
			console.log('设备上线');
			//执行python接口实现设备上线
			var childSync = pythonapi.run('online');
			if ( childSync != ''){
				var json = JSON.parse(childSync.toString());
				if (json.code=='0000'){
					control.is_start = true;
					//开启MQTT
					my_mqtt.init(control.mainWindow, function( py_config ){
						//获取用户列表
						/*
						var userlist = pythonapi.run('getuserlist');
						if ( userlist != '' ){
							var json = JSON.parse(userlist.toString());
							if ( json.length <=0 ){
								clientid = py_config.clientid;
								nav_json = {"event":"open","size":{"width":380,"height":380},"url":"bind_user.html?qr="+ clientid }
								json_str = JSON.stringify(nav_json);
								my_mqtt.navigat( json_str )
							}
						}
						*/
					});
				}
			}
		}
	},

	Init: function(mainWindow){
		this.mainWindow = mainWindow;
		console.log('这里开始');
		this.tect_net();
		this.start_websocket();
		this.net_timer = setInterval(function(){control.tect_net()},10000);
	}
}

module.exports = control;