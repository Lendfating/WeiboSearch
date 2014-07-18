var suggest_list = null;
function autoComplete(input){
	if(suggest_list == null){
		suggest_list = document.getElementById('suggest_list');
	}
	var query = input.value;
	if(query.length>0){
		var url = "/aj/autoComlpete?query="+query;
		$.get(url, function(data){
			if (data.state=="ok"&&data.data.length>0){
				// 当返回正确的结果时，调用对应的回调函数进行对应的操作
				var html = "<ul>";
				for(var i=0;i<data.data.length;i++){
					html += "<li><a href=\"/search?query="+data.data[i]+"\">"+data.data[i]+"</a></li>";
				}
				html += "</ul>";
				suggest_list.innerHTML = html;
				suggest_list.style.left = input.style.left;
				// 设置mini日历的显示位置
				var x = 0;
				var y = 0;
				var target = input;
				while(target){
					x += target.offsetLeft;
			        y += target.offsetTop;
			        
			        target = target.offsetParent;
				}
				suggest_list.style.left = ""+(x-1)+"px";
				suggest_list.style.top = ""+(y+37)+"px";
				suggest_list.style.display = "block";
				document.body.onclick = function(){
					suggest_list.style.display = "none";
					document.body.onclick = null;
				}
			} else {
				suggest_list.style.display = "none";
			}
		});
	}
	
}