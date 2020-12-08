
//播放背景美图
function set_Plug_in_Library_play(data) {
    console.log(data)
    set_Plug_in_Library_exit();
    document.getElementById("Plug_in_Library_img").style.background="#000";
    document.getElementById("Plug_in_Library_img").style.display="block";
    document.getElementById("Plug_in_Library_img").src=data["data"]
}


//退出-通用
function set_Plug_in_Library_exit() {

    document.getElementById("Plug_in_Library_img").style.display="none";
}