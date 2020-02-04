const choices = {
  0: 'Want to read',
  1: 'Currently reading',
  2: 'Read',
  'Want to read': 0,
  'Currently reading': 1,
  'Read': 2
}

const bookAction = document.getElementById('book-action');
function updateAction(idx) {
  bookAction.innerText = choices[idx];
  submitChoice(idx);
}

bookAction.addEventListener('click', function (e) {
  console.log('Choice was: ', choices[bookAction.innerText]);
  submitChoice(choices[bookAction.innerText]);
})

function submitChoice(choice) {
  const url = "{{url_for('add_book')}}";
  const data = { book_id: parseInt('{{book.book_id}}'), readingState: choice };

  fetch(url, {
    method: 'POST', // or 'PUT'
    body: JSON.stringify(data), // data can be `string` or {object}!
    headers: {
      'Content-Type': 'application/json'
    }
  }).then(res => res.json())
    .then(response => console.log('Success:', JSON.stringify(response)))
    .catch(error => console.error('Error:', error));
}
