//產製EXCEL報表
var btn = document.getElementById("createXLSX");
var fileName = "國際能源資料查詢結果";
var fileType = "xlsx";
btn.addEventListener("click", function () {
  var table = document.getElementById("tableToExport");
  var wb = XLSX.utils.table_to_book(table, { sheet: "Sheet" });
  return XLSX.writeFile(wb, null || fileName + "." + (fileType || "xlsx"));
});

//行列轉置功能
var flag = false;
//注：多次點擊後，內面文字會包裹多層div，尚無好的解決方法
function test() {
  if(!flag) {
    $('table').addClass('vertical').find('th, td').wrapInner('<div>');
//					$('table').addClass('vertical');//數字會變垂直，不能用
  } else {
    $('table').removeClass('vertical');
  }
  flag = !flag;
}

