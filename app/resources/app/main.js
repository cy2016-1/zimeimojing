const { app, BrowserWindow } = require('electron');

var mainWindow = null;

app.commandLine.appendSwitch('autoplay-policy', 'no-user-gesture-required');
app.disableHardwareAcceleration();

function createWindow() {
	var isenv = (process.env.PWD) ? true : false;
	var argv = process.argv;
	var options = {}
	if (argv.length > 1 && argv[1].toUpperCase() == 'DEBUG') {
		options = {
			backgroundColor: '#000000',
			webPreferences: {
				webSecurity: false,
				allowDisplayingInsecureContent: false,
				nodeIntegration: true,
				contextIsolation: false
			}
		}
	} else {
		options = {
			backgroundColor: '#000000',
			width: 1,
			height: 1,
			kiosk: true,	//全屏模式
			webPreferences: {
				devTools: false,
				webSecurity: false,
				allowDisplayingInsecureContent: false,
				nodeIntegration: true,
				contextIsolation: false
			}
		}
	}
	// 创建浏览器窗口
	mainWindow = new BrowserWindow(options);
	if (!options.kiosk && isenv) mainWindow.openDevTools();// 打开开发工具

	const control = require('./control');
	control.Init(mainWindow);
}

app.whenReady().then(() => {
	createWindow()
	app.on('activate', () => {
		if (BrowserWindow.getAllWindows().length === 0) {
			createWindow()
		}
	})
})

app.on('window-all-closed', () => {
	if (process.platform !== 'darwin') {
		app.quit()
	}
})
