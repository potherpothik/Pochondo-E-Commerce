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
    document.querySelector('#id_main_category').addEventListener('change', function () {
        let main_id = document.querySelector('#id_main_category').value;
        if (main_id != null) {
            select_sub(main_id);
        }
        else {
            console.log(main_id);
        }
    })
});

function select_sub(main_id) {
    url = 'http://127.0.0.1:8000/select_sub';
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({ 'main_id': main_id })
    })
        .then((response) => {
            return response.json()
        })
        .then((data) => {
            console.log('data', data);
            const sub = document.querySelector('#id_sub_category');
            sub.options.length = 0;
            for (var k in data) {
                sub.options.add(new Option(k, data[k]))
            }
        })
}