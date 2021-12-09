var Start_Pause_Resume_Stop = {
    system: {
        text: '系统模块',
        Receiver: {
            Record: {
                text: '语音识别'
            },
            SpeechSynthesis: {
                text: '语音合成'
            },
            Screen: {
                text: '屏幕显示'
            },
            Awake: {
                text: '语音唤醒'
            }
        }
    },
    plugin: {
        text: '插件',
        Receiver: 'Ajax_plugin'
    }
};

var Message = {
    Start: Start_Pause_Resume_Stop,

    Pause: Start_Pause_Resume_Stop,

    Resume: Start_Pause_Resume_Stop,

    Stop: Start_Pause_Resume_Stop,

    Text: {
        system: {
            text: '系统模块',
            Receiver: {
                ControlCenter: {
                    text: '控制中心',
                    Data: 'textarea'
                },
                SpeechSynthesis: {
                    text: '语音合成',
                    Data: 'textarea'
                },
                Screen: {
                    text: '屏幕显示',
                    Data: 'textarea'
                }
            }
        },
        plugin: {
            text: '插件',
            Receiver: 'Ajax_plugin',
            Data: 'textarea'
        }
    },
    Awake: {
        ControlCenter: {
            text: '控制中心',
            Receiver: {
                ControlCenter: {
                    text: '控制中心'
                }
            }
        }
    },
    LoadPlugin: {
        ControlCenter: {
            text: '控制中心',
            Receiver: {
                ControlCenter: {
                    text: '控制中心',
                    Data: 'Ajax_plugin'
                }
            }
        }
    },
    Silence: {
        ControlCenter: {
            text: '控制中心',
            Receiver: {
                ControlCenter: {
                    text: '控制中心'
                }
            }
        }
    },
    QuitGeekTalk: {
        ControlCenter: {
            text: '控制中心',
            Receiver: {
                ControlCenter: {
                    text: '控制中心'
                }
            }
        }
    },
    ControlCenterQuit: {
        ControlCenter: {
            text: '控制中心',
            Receiver: {
                ControlCenter: {
                    text: '控制中心'
                }
            }
        }
    }
}