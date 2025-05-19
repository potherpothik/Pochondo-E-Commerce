function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
const csrftoken = getCookie('csrftoken');



document.addEventListener('DOMContentLoaded', () => {
  document.querySelector('.qty-plus').onclick = () => {
    var effect = document.getElementById('qty');
    var qty = effect.value;
    if (!isNaN(qty)) {
      effect.value++;
    }
    var quantity = effect.value;
  }

  document.querySelector('.qty-minus').onclick = () => {
    var effect = document.getElementById('qty');
    var qty = effect.value;
    if (!isNaN(qty) && qty > 1) {
      effect.value--;
    }
  }

  document.querySelector('.widget-desc').querySelectorAll('li').forEach(function (item) {
    item.onclick = () => {
      var psize = item.innerText;
      document.querySelector('.product_size').innerText = psize;

    };
  });


  document.querySelector('#addcart').onclick = () => {
    var effect = document.getElementById('qty');
    var qty = effect.value;
    var productId = Number(document.querySelector('.product_id').innerText);
    var session = document.querySelector('.session_id').innerText;
    var size;
    size = document.querySelector('.product_size').innerText;

    if (size === '') {
      alert('Please select size first')
    } else {

      var data = { session: session, productId: productId, quantity: qty, size: size };


      var url = 'http://127.0.0.1:8000/add/cart';

      fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrftoken, //Necessary to work with request.is_ajax()          
        },

        body: JSON.stringify(data)
      })
        .then((response) => {
          if (response.status === 200) {
            var dis = document.querySelector('.cart-submit');
            dis.style.setProperty("display", "none", "important");
            document.querySelector('#addedcart').style.setProperty("display", "block", "important");

            effect = document.querySelector('.cart_quantity');
            cartItem = effect.innerText;
            effect.innerText++;

          }
          return response.json()
        })
        .then(data => {
          console.log('Success:', data);
          console.log(Object.values(data));
          console.log(data);
        });

    }
  }

})





// onclick="var effect = document.getElementById('qty'); var qty = effect.value; if( !isNaN( qty ) &amp;&amp; qty &gt; 1 ) effect.value--;return false;"


