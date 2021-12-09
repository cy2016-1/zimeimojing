const {app,BrowserWindow} = require('electron');
const control = require('./control');

var mainWindow = null;

app.on('window-all-closed', function() {
	if (process.platform != 'darwin') {
		app.quit();
	}
});

app.commandLine.appendSwitch('autoplay-policy', 'no-user-gesture-required');
app.disableHardwareAcceleration();

app.on('ready', function() {
	//隐藏菜单栏
	//electron.Menu.setApplicationMenu(null);

	var shared = {argv: process.argv}
	var options = {}
	if (shared.argv.length > 1){
		options = {
			backgroundColor: '#000000',
			webPreferences: {
				webSecurity: false,
				allowDisplayingInsecureContent:false,
				nodeIntegration: true
			}
		}
	}else{
		options = {
			backgroundColor: '#000000',
			width: 1,
			height: 1,
			kiosk: true,	//全屏模式
			webPreferences: {
				devTools: false,
				webSecurity: false,
				allowDisplayingInsecureContent:false,
				nodeIntegration: true
			}
		}
	}

	// 创建浏览器窗口。
	mainWindow = new BrowserWindow(options);
	mainWindow.openDevTools();// 打开开发工具

	// 加载应用
	control.Init(mainWindow);

	// 当mainWindow被关闭，这个事件会被发出
	mainWindow.on('closed', function() {mainWindow = null;});
});
