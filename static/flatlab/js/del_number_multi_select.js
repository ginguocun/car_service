function getQueryString(name) {
  var reg = new RegExp('(^|&)' + name + '=([^&]*)(&|$)', 'i');
  var r = window.location.search.substr(1).match(reg);
  if (r != null) {
    return unescape(r[2]);
  }
  return null;
}

var del_id_list = getQueryString('d');

if (del_id_list) {
    del_ids = del_id_list.split(',')
    for (i = 0; i < del_ids.length; i++) {
        $('#hitgen_dels').find("option[value = '"+del_ids[i]+"']").attr("selected","selected");
    }
}

function get_d_list(){
    var d_list = [];
    var opt = $('#hitgen_dels option:selected');
    opt.each(function(item){d_list.push(opt[item].value)})
    console.log(d_list)
    var d_value = d_list.join(',')
    console.log(d_value);
    $('#d').val(d_value);
}

document.addEventListener('DOMContentLoaded', function(){
    $('#hitgen_dels').on('change', get_d_list);
});