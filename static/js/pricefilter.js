

document.addEventListener('DOMContentLoaded', ()=>{

  document.querySelectorAll("span.ui-slider-handle, div.slider-range-price").forEach(function(span) {
    span.onclick = function(){
      var range = document.querySelector(".range-price").innerHTML;
      // var price = document.querySelector('.product-price').innerHTML;
      console.log(range)
      if (range != null){
        var ar = range.split(' ');
        var newar = [];
        for(i = 0; i < ar.length; i++){
            if(ar[i].startsWith('$')){
            var item = ar[i].substring(1);
              newar.push(item);
            }
        var minValue = Number(newar[0]);
        var maxValue = Number(newar[1]); 
      }
      }

      console.log(minValue, maxValue)
      // document.querySelectorAll('.single_gallery_item').style.display="block";
      document.querySelectorAll('.single_gallery_item').forEach(function(item){
        
        var price = item.querySelector('.regular-price').innerHTML; 
        console.log(price);       
        price = Number(price.substring(1));
        console.log(price);
        var displayType = item.style.display;
        console.log(typeof(displayType))

        if ( (price >= minValue || price <= maxValue) && displayType == 'none' ){
          item.style.display= "block";
        }

        if (price <= minValue || price >= maxValue){
          item.style.display="none";
          
        }                      
          
        
      })      
    }    
  });
});