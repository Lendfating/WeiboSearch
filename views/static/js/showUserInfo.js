var g_obj = null;
var g_nickname = null;
var info_box = null;
function showUserInfo(obj, nickname){
	g_obj = obj;
	g_nickname = nickname;
	if (info_box==null){
		info_box = document.getElementById('info_box');
	}
	var url = "/aj/user?nickname="+nickname;
	$.get(url, function(data){
		if (data.state=="ok"){
			// 当返回正确的结果时，调用对应的回调函数进行对应的操作
			var nickname = data.data['_id'];
			var url = data.data['url'];
			var v = data.data['v'];
			var sex = data.data['sex'];
			var count = data.data['count'];
			var card = data.data['content'];
			var html = '<dl class="info"><dt class="info_pic"><a href="http://weibo.com/n/'+nickname+'" target="_blank">';
			html += '<img src="'+url+'" width="50" height="50"></img></a></dt><dd class="info_detail"><p class="name">';
			html += '<a href="http://weibo.com/n/'+nickname+'">'+nickname+'</a> '+v+sex+'</p>';
			html += '<p class="number">'+count+'</p></dd><dd class="clear"></dd></dl><dl class="card"><dt><p>'+card+'</p></dt></dl>';
			
			info_box.innerHTML = html;
			// 设置mini日历的显示位置
			var x = 0;
			var y = 0;
			var target = obj;
			while(target){
				x += target.offsetLeft;
		        y += target.offsetTop;
		        
		        target = target.offsetParent;
			}
			info_box.style.left = ""+(x-1)+"px";
			info_box.style.top = ""+(y+50)+"px";
			info_box.style.display = "block";
			document.body.onclick = function(){
				info_box.style.display = "none";
				document.body.onclick = null;
				g_obj.onmousemove = showUserInfo(g_obj, g_nickname);
				g_obj.onmouseout = null;
			}
		} else {
			info_box.style.display = "none";
		}
	});
	obj.onmousemove = null;
	obj.onmouseout = function(){
		g_obj.onmousemove = showUserInfo(g_obj, g_nickname);
		g_obj.onmouseout = null;
		info_box.style.display = "none";
	}
}