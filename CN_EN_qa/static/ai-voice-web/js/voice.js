//限制输入的字数
$("#textarea-text").bind("input propertychange", function (event) {
  if ($(this).val().length < 200) {
    $(this).parent().css("border", "1px solid gray");
    $(".textarea-text-len").text($(this).val().length);
    $(".textarea-text-len").css("color", "#000000");
  } else {
    $(this).parent().css("border", "1px solid red");
    $(".textarea-text-len").text("请输入200字内");
    $(".textarea-text-len").css("color", "red");
  }
});

//随机示例
$(".ran-sample").on('click', function () {
  var str = ["春节，即农历新年，是一年之岁首，传统意义上的“年节”", "欢迎使用云润AI开放平台", "广州市云润大数据服务有限公司成立于2013年", "今年网络春晚首次启用的AI虚拟主持人，其核心技术有哪些"];
  $('#textarea-text').val(str[Math.floor(Math.random() * str.length)]);
  $('.textarea-text-len').text($('#textarea-text').val().length);
});

var speedVal = 5,
    tonesVal = 5,
    volumeVal = 5; //默认滑块在中间
$('#speedVal').on('input propertychange', function (e) {
  speedVal = e.target.value;
  // $(this).next('span').text(speedVal)
  $(this).next('span').text('X'+speedVal);
});

$('#tonesVal').on('input propertychange', function (e) {
  tonesVal = e.target.value;
  $(this).next('span').text(tonesVal);
});

$('#volumeVal').on('input propertychange', function (e) {
  volumeVal = e.target.value;
  $(this).next('span').text(volumeVal);
});

var src_counter = 0;

var getUrl = "http://192.168.9.184:27703/static/output/web_audio.mp3";//初始的url
console.log(getUrl);

//web后端传过来的地址处理加上？xxx=
function getSrc(mp3Url) {
  console.log(mp3Url);
  url = mp3Url;
  // var url = "/static/audio.mp3?xxx=" + src_counter;
  // url = url+"?xxx=" + src_counter;
  getUrl = url+"?xxx=" + src_counter;
  // getUrl = "/static/output/web_output/audio.mp3?xxx=" + src_counter;
  src_counter += 1;
  console.log(getUrl);//"加了？xxx=:"
  return getUrl;
}
//点击播放
$('#play').on('click', function () {
  // if ($("#textarea-text").text() === '播放') {
  if ($("#play-text").text() === '播放') {
    $('#playImg').attr('src', 'images/pause.png');
    $("#play-text").text('暂停');
    var formData = {
      text: $("#textarea-text").val(),
      role: $('input[name="role"]:checked').val(),
      speedVal: speedVal,
      tonesVal: tonesVal,
      volumeVal: volumeVal,
    };
    //点击播放时调后台接口
    console.log(formData);
    $.ajax({
      type: "post",
      url: "http://192.168.9.184:27703/web", //网页的后端接口
      data: formData,
      dataType: "json",
      success: function (data) {
        console.log(data);
        if (data.status === "ok") {
          console.log(data);
          var audio = document.getElementById("audio_player");
          console.log(audio);
          audio.load();
          audio.play();
          // src_counter += 1;s

          for(var i of data.data){
            console.log(i.file_url);

            // console.log(getUrl);
              getUrl = i.file_url;
              // console.log(getUrl);
              getSrc(getUrl);
              console.log(getUrl); //"新的geturl:"加上？xxx
              $("#audio_src").attr("src",getUrl); //将生成的url付给html的ip=audio_src的src属性

            }

        } else {
          console.log("失败：" + data.errorMsg);
        }
      },
      error: function () {
        console.log("error");
      }
    });
  } else {
    var audio = document.getElementById("audio_player");

    audio.pause();
    // audio.setAttribute("src", data);

    $('#playImg').attr('src', 'images/play.png');
    $("#play-text").text('播放');
  }
});

function download(href, title) {
  console.log("下载的url:"+getUrl);
  const a = document.createElement('a');
  a.setAttribute('href',getUrl); //href http://127.0.0"http://192.168.9.176:27703/static/audio.mp3"
  a.setAttribute('download', "云润TTS");  //title
  a.click();
  console.log(1111)
}
$("#down").on("click", download);


