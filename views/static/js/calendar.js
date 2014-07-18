window.calendar = { version: "4.0.1" };
calendar.init = function(){
	this._obj = document.getElementById('calendar');

	this._els=[];
	this.get_elements("select");
	this.get_elements("ul");
	this.init_view();
};

calendar.get_elements = function(tag){
	//get all child elements as named hash
	var els=this._obj.getElementsByTagName(tag);//将该区域的所有元素全部添入
	for (var i=0; i < els.length; i++){
		var name=els[i].className;
		if (name) name = name.split(" ")[0];
		if (!this._els[name]) this._els[name]=[];
		this._els[name].push(els[i]);
	}
};

calendar.init_view = function(){
	var months = ['一月','二月','三月','四月','五月','六月','七月','八月','九月','十月','十一月','十二月'];
	var weeks = ['日','一','二','三','四','五','六'];
	// 初始化月份候选项
	for(var i=0;i<12;i++){
		this._els['month'][0].innerHTML += '<option value="'+i+'">'+months[i]+'</option>';
	}
	// 初始化年份候选项
	for(var i=2009;i<2014;i++){
		this._els['year'][0].innerHTML += '<option value="'+i+'">'+i+'</option>';
	}
	// 初始化星期尺度
	for(var i=0;i<7;i++){
		this._els['weeks'][0].innerHTML += '<li>'+weeks[i]+'</li>';
	}
};
// 展示mini日历
calendar.showView = function(src){
	this._src = src;
	this._date = src.value=="请选择日期"?this._currentDate():new Date(src.value);
	this._els['year'][0].value = this._date.getFullYear();
	this._els['month'][0].value = this._date.getMonth();
	this.updateView();
	// 设置mini日历的显示位置
	var x = 0;
	var y = 0;
	var target = src;
	while(target){
		x += target.offsetLeft;
        y += target.offsetTop;
        
        target = target.offsetParent;
	}
	this._obj.style.left = ""+x+"px";
	this._obj.style.top = ""+(y+26)+"px";
	// 显示mini日历
	this._obj.style.display = "block";
};
/* 更新mini日历显示时间段 */
calendar.updateView = function(){
	var body = this._els['days'][0];
	var year = this._els['year'][0].value;
	var month = this._els['month'][0].value;
	
	var date = new Date(''+year+'-'+(parseInt(month)+1)+'-1');
	var start_date = this.date.week_start(date);
	var end_date = this.date.add(date, 1, 'month');
	var today = this._currentDate();
	
	body.innerHTML = "";
	
	var d = start_date;
	while (d.valueOf() < end_date.valueOf()){
		if (d.valueOf()<date.valueOf()){
			var html = "<li></li>";
		} else if(d.valueOf()==this._date.valueOf()){
			var html = '<li><a href="#date" onclick="return false;" title="'+this.date.date_to_string(d)+'" class="day">'+d.getDate()+'</a></li>';
		} else if(d.valueOf()<today.valueOf()){
			var html = '<li><a href="#date" onclick="javascript:calendar.updateDate(this); return false;" title="'+this.date.date_to_string(d)+'">'+d.getDate()+'</a></li>';
		} else {
			var html = '<li>'+d.getDate()+'</li>';
		}
		body.innerHTML += html;
		d = calendar.date.add(d,1,"day");
	}
};
/* 更改日期 */
calendar.updateDate = function(item){
	this._src.value = item.getAttribute('title');
	this._obj.style.display = "none";
};
// 当前日期的日期部分
calendar._currentDate = function(){
	// 返回当前时间的日期部分
	var date = new Date();
	date.setHours(0);
	date.setMinutes(0);
	date.setSeconds(0);
	date.setMilliseconds(0);
	if (date.getHours() != 0)
		date.setTime(date.getTime() + 60 * 60 * 1000 * (24 - date.getHours()));
	return date;
};
calendar.date={
	get_date:function(){
		var year = calendar._year.value;
		var month = calendar._month.value;
		return new Date(''+year+'-'+month+'1')
	},
	week_start:function(date){
		var shift=(date.getDay()+6)%7;
		return this.add(date,-1*shift,"day");
	},
	month_start:function(date){
		date.setDate(1);
		return this.date_part(date);
	},
	add:function(date,inc,mode){
		var ndate=new Date(date);
		switch(mode){
			case "week":
				inc *= 7;
			case "day":
				ndate.setDate(ndate.getDate() + inc);
				if (!date.getHours() && ndate.getHours()) //shift to yesterday
					ndate.setTime(ndate.getTime() + 60 * 60 * 1000 * (24 - ndate.getHours()));
				break;
			case "month": ndate.setMonth(ndate.getMonth()+inc); break;
		}
		return ndate;
	},
	date_to_string:function(date){
		return ''+date.getFullYear()+'-'+date.getMonth()+'-'+date.getDay();
	}
};


/* 页面加载完即进行必要的初始化工作 */
window.onload = function() { 
	calendar.init();
}; 