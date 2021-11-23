
from api.BDaip import AipSpeech

def BDSpeechSynthesis(text, fileName):
    APP_ID = '15449758'
    API_KEY = 'tOpUbG9aNsiVrCYSSug605Tn'
    SECRET_KEY = 'zVRAwxFWUzzHEfXruUB20wIyhGrzj1b6'
    client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)

    # 发音人选择, 基础音库：0为度小美，1为度小宇，3为度逍遥，4为度丫丫，
    # 精品音库：5为度小娇，103为度米朵，106为度博文，110为度小童，111为度小萌，默认为度小美
    #PER = 4

    # 语速，取值0-15，默认为5中语速     SPD = 5

    # 音调，取值0-15，默认为5中语调     PIT = 5

    # 音量，取值0-9，默认为5中音量      VOL = 5

    # 下载的文件格式, 3：mp3(default) 4： pcm-16k 5： pcm-8k 6. wav
    # AUE = 6

    # self.send(MsgType.Text,'Screen','等待音频数据中...')
    auido = client.synthesis(
        text, 'zh', 1, {'vol': 5, 'per': 4, 'aue': '3'})
    print(len(auido))
    with open(fileName, 'wb') as f:
        f.write(auido)


if __name__ == "__main__":
    answers = ["开始配置网络，请打开微信小程序搜索“自美系统”进入配网。"]
    for w in answers:
        BDSpeechSynthesis(w, w + '.mp3')



