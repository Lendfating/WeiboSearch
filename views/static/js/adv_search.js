searcher = {}
searcher.adv_setting=function(){
	document.getElementById('bg_shade').style.display="block";
	document.getElementById('adv_search').style.display="block";
	var query = document.getElementsByName('query');
	query[1].value = query[0].value;
}
searcher.search=function(){
	var query = document.getElementsByName('query');
	var start_time = document.getElementsByName('start_time');
	var end_time = document.getElementsByName('end_time');
	var url = "/search?query="+query[1].value+"&start_time="+start_time[0].value+"&end_time="+end_time[0].value;
	window.location.href = url;
}
searcher.close=function(){
	document.getElementById('bg_shade').style.display="none";
	document.getElementById('adv_search').style.display="none";
	document.getElementById('calendar').style.display="none";
}